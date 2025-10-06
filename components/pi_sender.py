#!/usr/bin/env python3
"""
NSAT Pi streaming server with UDP discovery (wired + wireless).
- TCP 0.0.0.0:5050 serves JSONL samples after handshake 'SUBSCRIBE\n'.
- UDP 0.0.0.0:5051 answers 'NSAT_DISCOVER' with JSON {service,port,host}.
"""
import json, socket, threading, time
from data_generator import generator

TCP_HOST, TCP_PORT = "0.0.0.0", 5050
UDP_HOST, UDP_PORT = "0.0.0.0", 5051
HANDSHAKE = b"SUBSCRIBE\n"
TARGET_HZ = 200.0

def tcp_client_thread(conn, addr):
    conn.settimeout(2.0)
    try:
        try:
            data = conn.recv(64)
        except socket.timeout:
            data = b""
        if HANDSHAKE not in (data or b"").upper():
            return
        gen = generator(TARGET_HZ)
        interval = 1.0 / TARGET_HZ if TARGET_HZ > 0 else 0.0
        for sample in gen:
            line = (json.dumps(sample) + "\n").encode("utf-8")
            try:
                conn.sendall(line)
            except Exception:
                break
            if interval > 0:
                time.sleep(interval)
    finally:
        try: conn.close()
        except: pass

def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((TCP_HOST, TCP_PORT))
        s.listen(5)
        print(f"[TCP] Listening on {TCP_HOST}:{TCP_PORT}")
        while True:
            conn, addr = s.accept()
            print("[TCP] Client connected:", addr)
            threading.Thread(target=tcp_client_thread, args=(conn, addr), daemon=True).start()

def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((UDP_HOST, UDP_PORT))
        print(f"[UDP] Discovery listening on {UDP_HOST}:{UDP_PORT}")
        while True:
            try:
                data, raddr = s.recvfrom(512)
            except OSError:
                continue
            if (data or b"").decode("utf-8", "ignore").strip() != "NSAT_DISCOVER":
                continue
            # reply with this server's IP (as seen by peer)
            reply_ip = raddr[0]
            payload = json.dumps({"service":"nsat","port":TCP_PORT,"host":reply_ip}).encode("utf-8")
            try: s.sendto(payload, raddr)
            except OSError: pass

if __name__ == "__main__":
    threading.Thread(target=udp_server, daemon=True).start()
    tcp_server()
