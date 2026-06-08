import ctypes
from ctypes import wintypes
import math
import random
import time
import sys

# Windows GDI Constants
SRCCOPY = 0x00CC0020
PATINVERT = 0x5A0049
SRCINVERT = 0x00660046
SRCPAINT = 0x00EE0086
NOTSRCCOPY = 0x00330008
SM_CXSCREEN = 0
SM_CYSCREEN = 1
MB_YESNO = 0x00000004
MB_ICONWARNING = 0x00000030
MB_TOPMOST = 0x00040000
IDYES = 6

# Load pure Windows GDI libraries
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

# ============ PURE GDI PAYLOADS ============

def payload_wave(hdc, w, h, t):
    """GDI BitBlt wave distortion"""
    angle = t / 10.0
    for y in range(h):
        offset = int(math.sin(angle + y / 30) * 40)
        gdi32.BitBlt(hdc, offset, y, w, 1, hdc, 0, y, SRCCOPY)
    return t + 1

def payload_vertical_wave(hdc, w, h, t):
    """GDI vertical wave"""
    angle = t / 10.0
    for x in range(w):
        offset = int(math.sin(angle + x / 30) * 40)
        gdi32.BitBlt(hdc, x, offset, 1, h, hdc, x, 0, SRCCOPY)
    return t + 1

