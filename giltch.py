import ctypes
from ctypes import wintypes
import random
import time
import math
import sys

# Windows constants
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020
SRCINVERT = 0x00660046
PATINVERT = 0x5A0049
MB_YESNO = 0x00000004
MB_ICONWARNING = 0x00000030
MB_SYSTEMMODAL = 0x00001000
IDYES = 6
VK_ESCAPE = 0x1B

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

def restore_screen(hdc, hdc_backup, hbm_backup, w, h):
    gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
    user32.InvalidateRect(0, None, 0)

def glitch_effect_1(hdc, w, h, frame):
    """Random horizontal glitch strips"""
    for _ in range(30):
        y = random.randint(0, h - 30)
        height = random.randint(10, 80)
        shift = random.randint(-60, 60)
        gdi32.BitBlt(hdc, shift, y, w, height, hdc, 0, y, SRCCOPY)
    return frame + 1

def glitch_effect_2(hdc, w, h, frame):
    """Color invert glitch"""
    for _ in range(20):
        x = random.randint(0, w - 100)
        y = random.randint(0, h - 100)
        width = random.randint(50, 200)
        height = random.randint(50, 150)
        gdi32.BitBlt(hdc, x + random.randint(-20, 20), y + random.randint(-20, 20), 
                     width, height, hdc, x, y, SRCINVERT)
    return frame + 1

def glitch_effect_3(hdc, w, h, frame):
    """Pixel sorting glitch"""
    for y in range(0, h, 10):
        # Copy row to memory
        row_colors = []
        for x in range(w):
            color = gdi32.GetPixel(hdc, x, y)
            if color != -1:
                row_colors.append(color)
        
        # Sort by brightness
        if row_colors:
            row_colors.sort(key=lambda c: ((c >> 16) & 0xFF) + ((c >> 8) & 0xFF) + (c & 0xFF))
            for x, color in enumerate(row_colors):
                if x < w:
                    gdi32.SetPixel(hdc, x, y, color)
    return frame + 1

def glitch_effect_4(hdc, w, h, frame):
    """Screen shake glitch"""
    offset_x = random.randint(-20, 20)
    offset_y = random.randint(-20, 20)
    gdi32.BitBlt(hdc, offset_x, offset_y, w, h, hdc, 0, 0, SRCCOPY)
    return frame + 1

def glitch_effect_5(hdc, w, h, frame):
    """Random block movement"""
    for _ in range(15):
        src_x = random.randint(0, w - 100)
        src_y = random.randint(0, h - 100)
        dst_x = src_x + random.randint(-50, 50)
        dst_y = src_y + random.randint(-50, 50)
        bw = random.randint(50, 150)
        bh = random.randint(50, 150)
        gdi32.BitBlt(hdc, dst_x, dst_y, bw, bh, hdc, src_x, src_y, SRCCOPY)
    return frame + 1

def glitch_effect_6(hdc, w, h, frame):
    """Vertical tearing glitch"""
    for x in range(0, w, random.randint(20, 60)):
        offset = random.randint(-40, 40)
        gdi32.BitBlt(hdc, x, offset, 5, h, hdc, x, 0, SRCCOPY)
    return frame + 1

def glitch_effect_7(hdc, w, h, frame):
    """Invert patches"""
    for _ in range(25):
        x = random.randint(0, w - 80)
        y = random.randint(0, h - 80)
        bw = random.randint(40, 120)
        bh = random.randint(40, 120)
        gdi32.PatBlt(hdc, x, y, bw, bh, PATINVERT)
    return frame + 1

def glitch_effect_8(hdc, w, h, frame):
    """RGB split glitch"""
    for y in range(0, h, 4):
        shift = int(math.sin(frame / 20 + y / 50) * 30)
        # Red channel shift
        for x in range(w):
            color = gdi32.GetPixel(hdc, (x + shift) % w, y)
            if color != -1:
                r = (color >> 16) & 0xFF
                g = (color >> 8) & 0xFF
                b = color & 0xFF
                gdi32.SetPixel(hdc, x, y, (r << 16) | (g << 8) | b)
    return frame + 1

def glitch_effect_9(hdc, w, h, frame):
    """Scanline glitch"""
    for y in range(0, h, random.randint(3, 8)):
        offset = random.randint(-30, 30)
        height = random.randint(2, 6)
        gdi32.BitBlt(hdc, offset, y, w, height, hdc, 0, y, SRCCOPY)
    return frame + 1

def glitch_effect_10(hdc, w, h, frame):
    """Random noise glitch"""
    for _ in range(500):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        color = random.randint(0, 0xFFFFFF)
        gdi32.SetPixel(hdc, x, y, color)
    return frame + 1

# ============ MAIN ============

def main():
    print("=" * 60)
    print("GDI GLITCH EFFECTS - REAL DESKTOP")
    print("=" * 60)
    print("⚠️ YOUR SCREEN WILL GLITCH! ⚠️")
    print("Press ESC to stop at any time")
    print("=" * 60)
    
    # Warning
    result = user32.MessageBoxW(0, 
        "⚠️ GDI GLITCH EFFECT ⚠️\n\n"
        "Your screen will experience GLITCH effects!\n"
        "Press ESC to stop.\n\n"
        "Continue?",
        "GDI Glitch", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled")
        return
    
    w, h = get_screen_size()
    print(f"Screen: {w}x{h}")
    print("Starting glitch effects in 3 seconds... Press ESC to cancel")
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
    
    glitches = [
        ("📺 Horizontal Glitch", glitch_effect_1, 6),
        ("🎨 Color Invert Glitch", glitch_effect_2, 6),
        ("📊 Pixel Sort Glitch", glitch_effect_3, 8),
        ("📱 Screen Shake", glitch_effect_4, 5),
        ("🧩 Block Movement", glitch_effect_5, 6),
        ("📐 Vertical Tearing", glitch_effect_6, 5),
        ("🔄 Invert Patches", glitch_effect_7, 5),
        ("🌈 RGB Split Glitch", glitch_effect_8, 7),
        ("📺 Scanline Glitch", glitch_effect_9, 5),
        ("⚡ Random Noise", glitch_effect_10, 5),
    ]
    
    frame = 0
    
    print("\n" + "=" * 50)
    print("⚠️ GLITCH EFFECTS STARTING! ⚠️")
    print("Press ESC to stop")
    print("=" * 50)
    
    try:
        for i, (name, glitch, duration) in enumerate(glitches):
            print(f"[{i+1}/{len(glitches)}] {name} ({duration}s)")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Check ESC key
                if user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
                    print("\n⚠️ ESC pressed - stopping!")
                    raise KeyboardInterrupt
                
                frame = glitch(hdc, w, h, frame)
                time.sleep(0.033)  # ~30 FPS
            
            # Restore between glitches
            gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
            time.sleep(0.3)
        
        print("\n✅ All glitch effects completed!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")
    finally:
        # Restore screen
        print("\nRestoring screen...")
        restore_screen(hdc, hdc_backup, hbm_backup, w, h)
        time.sleep(0.5)
        
        # Cleanup
        gdi32.DeleteObject(hbm_backup)
        gdi32.DeleteDC(hdc_backup)
        user32.ReleaseDC(0, hdc)
        
        print("Screen restored!")
        user32.MessageBoxW(0, "Glitch effects complete!\n\nScreen restored.", "Complete", 0x00000040)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")