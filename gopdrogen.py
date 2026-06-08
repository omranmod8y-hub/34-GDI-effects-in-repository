import ctypes
from ctypes import wintypes
import math
import random
import time
import sys

# Windows constants
SRCCOPY = 0x00CC0020
PATINVERT = 0x5A0049
SRCINVERT = 0x00660046
NOTSRCCOPY = 0x00330008
SM_CXSCREEN = 0
SM_CYSCREEN = 1
MB_YESNO = 0x00000004
MB_ICONWARNING = 0x00000030
MB_SYSTEMMODAL = 0x00001000
IDYES = 6

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

def get_screen_rect():
    """Get virtual screen bounds for multi-monitor"""
    rect = RECT()
    rect.left = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
    rect.top = user32.GetSystemMetrics(77)   # SM_YVIRTUALSCREEN
    rect.right = rect.left + user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
    rect.bottom = rect.top + user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
    return rect

# ============ REAL DESKTOP EFFECTS ============

def effect_wave(hdc, w, h, frame):
    """Wave distortion - shifts rows"""
    for y in range(h):
        offset = int(math.sin(frame / 10 + y / 30) * 40)
        gdi32.BitBlt(hdc, offset, y, w, 1, hdc, 0, y, SRCCOPY)
    return frame + 1

def effect_vertical_wave(hdc, w, h, frame):
    """Vertical wave - shifts columns"""
    for x in range(w):
        offset = int(math.sin(frame / 10 + x / 30) * 40)
        gdi32.BitBlt(hdc, x, offset, 1, h, hdc, x, 0, SRCCOPY)
    return frame + 1

