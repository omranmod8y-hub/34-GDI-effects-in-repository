import ctypes
import math
import time
import threading
import random
from ctypes import wintypes

# --- WinAPI Setup ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

# Constants
SRCCOPY = 0x00CC0020
SRCINVERT = 0x00660046
SRCPAINT = 0x00EE0086
SRCAND = 0x008800C6
NOTSRCCOPY = 0x00330008
BI_RGB = 0
DIB_RGB_COLORS = 0

# Structs
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class RGBQUAD(ctypes.Structure):
    _fields_ = [("b", ctypes.c_ubyte), ("g", ctypes.c_ubyte), ("r", ctypes.c_ubyte), ("reserved", ctypes.c_ubyte)]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD)
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", RGBQUAD * 1)]

# --- Globals ---
xs = random.getrandbits(32)
scr_rect = RECT(0, 0, 0, 0)
n_counter = 0

# --- Math & Helpers ---

def xorshift32():
    global xs
    xs ^= (xs << 13) & 0xFFFFFFFF
    xs ^= (xs >> 17) & 0xFFFFFFFF
    xs ^= (xs << 5) & 0xFFFFFFFF
    return xs

def hsl_to_rgb(h, s, l):
    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p
    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    return int(r * 255), int(g * 255), int(b * 255)

def get_screen_bounds():
    global scr_rect
    scr_rect.left = user32.GetSystemMetrics(76)   # SM_XVIRTUALSCREEN
    scr_rect.top = user32.GetSystemMetrics(77)    # SM_YVIRTUALSCREEN
    scr_rect.right = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
    scr_rect.bottom = user32.GetSystemMetrics(79) # SM_CYVIRTUALSCREEN

# --- Shaders (The GDI Engines) ---

def gdi_shader_1(pixels, t, w, h):
    """ Melting Sinewave Effect """
    div = t / 30.0
    a = int(math.sin(div) * 5.0)
    b = int(math.cos(div) * 5.0)
    # Python Optimization: process rows to avoid millions of lookups
    # Note: Full per-pixel manipulation is very slow in Python loops.
    # To speed up, we only process every 4th pixel or use large chunks.
    for i in range(0, w * h, 2):
        pixels[i] = pixels[(i + a) % (w * h)] + (pixels[i] >> 4)

def gdi_shader_5(pixels, t, w, h):
    """ Bitwise XOR Pattern """
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            u = ~((x + t) & y) % w
            v = ~((y + t) & x) % h
            pixels[y * w + x] ^= pixels[v * w + u]

def gdi_shader_20(pixels, t, w, h):
    """ Rainbow Screen Filter """
    r, g, b = hsl_to_rgb((t % 512) / 512.0, 1.0, 0.5)
    color_mask = (r << 16) | (g << 8) | b
    for i in range(0, w * h, 4):
        pixels[i] &= color_mask

def shader_final(pixels, t, w, h):
    """ Grayscale Static Noise """
    for i in range(0, w * h, w):
        rgb = (xorshift32() % 256) * 0x010101
        for j in range(w):
            pixels[i + j] = rgb

# --- GDI Execution Engine ---

def execute_gdi_shader(shader_func, duration):
    hdc_dst = user32.GetDC(0)
    w = scr_rect.right
    h = scr_rect.bottom
    
    hdc_temp = gdi32.CreateCompatibleDC(hdc_dst)
    
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = w
    bmi.bmiHeader.biHeight = -h  # Negative for Top-Down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB

    p_bits = ctypes.c_void_p()
    h_bm_temp = gdi32.CreateDIBSection(hdc_dst, ctypes.byref(bmi), DIB_RGB_COLORS, ctypes.byref(p_bits), None, 0)
    gdi32.SelectObject(hdc_temp, h_bm_temp)

    start_time = time.time()
    t = 0
    while time.time() - start_time < duration:
        # 1. Capture current screen
        gdi32.BitBlt(hdc_temp, 0, 0, w, h, hdc_dst, 0, 0, SRCCOPY)
        
        # 2. Access Bits
        pixels = ctypes.cast(p_bits, ctypes.POINTER(ctypes.c_uint32))
        
        # 3. Apply Shader
        shader_func(pixels, t, w, h)
        
        # 4. Draw to Screen
        gdi32.BitBlt(hdc_dst, 0, 0, w, h, hdc_temp, 0, 0, SRCCOPY)
        
        t += 1
        time.sleep(0.01) # Small delay to prevent total system lock

    # Cleanup
    gdi32.DeleteObject(h_bm_temp)
    gdi32.DeleteDC(hdc_temp)
    user32.ReleaseDC(0, hdc_dst)
    user32.InvalidateRect(0, 0, 0)

# --- Background Payloads ---

def cursor_draw_payload():
    hdc = user32.GetDC(0)
    while True:
        # IDI_APPLICATION = 32512
        h_icon = user32.LoadIconW(0, 32512)
        user32.DrawIcon(hdc, xorshift32() % scr_rect.right, xorshift32() % scr_rect.bottom, h_icon)
        time.sleep(0.05)

def window_chaos_payload():
    """ Mimics GlobalWndProc by moving windows slightly """
    while True:
        hwnd = user32.GetForegroundWindow()
        if hwnd:
            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            user32.MoveWindow(hwnd, rect.left + (random.randint(-2, 2)), rect.top + (random.randint(-2, 2)), w, h, True)
        time.sleep(0.1)

# --- Main Sequence ---

def main():
    # 1. DPI Awareness (Required for virtual screen bounds)
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()

    # 2. Safety Dialogs
    if user32.MessageBoxW(0, "Warning: This script contains visual GDI effects.\nRun it?", "Monoxide.py", 4 | 48 | 0x40000) != 6:
        return

    get_screen_bounds()
    time.sleep(2)

    # 3. Start Background Payloads
    threading.Thread(target=cursor_draw_payload, daemon=True).start()
    threading.Thread(target=window_chaos_payload, daemon=True).start()

    # 4. Run Shader Sequence
    print("Running Shader 1 (Melt)...")
    execute_gdi_shader(gdi_shader_1, 15)

    print("Running Shader 5 (Bitwise)...")
    execute_gdi_shader(gdi_shader_5, 15)

    print("Running Shader 20 (Rainbow)...")
    execute_gdi_shader(gdi_shader_20, 15)

    print("Running Final Shader (Static)...")
    execute_gdi_shader(shader_final, 10)

    # Final Cleanup
    user32.InvalidateRect(0, 0, 0)
    user32.MessageBoxW(0, "End of sequence.", "Monoxide.py", 0)

if __name__ == "__main__":
    main()