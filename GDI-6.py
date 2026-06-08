import ctypes
from ctypes import wintypes
import math
import time
import random

# Windows constants
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

def generate_beep_audio():
    """Generate simple beep sound using Windows Beep function"""
    # Beep at varying frequencies for a wave effect
    frequencies = [440, 880, 440, 880, 440, 880, 440]
    for freq in frequencies:
        kernel32.Beep(freq, 200)

def play_beep_async():
    """Play beep sequence in background thread"""
    import threading
    thread = threading.Thread(target=generate_beep_audio, daemon=True)
    thread.start()

def main():
    # Get screen dimensions
    x = user32.GetSystemMetrics(SM_CXSCREEN)
    y = user32.GetSystemMetrics(SM_CYSCREEN)
    angle = 0.0
    
    # Get device contexts
    hdc = user32.GetDC(0)
    mdc = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, x, y)
    gdi32.SelectObject(mdc, bmp)
    
    # Optional: play beep sound
    # play_beep_async()
    
    print("Screen wave effect running. Press ESC to exit...")
    print("Note: Audio requires a valid WAV file or uncomment beep code")
    
    try:
        while True:
            # Capture screen
            gdi32.BitBlt(mdc, 0, 0, x, y, hdc, 0, 0, SRCCOPY)
            
            # Horizontal wave
            for i in range(y):
                offset = int(math.sin(angle) * 40)
                gdi32.BitBlt(hdc, offset, i, x, 1, mdc, 0, i, SRCCOPY)
                angle += math.pi / 80
            
            time.sleep(0.01)
            
            # Capture again after horizontal wave
            gdi32.BitBlt(mdc, 0, 0, x, y, hdc, 0, 0, SRCCOPY)
            
            # Vertical wave
            for i in range(x):
                offset = int(math.sin(angle) * 40)
                gdi32.BitBlt(hdc, i, offset, 1, y, mdc, i, 0, SRCCOPY)
                angle += math.pi / 80
            
            time.sleep(0.01)
            
            # Check for escape key
            if user32.GetAsyncKeyState(0x1B) & 0x8000:
                print("ESC pressed, exiting...")
                break
                
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    # Cleanup
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mdc)
    user32.ReleaseDC(0, hdc)
    
    return 0

if __name__ == "__main__":
    main()