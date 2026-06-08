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
SRCPAINT = 0x00EE0086
NOTSRCCOPY = 0x00330008
SRCAND = 0x008800C6
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SM_CXCURSOR = 13
SM_CYCURSOR = 14
MB_YESNO = 0x00000004
MB_ICONWARNING = 0x00000030
MB_SYSTEMMODAL = 0x00001000
IDYES = 6

# Load Windows libraries
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class CURSORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("flags", ctypes.c_uint),
                ("hCursor", ctypes.c_void_p), ("ptScreenPos", POINT)]

# Global
running = True
xs = int(time.time() * 1000)
sin_vals = [math.sin(i * 2 * math.pi / 4096) for i in range(4096)]

def xorshift32():
    global xs
    xs ^= (xs << 13) & 0xFFFFFFFF
    xs ^= (xs >> 17) & 0xFFFFFFFF
    xs ^= (xs << 5) & 0xFFFFFFFF
    return xs

def fast_sine(f):
    idx = int(f / (2 * math.pi) * 4096) % 4096
    return sin_vals[idx]

def fast_cosine(f):
    return fast_sine(f + math.pi / 2)

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

# ============ RGB to HSL ============
def rgb_to_hsl(r, g, b):
    _r, _g, _b = r/255.0, g/255.0, b/255.0
    rgb_min = min(_r, _g, _b)
    rgb_max = max(_r, _g, _b)
    f_delta = rgb_max - rgb_min
    
    h, s, l = 0.0, 0.0, (rgb_max + rgb_min) / 2.0
    
    if f_delta != 0:
        s = f_delta / (2.0 - rgb_max - rgb_min) if l > 0.5 else f_delta / (rgb_max + rgb_min)
        if _r == rgb_max:
            h = ((_g - _b) / f_delta) % 6.0
        elif _g == rgb_max:
            h = ((_b - _r) / f_delta) + 2.0
        else:
            h = ((_r - _g) / f_delta) + 4.0
        h /= 6.0
    return h, s, l

def hsl_to_rgb(h, s, l):
    if s == 0:
        val = int(l * 255)
        return (val << 16) | (val << 8) | val
    
    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p
    
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    r = hue_to_rgb(p, q, h + 1/3) * 255
    g = hue_to_rgb(p, q, h) * 255
    b = hue_to_rgb(p, q, h - 1/3) * 255
    return (int(r) << 16) | (int(g) << 8) | int(b)

# ============ GDI SHADERS (Fixed for ctypes) ============

