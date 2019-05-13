import struct
import random
import time

class AppleWatch3Row(object):
    def __init__(self):
        # Use the current timestamp in nanoseconds and random sensor data
        self.ts = int(time.time() * 10 ** 9)
        self.row = (self.ts,
                    random.random(),
                    random.random(),
                    random.random(),
                    random.random(),
                    random.random(),
                    random.random(),
                    random.random(),
                    random.random(),
                    random.random(),
                    random.random())
    
    def binary_encode(self):
        # Convert the watch row to binary as would occur on Apple Watch
        return struct.pack("Qdddddddddd", *self.row)
    
    def __hash__(self):
        # Unique by timestamp created (as in watch)
        return self.ts
    
    def __eq__(self, other):
        # Compare against a standard tuple
        if isinstance(other, tuple):
            return self.row == other
        
        # Compare against another watch row
        if isinstance(other, AppleWatch3Row):
            return self.ts == other.ts and self.row == other.row
        
        # If not of correct type then cannot be equal
        return False
    
    def __str__(self):
        return "AW3 Row: ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(*self.row)
