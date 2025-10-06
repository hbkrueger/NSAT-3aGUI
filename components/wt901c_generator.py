#!/usr/bin/env python3
import sys
import struct
import time
import threading
from collections import deque

import serial

PORT = "/dev/ttyUSB0"   # serial port the sensor is connected to
BAUD = 115200             # WT901C default is 9600; check config file using Wit Motion software if unsure of current configuration

# Hexidecimal value for start of message as well as message length 
# (message length is 11 hexidecimal values)
FRAME_HDR = 0x55
FRAME_LEN = 11

# Hexidecimal values for telegraphing message contents (read Wit Motion documentation)
FT_TIME  = 0x50
FT_ACC   = 0x51
FT_GYRO  = 0x52
FT_ANGLE = 0x53
FT_MAG   = 0x54
FT_QUAT  = 0x59

# Conversion scales for converting raw values into usable information (found in Wit Motion documentation)
# Double check these formulas for accuracy
ACC_SCALE_G      = 16.0 / 32768.0        # g
GYRO_SCALE_DPS   = 2000.0 / 32768.0      # deg/s
ANGLE_SCALE_DEG  = 180.0 / 32768.0       # deg
MAG_SCALE_UT = 4900.0 / 32768.0    

class WT901Parser:
    """Threaded parser for WIT 11-byte frames from a serial stream."""
    def __init__(self, ser: serial.Serial):
        self.ser = ser
        self.lock = threading.Lock()
        self.last_acc = (0.0, 0.0, 0.0)
        self.last_gyro = (0.0, 0.0, 0.0)
        self.last_angle = (0.0, 0.0, 0.0)
        self.last_mag = (0, 0, 0)
        self.last_quat = (0.0, 0.0, 0.0, 0.0)
        self.running = False
        self.errors = deque(maxlen=50)

    @staticmethod
    def _cksum11(buf: bytes) -> bool:
        """Verify 11-byte frame checksum: sum(first 10) & 0xFF == last."""
        return (sum(buf[:10]) & 0xFF) == buf[10]

    def _parse_payload(self, ftype: int, payload: bytes):
        # All 16-bit values are little-endian signed for acc/gyro/angle/mag (concept from embedded system)
        if ftype in (FT_ACC, FT_GYRO, FT_ANGLE, FT_MAG):
            x, y, z, temp = struct.unpack_from("<hhhh", payload, 0)  
            if ftype == FT_ACC:
                ax = x * ACC_SCALE_G
                ay = y * ACC_SCALE_G
                az = z * ACC_SCALE_G
                with self.lock:
                    self.last_acc = (ax, ay, az)
            elif ftype == FT_GYRO:
                gx = x * GYRO_SCALE_DPS
                gy = y * GYRO_SCALE_DPS
                gz = z * GYRO_SCALE_DPS
                with self.lock:
                    self.last_gyro = (gx, gy, gz)
            elif ftype == FT_ANGLE:
                roll  = x * ANGLE_SCALE_DEG
                pitch = y * ANGLE_SCALE_DEG
                yaw   = z * ANGLE_SCALE_DEG
                with self.lock:
                    self.last_angle = (roll, pitch, yaw)
            elif ftype == FT_MAG:
                with self.lock:
                    self.last_mag = (x, y, z)
        elif ftype == FT_QUAT:
            pass

    def _sync_and_read_frame(self) -> bytes | None:
        """Find header 0x55 then read full 11-byte frame."""
        # Sync to header
        b = self.ser.read(1)
        if not b:
            return None
        if b[0] != FRAME_HDR:
            return None
        # Read remaining 10 bytes
        rest = self.ser.read(FRAME_LEN - 1)
        if len(rest) != FRAME_LEN - 1:
            return None
        return b + rest

    def start(self):
        self.running = True
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def stop(self):
        self.running = False

    def _run(self):
        # Small buffer to scan for header quickly
        self.ser.reset_input_buffer()
        while self.running:
            try:
                frame = self._sync_and_read_frame()
                if not frame:
                    continue
                # Validate checksum
                if not self._cksum11(frame):
                    self.errors.append("checksum")
                    continue
                ftype = frame[1]
                payload = frame[2:10]
                self._parse_payload(ftype, payload)
            except Exception as e:
                self.errors.append(repr(e))
                # brief backoff on errors
                time.sleep(0.001)

def open_serial():
    return serial.Serial(
        PORT,
        BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.01,           # non-blocking-ish
    )

# generator function which passes sensor values to the caller
def generator():

    try:
        ser = open_serial()
    except serial.SerialException as e:
        print(f"Failed to open {PORT}: {e}", file=sys.stderr)
        sys.exit(1)

    parser = WT901Parser(ser)
    parser.start()

    try:
        while True:
        
            with parser.lock:
                ax, ay, az = parser.last_acc
                gx, gy, gz = parser.last_gyro
                roll, pitch, yaw = parser.last_angle
            
            yield ax, ay, az, gx, gy, gz, roll, pitch, yaw
			
    except KeyboardInterrupt:
        pass
    finally:
        parser.stop()
        ser.close()


