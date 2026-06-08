import ctypes
from ctypes import wintypes
import random
import math
import time
import sys

# Windows constants
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020
MB_YESNO = 0x00000004
MB_ICONWARNING = 0x00000030
MB_SYSTEMMODAL = 0x00001000
IDYES = 6
VK_ESCAPE = 0x1B

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

def random_color():
    """Generate random bright color"""
    colors = [
        0x0000FF,  # Red
        0x00FF00,  # Green  
        0xFF0000,  # Blue
        0x00FFFF,  # Yellow
        0xFF00FF,  # Cyan
        0xFFFF00,  # Magenta
        0x00AAFF,  # Orange
        0xAA00FF,  # Pink
        0xFFAA00,  # Light Blue
    ]
    return random.choice(colors)

def draw_circle(hdc, cx, cy, radius, color):
    """Draw a filled circle using GDI"""
    brush = gdi32.CreateSolidBrush(color)
    old_brush = gdi32.SelectObject(hdc, brush)
    gdi32.Ellipse(hdc, cx - radius, cy - radius, cx + radius, cy + radius)
    gdi32.SelectObject(hdc, old_brush)
    gdi32.DeleteObject(brush)

def main():
    print("=" * 60)
    print("FIREWORKS GDI - REAL DESKTOP")
    print("=" * 60)
    print("⚠️ FIREWORKS WILL APPEAR ON YOUR SCREEN! ⚠️")
    print("Press ESC to stop")
    print("=" * 60)
    
    # Warning
    result = user32.MessageBoxW(0, 
        "FIREWORKS GDI EFFECT\n\nFireworks will appear on your screen!\nPress ESC to stop.\n\nContinue?",
        "Fireworks GDI", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled")
        return
    
    w, h = get_screen_size()
    print(f"Screen: {w}x{h}")
    print("Starting fireworks in 3 seconds... Press ESC to cancel")
    time.sleep(3)
    
    hdc = user32.GetDC(0)
    if not hdc:
        print("Failed to get desktop DC!")
        return
    
    # Backup original screen
    hdc_backup = gdi32.CreateCompatibleDC(hdc)
    hbm_backup = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_backup, hbm_backup)
    gdi32.BitBlt(hdc_backup, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    fireworks = []
    frame = 0
    
    print("\n🎆 FIREWORKS STARTED! Press ESC to stop 🎆")
    
    try:
        while True:
            # Check ESC key
            if user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
                print("\nESC pressed - stopping!")
                break
            
            # Add new fireworks randomly
            if random.randint(1, 20) == 1 and len(fireworks) < 15:
                x = random.randint(50, w - 50)
                y = random.randint(50, h - 50)
                color = random_color()
                radius = random.randint(10, 40)
                fireworks.append({
                    'x': x, 'y': y, 'color': color, 
                    'radius': radius, 'life': 30,
                    'max_radius': radius
                })
            
            # Draw and update fireworks
            for fw in fireworks[:]:
                # Draw expanding circle
                progress = 1.0 - (fw['life'] / 30.0)
                current_radius = int(fw['max_radius'] * progress)
                
                if current_radius > 0:
                    # Fade color based on life
                    r = (fw['color'] >> 16) & 0xFF
                    g = (fw['color'] >> 8) & 0xFF
                    b = fw['color'] & 0xFF
                    alpha = fw['life'] / 30.0
                    
                    r = int(r * alpha)
                    g = int(g * alpha)
                    b = int(b * alpha)
                    fade_color = (b << 16) | (g << 8) | r
                    
                    # Draw circle outline
                    pen = gdi32.CreatePen(0, 2, fade_color)
                    old_pen = gdi32.SelectObject(hdc, pen)
                    brush = gdi32.GetStockObject(5)  # NULL_BRUSH
                    old_brush = gdi32.SelectObject(hdc, brush)
                    
                    gdi32.Ellipse(hdc, fw['x'] - current_radius, fw['y'] - current_radius,
                                 fw['x'] + current_radius, fw['y'] + current_radius)
                    
                    gdi32.SelectObject(hdc, old_pen)
                    gdi32.SelectObject(hdc, old_brush)
                    gdi32.DeleteObject(pen)
                    
                    # Draw sparks around the circle
                    for _ in range(8):
                        angle = random.uniform(0, 2 * math.pi)
                        r2 = current_radius + random.randint(-5, 5)
                        sx = int(fw['x'] + math.cos(angle) * r2)
                        sy = int(fw['y'] + math.sin(angle) * r2)
                        if 0 <= sx < w and 0 <= sy < h:
                            gdi32.SetPixel(hdc, sx, sy, fade_color)
                
                fw['life'] -= 1
                if fw['life'] <= 0:
                    fireworks.remove(fw)
            
            frame += 1
            time.sleep(0.05)  # 50ms delay
    
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    finally:
        # Restore original screen
        print("\nRestoring screen...")
        gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
        user32.InvalidateRect(0, None, 0)
        time.sleep(0.5)
        
        # Cleanup
        gdi32.DeleteObject(hbm_backup)
        gdi32.DeleteDC(hdc_backup)
        user32.ReleaseDC(0, hdc)
        
        print("Screen restored!")
        user32.MessageBoxW(0, "Fireworks GDI Complete!\n\nScreen restored to normal.", "Complete", 0x00000040)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")