def shader_wave_shift(hdc, w, h, t):
    """Wave distortion - FIXED"""
    div = t / 30.0
    a = int(fast_sine(div) * 5)
    b = int(fast_cosine(div) * 5)
    
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    # Use BitBlt for rows instead of per-pixel (faster and no overflow)
    for y in range(h):
        u = (a) % w
        gdi32.BitBlt(hdc, 0, y, w, 1, hdc_mem, u, y, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def shader_vertical_wave(hdc, w, h, t):
    """Vertical wave distortion"""
    div = t / 30.0
    a = int(fast_sine(div) * 5)
    
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    for x in range(w):
        v = (a) % h
        gdi32.BitBlt(hdc, x, 0, 1, h, hdc_mem, x, v, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def shader_glitch(hdc, w, h, t):
    """Glitch effect - FIXED"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    for _ in range(30):
        y = xorshift32() % (h - 20)
        height_chunk = (xorshift32() % 60) + 10
        shift = (xorshift32() % 160) - 80
        gdi32.BitBlt(hdc, shift, y, w, height_chunk, hdc_mem, 0, y, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def shader_rainbow_hsl(hdc, w, h, t):
    """Rainbow HSL shift - FIXED (use PatBlt for speed)"""
    # Cycle through rainbow colors
    hue = (t % 360) / 360.0
    color = hsl_to_rgb(hue, 1.0, 0.5)
    brush = gdi32.CreateSolidBrush(color)
    gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, 0, 0, w, h, PATINVERT)
    gdi32.DeleteObject(brush)
    return t + 1

def shader_invert(hdc, w, h, t):
    """Screen invert"""
    gdi32.PatBlt(hdc, 0, 0, w, h, PATINVERT)
    return t + 1

def shader_shake(hdc, w, h, t):
    """Screen shake"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    ox = (xorshift32() % 31) - 15
    oy = (xorshift32() % 31) - 15
    gdi32.BitBlt(hdc, ox, oy, w, h, hdc_mem, 0, 0, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def shader_zoom(hdc, w, h, t):
    """Zoom effect"""
    zoom = abs(math.sin(t / 30)) * 0.7 + 0.3
    nw = int(w * zoom)
    nh = int(h * zoom)
    x = (w - nw) // 2
    y = (h - nh) // 2
    if nw > 0 and nh > 0:
        gdi32.StretchBlt(hdc, x, y, nw, nh, hdc, 0, 0, w, h, SRCCOPY)
    return t + 1

def shader_pixelate(hdc, w, h, t):
    """Pixelate effect"""
    size = max(4, 8 + int(math.sin(t / 20) * 4))
    
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
    return t + 1

def shader_negative(hdc, w, h, t):
    """Negative color"""
    gdi32.BitBlt(hdc, 0, 0, w, h, hdc, 0, 0, NOTSRCCOPY)
    return t + 1

def shader_color_patches(hdc, w, h, t):
    """Random color patches"""
    for _ in range(20):
        x = xorshift32() % (w - 100)
        y = xorshift32() % (h - 100)
        bw = (xorshift32() % 150) + 50
        bh = (xorshift32() % 150) + 50
        color = (xorshift32() % 256) * 0x010101
        brush = gdi32.CreateSolidBrush(color)
        rect = RECT(x, y, x + bw, y + bh)
        gdi32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
    return t + 1

def shader_tunnel(hdc, w, h, t):
    """Simple tunnel effect using row shifts"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    cx = w // 2
    for y in range(h):
        dy = y - cx
        dist = abs(dy)
        shift = int(math.sin(dist * 0.05 - t / 20) * 20)
        gdi32.BitBlt(hdc, shift, y, w, 1, hdc_mem, 0, y, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def shader_swirl(hdc, w, h, t):
    """Simple swirl effect"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    cx, cy = w // 2, h // 2
    for y in range(h):
        dy = y - cy
        angle = math.sin(dy * 0.05 - t / 30) * 30
        shift = int(angle)
        gdi32.BitBlt(hdc, shift, y, w, 1, hdc_mem, 0, y, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def shader_scanlines(hdc, w, h, t):
    """Scanlines effect"""
    for y in range(0, h, 4):
        brush = gdi32.CreateSolidBrush(0x000000)
        rect = RECT(0, y, w, y + 2)
        gdi32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
    return t + 1

# ============ MAIN ============

def main():
    global running
    
    print("=" * 70)
    print("MONOXIDE GDI SHADERS - REAL DESKTOP (FIXED)")
    print("=" * 70)
    print("⚠️ THIS WILL AFFECT YOUR ACTUAL SCREEN! ⚠️")
    print("Press Ctrl+C in terminal to stop")
    print("=" * 70)
    
    # First warning
    result = user32.MessageBoxW(0, 
        "⚠️ MONOXIDE GDI SHADERS ⚠️\n\n"
        "This WILL affect your ACTUAL DESKTOP screen!\n"
        "15 shaders will run on your display.\n\n"
        "Press Ctrl+C in terminal to stop anytime.\n\n"
        "Continue?",
        "Monoxide - REAL DESKTOP", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled by user")
        return
    
    # Second warning
    result = user32.MessageBoxW(0,
        "⚠️ LAST WARNING ⚠️\n\n"
        "This is NOT a simulation - your screen WILL be affected!\n\n"
        "ARE YOU ABSOLUTELY SURE?",
        "FINAL WARNING", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled at last warning")
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
    
    shaders = [
        ("Wave Shift", shader_wave_shift, 5),
        ("Vertical Wave", shader_vertical_wave, 5),
        ("Glitch", shader_glitch, 5),
        ("Rainbow", shader_rainbow_hsl, 5),
        ("Invert", shader_invert, 3),
        ("Screen Shake", shader_shake, 4),
        ("Zoom", shader_zoom, 5),
        ("Pixelate", shader_pixelate, 5),
        ("Negative", shader_negative, 3),
        ("Color Patches", shader_color_patches, 5),
        ("Tunnel", shader_tunnel, 5),
        ("Swirl", shader_swirl, 5),
        ("Scanlines", shader_scanlines, 3),
    ]
    
    t = 0
    
    print("\n" + "=" * 50)
    print("STARTING SHADERS ON REAL DESKTOP")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        for i, (name, shader, duration) in enumerate(shaders):
            print(f"[{i+1}/{len(shaders)}] {name} ({duration} seconds)")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                t = shader(hdc, w, h, t)
                time.sleep(0.033)  # ~30 FPS
                
                # Check for ESC key
                if user32.GetAsyncKeyState(0x1B) & 0x8000:
                    print("\nESC pressed - stopping!")
                    running = False
                    break
            
            # Restore backup between shaders
            gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
            time.sleep(0.2)
            
            if not running:
                break
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")
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
        user32.MessageBoxW(0, "Monoxide GDI Shaders Complete!\n\nScreen restored to normal.", 
                          "Complete", 0x00000040)

if __name__ == "__main__":
    main()