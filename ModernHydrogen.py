import ctypes
from ctypes import wintypes
import math
import random
import time
import threading
import sys

# --- Windows API Constants ---
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020
PATINVERT = 0x5A0049
NOTSRCCOPY = 0x00330008
NOTSRCERASE = 0x001100A6
SRCAND = 0x008800C6
SRCINVERT = 0x00660046
GM_ADVANCED = 2
CAPTUREBLT = 0x40000000

# --- Libraries ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
winmm = ctypes.windll.winmm
kernel32 = ctypes.windll.kernel32

# --- Helper Functions ---
def gen_unicode(length):
    return "".join(chr(random.randint(1024, 1280)) for _ in range(length))

# --- Simple Working GDI Payloads ---
def Payload_ColorFlash(t, hdc, sw, sh):
    """Flashing colors across screen"""
    color = ((t * 8) % 256) | (((t * 4) % 256) << 8) | (((t * 2) % 256) << 16)
    brush = gdi32.CreateSolidBrush(color)
    old_brush = gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, 0, 0, sw, sh, PATINVERT)
    gdi32.SelectObject(hdc, old_brush)
    gdi32.DeleteObject(brush)

def Payload_ScrollingBits(t, hdc, sw, sh):
    """Scrolling screen offset effect"""
    offset = (t * 8) % sw
    gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, offset, 0, SRCCOPY)

def Payload_StretchWobble(t, hdc, sw, sh):
    """Wobbly stretch effect"""
    stretch = 50 + int(math.sin(t * 0.1) * 30)
    gdi32.StretchBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, sw, stretch, SRCCOPY)

def Payload_BlockCopy(t, hdc, sw, sh):
    """Copy random blocks around"""
    for _ in range(20):
        x = random.randint(0, sw - 100)
        y = random.randint(0, sh - 100)
        w = random.randint(20, 100)
        h = random.randint(20, 100)
        dx = random.randint(-50, 50)
        dy = random.randint(-50, 50)
        gdi32.BitBlt(hdc, x + dx, y + dy, w, h, hdc, x, y, SRCCOPY)

def Payload_RandomRectangles(t, hdc, sw, sh):
    """Draw random inverted rectangles"""
    for _ in range(30):
        x = random.randint(0, sw)
        y = random.randint(0, sh)
        w = random.randint(10, 200)
        h = random.randint(10, 200)
        brush = gdi32.CreateSolidBrush(random.randint(0, 0xFFFFFF))
        old_brush = gdi32.SelectObject(hdc, brush)
        gdi32.PatBlt(hdc, x, y, w, h, PATINVERT)
        gdi32.SelectObject(hdc, old_brush)
        gdi32.DeleteObject(brush)

def Payload_LineNoise(t, hdc, sw, sh):
    """Draw random lines"""
    for _ in range(50):
        pen = gdi32.CreatePen(0, 1, random.randint(0, 0xFFFFFF))
        old_pen = gdi32.SelectObject(hdc, pen)
        gdi32.MoveToEx(hdc, random.randint(0, sw), random.randint(0, sh), None)
        gdi32.LineTo(hdc, random.randint(0, sw), random.randint(0, sh))
        gdi32.SelectObject(hdc, old_pen)
        gdi32.DeleteObject(pen)

def Payload_ScreenInvert(t, hdc, sw, sh):
    """Invert entire screen"""
    gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, NOTSRCCOPY)

def Payload_XORGlitch(t, hdc, sw, sh):
    """XOR glitch effect"""
    gdi32.BitBlt(hdc, random.randint(-30, 30), random.randint(-30, 30), 
                 sw, sh, hdc, 0, 0, SRCINVERT)

def Payload_HorizontalSlices(t, hdc, sw, sh):
    """Horizontal slice scrambling"""
    slice_h = 20
    for y in range(0, sh, slice_h):
        src_y = (y + t * 5) % sh
        gdi32.BitBlt(hdc, 0, y, sw, slice_h, hdc, 0, src_y, SRCCOPY)

def Payload_VerticalSlices(t, hdc, sw, sh):
    """Vertical slice scrambling"""
    slice_w = 20
    for x in range(0, sw, slice_w):
        src_x = (x + t * 3) % sw
        gdi32.BitBlt(hdc, x, 0, slice_w, sh, hdc, src_x, 0, SRCCOPY)

def Payload_ZoomGlitch(t, hdc, sw, sh):
    """Zoom in/out glitch"""
    zoom = 0.5 + math.sin(t * 0.1) * 0.3
    zoom_w = int(sw * zoom)
    zoom_h = int(sh * zoom)
    x_off = (sw - zoom_w) // 2
    y_off = (sh - zoom_h) // 2
    gdi32.StretchBlt(hdc, x_off, y_off, zoom_w, zoom_h, hdc, 0, 0, sw, sh, SRCCOPY)

def Payload_Pixelate(t, hdc, sw, sh):
    """Pixelate effect by stretching small blocks"""
    block = 5 + (t % 15)
    for x in range(0, sw, block):
        for y in range(0, sh, block):
            gdi32.StretchBlt(hdc, x, y, block, block, hdc, x, y, 1, 1, SRCCOPY)

