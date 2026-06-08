import ctypes
import random
import time
import math
from ctypes import wintypes

# --- Windows API Setup ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Get Screen Dimensions
SW = user32.GetSystemMetrics(0)
SH = user32.GetSystemMetrics(1)

class RainDrop:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, SW)
        self.y = random.randint(-SH, 0)
        self.speed = random.randint(15, 30)
        self.length = random.randint(10, 25)
        # BGR Colors: Light Blue to Cyan
        self.color = random.choice([0xFFCC66, 0xFF9933, 0xFFFFFF]) 

def rain_engine():
    # DPI Awareness
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()

    hdc = user32.GetDC(0)
    
    # Create a list of 100 raindrops
    raindrops = [RainDrop() for _ in range(100)]
    
    print("Rain effect started. (No Melt)")
    print("Press Ctrl+C in this terminal to stop.")

    try:
        while True:
            # We refresh the desktop slightly to prevent trails
            # Note: This may cause some flickering of icons
            user32.InvalidateRect(0, 0, 0)
            
            for drop in raindrops:
                # Update position
                drop.y += drop.speed
                
                # Draw the raindrop
                # Create a pen for the line
                pen = gdi32.CreatePen(0, 1, drop.color)
                old_pen = gdi32.SelectObject(hdc, pen)
                
                # Draw the line
                gdi32.MoveToEx(hdc, drop.x, drop.y, None)
                gdi32.LineTo(hdc, drop.x, drop.y + drop.length)
                
                # Cleanup GDI objects
                gdi32.SelectObject(hdc, old_pen)
                gdi32.DeleteObject(pen)
                
                # If drop goes off screen, reset it to the top
                if drop.y > SH:
                    drop.reset()

            # Small delay to keep it smooth
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        user32.ReleaseDC(0, hdc)
        user32.InvalidateRect(0, 0, 0)
        print("Desktop Refreshed.")

if __name__ == "__main__":
    rain_engine()