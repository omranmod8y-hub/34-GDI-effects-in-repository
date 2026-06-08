import ctypes
import random
import time
import math
import threading
from ctypes import wintypes

# --- Windows API Setup ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
winmm = ctypes.windll.winmm
kernel32 = ctypes.windll.kernel32

# Get Screen Dimensions
SW = user32.GetSystemMetrics(0)
SH = user32.GetSystemMetrics(1)

# --- Audio Engine (Rain Static) ---
def play_rain_sound():
    # Bytebeat formula for rain/static noise
    sample_rate = 8000
    duration = 60 # 1 minute loop
    num_samples = sample_rate * duration
    buffer = (ctypes.c_ubyte * num_samples)()
    
    for t in range(num_samples):
        # Math formula to simulate white noise/rain splatter
        val = (t * ((t >> 12 | t >> 8) & 63 & t >> 4))
        buffer[t] = val & 0xFF

    # Low-level Windows audio playback
    wfx = bytes([1, 0, 1, 0, 64, 31, 0, 0, 64, 31, 0, 0, 1, 0, 8, 0, 0, 0])
    h_waveout = wintypes.HANDLE()
    winmm.waveOutOpen(ctypes.byref(h_waveout), -1, wfx, 0, 0, 0)
    
    header = ctypes.create_string_buffer(bytes(buffer))
    # We write the buffer and let it play in the background
    winmm.waveOutWrite(h_waveout, header, len(header))

# --- Rain Particle System ---
class RainDrop:
    def __init__(self, layer):
        self.layer = layer # 0 = Back (Slow), 1 = Mid, 2 = Front (Fast)
        self.reset()

    def reset(self):
        self.x = random.randint(0, SW)
        self.y = random.randint(-SH, 0)
        
        if self.layer == 0: # Background
            self.speed = random.randint(10, 15)
            self.length = random.randint(5, 10)
            self.thickness = 1
            self.color = 0x664444 # Dim Blue (BGR)
        elif self.layer == 1: # Midground
            self.speed = random.randint(18, 25)
            self.length = random.randint(15, 25)
            self.thickness = 1
            self.color = 0xAA8888 # Medium Blue
        else: # Foreground
            self.speed = random.randint(30, 45)
            self.length = random.randint(30, 50)
            self.thickness = 2
            self.color = 0xFFEEEE # Brightest/White-ish Blue

    def update(self, hdc):
        # Draw splash if hitting the bottom
        if self.y + self.speed >= SH - 40: # Roughly taskbar height
            self.draw_splash(hdc)
            self.reset()
            return

        self.y += self.speed
        
        # Draw the drop
        pen = gdi32.CreatePen(0, self.thickness, self.color)
        old_pen = gdi32.SelectObject(hdc, pen)
        gdi32.MoveToEx(hdc, self.x, int(self.y), None)
        gdi32.LineTo(hdc, self.x, int(self.y + self.length))
        gdi32.SelectObject(hdc, old_pen)
        gdi32.DeleteObject(pen)

    def draw_splash(self, hdc):
        # Draw a small "V" or ellipse to simulate a splash
        brush = gdi32.CreateSolidBrush(self.color)
        old_brush = gdi32.SelectObject(hdc, brush)
        gdi32.PatBlt(hdc, self.x - 2, SH - 40, 4, 2, 0x00F00021)
        gdi32.SelectObject(hdc, old_brush)
        gdi32.DeleteObject(brush)

def main():
    # Set DPI awareness
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()

    # Start Sound Thread
    sound_thread = threading.Thread(target=play_rain_sound, daemon=True)
    sound_thread.start()

    hdc = user32.GetDC(0)
    
    # Create layers of raindrops (200 drops total)
    raindrops = []
    for _ in range(120): raindrops.append(RainDrop(0)) # Back
    for _ in range(60):  raindrops.append(RainDrop(1)) # Mid
    for _ in range(20):  raindrops.append(RainDrop(2)) # Front

    print("FULL REAL Rain Effect Active.")
    print("Press Ctrl+C to stop and refresh desktop.")

    try:
        while True:
            # Refresh screen (needed for GDI drawing over other windows)
            user32.InvalidateRect(0, 0, 0)
            
            # Update all drops
            for drop in raindrops:
                drop.update(hdc)
            
            # Control frame rate (~60fps)
            time.sleep(0.016)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Cleanup
        user32.ReleaseDC(0, hdc)
        user32.InvalidateRect(0, 0, 0)
        print("Desktop Refreshed.")

if __name__ == "__main__":
    main()