def payload_glitch(hdc, w, h, t):
    """GDI glitch with memory DC"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    for _ in range(30):
        y = random.randint(0, h - 30)
        height = random.randint(10, 80)
        shift = random.randint(-100, 100)
        gdi32.BitBlt(hdc, shift, y, w, height, hdc_mem, 0, y, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def payload_invert(hdc, w, h, t):
    """GDI PatBlt invert"""
    gdi32.PatBlt(hdc, 0, 0, w, h, PATINVERT)
    return t + 1

def payload_shake(hdc, w, h, t):
    """GDI screen shake"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    ox = random.randint(-15, 15)
    oy = random.randint(-15, 15)
    gdi32.BitBlt(hdc, ox, oy, w, h, hdc_mem, 0, 0, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def payload_zoom(hdc, w, h, t):
    """GDI StretchBlt zoom"""
    zoom = abs(math.sin(t / 30)) * 0.6 + 0.4
    nw = int(w * zoom)
    nh = int(h * zoom)
    x = (w - nw) // 2
    y = (h - nh) // 2
    if nw > 0 and nh > 0:
        gdi32.StretchBlt(hdc, x, y, nw, nh, hdc, 0, 0, w, h, SRCCOPY)
    return t + 1

def payload_pixelate(hdc, w, h, t):
    """GDI pixelate with GetPixel/SetPixel"""
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

def payload_negative(hdc, w, h, t):
    """GDI negative effect"""
    gdi32.BitBlt(hdc, 0, 0, w, h, hdc, 0, 0, NOTSRCCOPY)
    return t + 1

def payload_tunnel(hdc, w, h, t):
    """GDI tunnel effect"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    cx, cy = w // 2, h // 2
    for y in range(h):
        for x in range(w):
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            ang = math.atan2(dy, dx)
            u = int((ang + t/20) / (2*math.pi) * w) % w
            v = int(dist * 3) % h
            color = gdi32.GetPixel(hdc_mem, u, v)
            if color != -1:
                gdi32.SetPixel(hdc, x, y, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def payload_swirl(hdc, w, h, t):
    """GDI swirl effect"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    cx, cy = w // 2, h // 2
    for y in range(h):
        for x in range(w):
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            ang = math.atan2(dy, dx) + dist * 0.03 - t/25
            u = int(cx + math.cos(ang) * dist) % w
            v = int(cy + math.sin(ang) * dist) % h
            color = gdi32.GetPixel(hdc_mem, u, v)
            if color != -1:
                gdi32.SetPixel(hdc, x, y, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def payload_plgblt(hdc, w, h, t):
    """GDI PlgBlt parallelogram transform"""
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    
    points = (POINT * 3)()
    points[0].x = 50 + (t % 100)
    points[0].y = -50 + (t % 50)
    points[1].x = w + 50 - (t % 100)
    points[1].y = 50 + (t % 50)
    points[2].x = -50 + (t % 50)
    points[2].y = h - 50 - (t % 50)
    
    gdi32.PlgBlt(hdc, points, hdc, -20, -20, w + 40, h + 40, None, 0, 0)
    return t + 5

def payload_scanlines(hdc, w, h, t):
    """GDI scanlines"""
    for y in range(0, h, 4):
        brush = gdi32.CreateSolidBrush(0x000000)
        rect = RECT(0, y, w, y + 2)
        gdi32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
    return t + 1

# ============ MAIN ============

def main():
    print("=" * 70)
    print("PURE GDI EFFECTS - REAL DESKTOP")
    print("=" * 70)
    print("No game engines - Just raw Windows GDI32")
    print("BitBlt, StretchBlt, PatBlt, PlgBlt, GetPixel/SetPixel")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    # Warning dialogs (pure Win32)
    result = user32.MessageBoxW(0, 
        "⚠️ PURE GDI EFFECTS ⚠️\n\n"
        "This uses raw Windows GDI32 API calls.\n"
        "No game engine - direct screen manipulation!\n\n"
        "Continue?",
        "GDI Effects", MB_YESNO | MB_ICONWARNING | MB_TOPMOST)
    
    if result != IDYES:
        return
    
    result = user32.MessageBoxW(0,
        "⚠️ LAST WARNING ⚠️\n\n"
        "Pure GDI - BitBlt, StretchBlt, PatBlt\n"
        "Your screen WILL be affected!\n\n"
        "Continue?",
        "FINAL WARNING", MB_YESNO | MB_ICONWARNING | MB_TOPMOST)
    
    if result != IDYES:
        return
    
    # Get screen size
    w, h = get_screen_size()
    print(f"Screen: {w}x{h}")
    print("Starting GDI effects in 3 seconds...")
    time.sleep(3)
    
    # Get desktop DC (pure GDI)
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
        ("🌊 BitBlt Wave", payload_wave, 6),
        ("📊 BitBlt Vertical Wave", payload_vertical_wave, 6),
        ("⚡ BitBlt Glitch", payload_glitch, 5),
        ("🔄 PatBlt Invert", payload_invert, 4),
        ("📱 BitBlt Shake", payload_shake, 5),
        ("🔍 StretchBlt Zoom", payload_zoom, 6),
        ("📷 GetPixel/SetPixel Pixelate", payload_pixelate, 6),
        ("🎨 BitBlt Negative", payload_negative, 4),
        ("🌀 BitBlt Tunnel", payload_tunnel, 6),
        ("🎠 BitBlt Swirl", payload_swirl, 6),
        ("📺 PatBlt Scanlines", payload_scanlines, 4),
        ("🔷 PlgBlt Transform", payload_plgblt, 6),
    ]
    
    frame = 0
    
    print("\n" + "=" * 50)
    print("PURE GDI OPERATIONS:")
    print("  BitBlt     - Bit block transfer")
    print("  StretchBlt - Stretched bit block")
    print("  PatBlt     - Pattern block")
    print("  PlgBlt     - Parallelogram transform")
    print("  GetPixel/SetPixel - Per-pixel ops")
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
            time.sleep(0.3)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")
    finally:
        # Restore screen
        print("\nRestoring screen...")
        gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
        user32.InvalidateRect(0, None, 0)
        time.sleep(0.5)
        
        # Cleanup GDI objects
        gdi32.DeleteObject(hbm_backup)
        gdi32.DeleteDC(hdc_backup)
        user32.ReleaseDC(0, hdc)
        
        print("Screen restored!")
        user32.MessageBoxW(0, "GDI Effects Complete!\n\nPure GDI - No game engines used!", 
                          "Complete", 0x00000040)

if __name__ == "__main__":
    main()