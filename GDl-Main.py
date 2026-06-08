import ctypes
from ctypes import wintypes
import random
import time

# Windows constants
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020

# Load user32 and gdi32
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def main():
    # Get screen dimensions
    w = user32.GetSystemMetrics(SM_CXSCREEN)
    h = user32.GetSystemMetrics(SM_CYSCREEN)
    
    random.seed(time.time())
    
    # Get desktop window DC
    hdc = user32.GetDC(0)
    
    try:
        while True:
            y = random.randint(0, h - 1)
            direction = random.randint(0, 1)
            
            if direction == 0:  # Left-to-right
                gdi32.BitBlt(hdc, 1, y, w, 1000, hdc, 0, y, SRCCOPY)
            else:  # Right-to-left
                gdi32.BitBlt(hdc, 0, y, w, 1000, hdc, 1, y, SRCCOPY)
            
            time.sleep(0)  # Yield control
    finally:
        user32.ReleaseDC(0, hdc)

if __name__ == "__main__":
    main()