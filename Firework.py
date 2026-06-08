import ctypes
import random
import time
import math
import threading

# --- Windows API Setup ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Get Screen Dimensions
SW = user32.GetSystemMetrics(0)
SH = user32.GetSystemMetrics(1)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # Random explosion direction and speed
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(5, 15)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = 0.25
        self.life = 1.0  # Percentage of life remaining
        self.decay = random.uniform(0.02, 0.05)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Gravity pulls it down
        self.life -= self.decay

def create_firework(particles):
    # Pick a random spot on the screen
    origin_x = random.randint(100, SW - 100)
    origin_y = random.randint(100, SH - 100)
    
    # Pick a random bright color (BGR format for GDI)
    color = random.randint(0, 0xFFFFFF)
    
    # Create an explosion of 20-30 particles
    for _ in range(random.randint(20, 40)):
        particles.append(Particle(origin_x, origin_y, color))

def firework_engine():
    hdc = user32.GetDC(0)
    particles = []
    
    print("Firework Pop started. Press Ctrl+C in the terminal to stop.")
    
    try:
        while True:
            # Chance to spawn a new firework
            if random.random() < 0.1: 
                create_firework(particles)

            # Update and Draw Particles
            for p in particles[:]:
                p.update()
                
                if p.life > 0:
                    # Draw a small 4x4 rectangle (firework spark)
                    brush = gdi32.CreateSolidBrush(p.color)
                    old_brush = gdi32.SelectObject(hdc, brush)
                    
                    # Draw the spark
                    size = int(4 * p.life)
                    gdi32.PatBlt(hdc, int(p.x), int(p.y), size, size, 0x00F00021) # PATCOPY
                    
                    # Cleanup GDI objects to prevent memory leaks
                    gdi32.SelectObject(hdc, old_brush)
                    gdi32.DeleteObject(brush)
                else:
                    particles.remove(p)

            # Performance delay (controls explosion speed)
            time.sleep(0.01)
            
            # Occasionally refresh the screen to clear trails
            if random.random() < 0.05:
                user32.InvalidateRect(0, 0, 0)

    except KeyboardInterrupt:
        user32.InvalidateRect(0, 0, 0)
        user32.ReleaseDC(0, hdc)
        print("Fireworks stopped.")

if __name__ == "__main__":
    # DPI Awareness (Essential for multi-monitor or scaled displays)
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()
        
    firework_engine()