def effect_glitch(hdc, w, h, frame):
    """Glitch effect"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    for _ in range(40):
        y = random.randint(0, h - 30)
        height = random.randint(10, 80)
        shift = random.randint(-100, 100)
        gdi32.BitBlt(hdc, shift, y, w, height, hdc_mem, 0, y, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def effect_invert(hdc, w, h, frame):
    """Screen invert"""
    gdi32.PatBlt(hdc, 0, 0, w, h, PATINVERT)
    return frame + 1

def effect_shake(hdc, w, h, frame):
    """Screen shake"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    ox = random.randint(-12, 12)
    oy = random.randint(-12, 12)
    gdi32.BitBlt(hdc, ox, oy, w, h, hdc_mem, 0, 0, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def effect_zoom(hdc, w, h, frame):
    """Zoom effect"""
    zoom = abs(math.sin(frame / 30)) * 0.6 + 0.4
    nw = int(w * zoom)
    nh = int(h * zoom)
    x = (w - nw) // 2
    y = (h - nh) // 2
    if nw > 0 and nh > 0:
        gdi32.StretchBlt(hdc, x, y, nw, nh, hdc, 0, 0, w, h, SRCCOPY)
    return frame + 1

def effect_pixelate(hdc, w, h, frame):
    """Pixelate effect"""
    size = max(4, 6 + int(math.sin(frame / 20) * 3))
    
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    for y in range(0, h, size):
        for x in range(0, w, size):
            color = gdi32.GetPixel(hdc_mem, x, y)
            if color != -1:
                for dy in range(min(size, h - y)):
                    for dx in range(min(size, w - x)):
                        gdi32.SetPixel(hdc, x + dx, y + dy, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def effect_negative(hdc, w, h, frame):
    """Negative color"""
    gdi32.BitBlt(hdc, 0, 0, w, h, hdc, 0, 0, NOTSRCCOPY)
    return frame + 1

def effect_tunnel(hdc, w, h, frame):
    """Tunnel effect"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    cx, cy = w // 2, h // 2
    for y in range(h):
        dy = y - cy
        for x in range(w):
            dx = x - cx
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            u = int((angle + frame/20) / (2*math.pi) * w) % w
            v = int(dist * 2) % h
            color = gdi32.GetPixel(hdc_mem, u, v)
            if color != -1:
                gdi32.SetPixel(hdc, x, y, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def effect_swirl(hdc, w, h, frame):
    """Swirl effect"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    cx, cy = w // 2, h // 2
    for y in range(h):
        dy = y - cy
        for x in range(w):
            dx = x - cx
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx) + dist * 0.03 - frame/25
            u = int(cx + math.cos(angle) * dist) % w
            v = int(cy + math.sin(angle) * dist) % h
            color = gdi32.GetPixel(hdc_mem, u, v)
            if color != -1:
                gdi32.SetPixel(hdc, x, y, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def effect_scanlines(hdc, w, h, frame):
    """Scanlines effect"""
    for y in range(0, h, 4):
        brush = gdi32.CreateSolidBrush(0x000000)
        rect = RECT(0, y, w, y + 2)
        gdi32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
    return frame + 1

def effect_rainbow(hdc, w, h, frame):
    """Rainbow color overlay"""
    for y in range(0, h, 2):
        hue = (frame + y) % 360
        # Convert hue to RGB
        h_val = hue / 360.0
        s = 1.0
        l = 0.5
        # Simple HSV to RGB
        if s == 0:
            r = g = b = int(l * 255)
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h_val + 1/3) * 255
            g = hue_to_rgb(p, q, h_val) * 255
            b = hue_to_rgb(p, q, h_val - 1/3) * 255
        color = (int(r) << 16) | (int(g) << 8) | int(b)
        
        brush = gdi32.CreateSolidBrush(color)
        rect = RECT(0, y, w, y + 1)
        gdi32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
    return frame + 5

def effect_blocks(hdc, w, h, frame):
    """Random color blocks"""
    for _ in range(50):
        x = random.randint(0, w - 100)
        y = random.randint(0, h - 80)
        bw = random.randint(50, 200)
        bh = random.randint(50, 150)
        color = random.randint(0, 0xFFFFFF)
        brush = gdi32.CreateSolidBrush(color)
        rect = RECT(x, y, x + bw, y + bh)
        gdi32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
    return frame + 1

# ============ MAIN ============

def main():
    print("=" * 70)
    print("MONOXIDE - REAL DESKTOP GDI EFFECTS")
    print("=" * 70)
    print("⚠️ THIS WILL AFFECT YOUR ACTUAL SCREEN! ⚠️")
    print("Press Ctrl+C in terminal to stop")
    print("=" * 70)
    
    # First warning
    result = user32.MessageBoxW(0, 
        "⚠️ MONOXIDE REAL DESKTOP ⚠️\n\n"
        "This WILL affect your ACTUAL DESKTOP screen!\n"
        "12 GDI effects will run on your display.\n\n"
        "Press Ctrl+C in terminal to stop anytime.\n\n"
        "Continue?",
        "Monoxide - REAL DESKTOP", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled")
        return
    
    # Second warning
    result = user32.MessageBoxW(0,
        "⚠️ LAST WARNING ⚠️\n\n"
        "This is NOT a simulation!\n"
        "Your actual screen will be distorted!\n\n"
        "ARE YOU ABSOLUTELY SURE?",
        "FINAL WARNING", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled")
        return
    
    # Get screen size
    w, h = get_screen_size()
    print(f"Screen: {w}x{h}")
    print("Starting effects in 3 seconds...")
    time.sleep(3)
    
    # Get desktop DC
    hdc = user32.GetDC(0)
    if not hdc:
        print("Failed to get desktop DC!")
        return
    
    # Backup original screen
    hdc_backup = gdi32.CreateCompatibleDC(hdc)
    hbm_backup = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_backup, hbm_backup)
    gdi32.BitBlt(hdc_backup, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    effects = [
        ("🌊 Wave Distortion", effect_wave, 6),
        ("📊 Vertical Wave", effect_vertical_wave, 6),
        ("⚡ Glitch Effect", effect_glitch, 5),
        ("🔄 Screen Invert", effect_invert, 4),
        ("📱 Screen Shake", effect_shake, 5),
        ("🔍 Zoom Effect", effect_zoom, 6),
        ("📷 Pixelate", effect_pixelate, 6),
        ("🎨 Negative", effect_negative, 4),
        ("🌀 Tunnel", effect_tunnel, 6),
        ("🎠 Swirl", effect_swirl, 6),
        ("📺 Scanlines", effect_scanlines, 4),
        ("🌈 Rainbow", effect_rainbow, 6),
        ("🧱 Color Blocks", effect_blocks, 5),
    ]
    
    frame = 0
    
    print("\n" + "=" * 50)
    print("STARTING EFFECTS ON REAL DESKTOP")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        for i, (name, effect, duration) in enumerate(effects):
            print(f"[{i+1}/{len(effects)}] {name} ({duration}s)")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                frame = effect(hdc, w, h, frame)
                time.sleep(0.033)  # ~30 FPS
                
                # Check ESC
                if user32.GetAsyncKeyState(0x1B) & 0x8000:
                    print("\nESC pressed - stopping!")
                    break
            
            # Restore between effects
            gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
            time.sleep(0.2)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")
    finally:
        # Restore screen
        print("\nRestoring screen...")
        gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
        user32.InvalidateRect(0, None, 0)
        time.sleep(0.5)
        
        # Cleanup
        gdi32.DeleteObject(hbm_backup)
        gdi32.DeleteDC(hdc_backup)
        user32.ReleaseDC(0, hdc)
        
        print("Screen restored!")
        user32.MessageBoxW(0, "Monoxide Complete!\n\nScreen restored to normal.", 
                          "Complete", 0x00000040)

if __name__ == "__main__":
    main()