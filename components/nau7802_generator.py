# SPDX-FileCopyrightText: 2023 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
Built from nau7802_simpletest.py  2023-01-13 2.0.2  Cedar Grove Maker Studios

Instantiates one NAU7802 channel with default gain of 128 and sample rate of 320

No data filtering

"""


# nau7802 initializer function 
_nau = None
def _ensure_nau():
    global _nau
    if _nau is None:
        from cedargrove_nau7802 import NAU7802
        import board
        _nau = NAU7802(board.I2C(), address=0x2A, active_channels=1)
        _nau.enable(True)
        _nau.channel = 1
        _nau.calibrate("INTERNAL")
        _nau.calibrate("OFFSET")
        _nau.poll_rate = 320
        

# generator function which passes sensor values to the caller
def generator():
    
    # initializing load cell and nau7802 chip
    _ensure_nau()
    val = 0
    
    while True:
        
        try:
            
            # recycling old data values if for some reason a new one isn't detected
            if not _nau.available:
                yield val
            
            # converting raw data into usable information using an equation found from calibration
            else:
                raw_val = _nau.read()
                val = -0.0097 * (raw_val - (-21.475) ) - 7.1090
                yield val 
                
        # load cell throws the occassional IO error. To prevent it from shutting down the whole program we just recycle the last known value.
        except (OSError, IOError):
            yield val
    


    
    