def Payload_ColorCycle(t, hdc, sw, sh):
    """Cycle colors across screen with gradient"""
    for y in range(0, sh, 10):
        color = ((y + t * 10) % 256) << 16 | ((y + t * 5) % 256) << 8 | ((y + t * 20) % 256)
        pen = gdi32.CreatePen(0, 10, color)
        old_pen = gdi32.SelectObject(hdc, pen)
        gdi32.MoveToEx(hdc, 0, y, None)
        gdi32.LineTo(hdc, sw, y)
        gdi32.SelectObject(hdc, old_pen)
        gdi32.DeleteObject(pen)

def Payload_WaveDistortion(t, hdc, sw, sh):
    """Sine wave distortion"""
    for y in range(sh):
        offset = int(math.sin(y * 0.02 + t * 0.2) * 30)
        if offset != 0:
            gdi32.BitBlt(hdc, offset, y, sw - abs(offset), 1, hdc, 0, y, SRCCOPY)

def Payload_DoubleVision(t, hdc, sw, sh):
    """Double vision / ghosting effect"""
    offset = int(math.sin(t * 0.2) * 20)
    gdi32.BitBlt(hdc, offset, 0, sw, sh, hdc, 0, 0, SRCCOPY)

def Payload_FloodFill(t, hdc, sw, sh):
    """Flood fill with random colors"""
    for _ in range(10):
        x = random.randint(0, sw)
        y = random.randint(0, sh)
        color = random.randint(0, 0xFFFFFF)
        # Use ExtFloodFill if available, otherwise just draw rectangle
        brush = gdi32.CreateSolidBrush(color)
        old_brush = gdi32.SelectObject(hdc, brush)
        gdi32.PatBlt(hdc, x - 50, y - 50, 100, 100, PATINVERT)
        gdi32.SelectObject(hdc, old_brush)
        gdi32.DeleteObject(brush)

# --- Window Corruption ---
def EnumProc(hwnd, lp):
    """Corrupt individual windows"""
    try:
        user32.SetWindowTextW(hwnd, gen_unicode(15))
        hdc = user32.GetDC(hwnd)
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        if w > 0 and h > 0:
            gdi32.BitBlt(hdc, 0, 0, w, h, hdc, 
                        random.randint(-20, 20), random.randint(-20, 20), 
                        SRCCOPY | CAPTUREBLT)
        user32.ReleaseDC(hwnd, hdc)
    except:
        pass
    return True

def corruption_loop():
    """Continuously corrupt windows"""
    enum_func = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(EnumProc)
    desktop = user32.GetDesktopWindow()
    while True:
        user32.EnumChildWindows(desktop, enum_func, 0)
        time.sleep(0.3)

def msg_loop():
    """Popup message loop"""
    while True:
        try:
            threading.Thread(target=lambda: user32.MessageBoxW(
                0, gen_unicode(10), gen_unicode(10), 
                random.choice([0x2, 0x5, 0x0, 0x1]) | 0x10
            ), daemon=True).start()
        except:
            pass
        time.sleep(1.0)

# --- Main Execution ---
def main():
    # Warning prompt
    result = user32.MessageBoxW(0, 
        "This will run GDI visual effects on your screen.\nContinue?", 
        "Warning", 0x4 | 0x30)
    if result != 6:
        return
    
    user32.SetProcessDPIAware()
    sw = user32.GetSystemMetrics(SM_CXSCREEN)
    sh = user32.GetSystemMetrics(SM_CYSCREEN)
    
    print(f"[*] Screen: {sw}x{sh}")
    print("[*] Starting GDI payloads...")
    
    # List of all payloads
    payloads = [
        ("Color Flash", Payload_ColorFlash),
        ("Scrolling Bits", Payload_ScrollingBits),
        ("Stretch Wobble", Payload_StretchWobble),
        ("Block Copy", Payload_BlockCopy),
        ("Random Rectangles", Payload_RandomRectangles),
        ("Line Noise", Payload_LineNoise),
        ("Screen Invert", Payload_ScreenInvert),
        ("XOR Glitch", Payload_XORGlitch),
        ("Horizontal Slices", Payload_HorizontalSlices),
        ("Vertical Slices", Payload_VerticalSlices),
        ("Zoom Glitch", Payload_ZoomGlitch),
        ("Pixelate", Payload_Pixelate),
        ("Color Cycle", Payload_ColorCycle),
        ("Wave Distortion", Payload_WaveDistortion),
        ("Double Vision", Payload_DoubleVision),
        ("Flood Fill", Payload_FloodFill),
    ]
    
    # Run each payload for 5 seconds
    for name, payload in payloads:
        print(f"  Running: {name}")
        start_time = time.time()
        t = 0
        hdc = user32.GetDC(0)
        while time.time() - start_time < 5:
            payload(t, hdc, sw, sh)
            t += 1
            time.sleep(0.016)  # ~60fps
        user32.ReleaseDC(0, hdc)
        time.sleep(0.3)
    
    # Final chaos mode
    print("[*] Chaos mode activated...")
    threading.Thread(target=corruption_loop, daemon=True).start()
    threading.Thread(target=msg_loop, daemon=True).start()
    
    # Let chaos run for 15 seconds
    time.sleep(15)
    
    # Attempt to restore
    print("[*] Attempting to restore screen...")
    user32.RedrawWindow(0, None, None, 0x85)
    print("[*] Done.")

if __name__ == "__main__":
    main()