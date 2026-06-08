import ctypes
import math
import time
import random
import colorsys
from ctypes import wintypes

# --- Windows API Constants ---
SRCCOPY = 0x00CC0020
BI_RGB = 0

# --- Structure Definitions ---
class RGBQUAD(ctypes.Structure):
    _fields_ = [("rgb", ctypes.c_uint32)]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD)
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", RGBQUAD * 1)]

# --- Global Logic & DLLs ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
SW = user32.GetSystemMetrics(0)
SH = user32.GetSystemMetrics(1)

# Xorshift PRNG
xs = random.getrandbits(32)
def xorshift32():
    global xs
    xs ^= (xs << 13) & 0xFFFFFFFF
    xs ^= (xs >> 17) & 0xFFFFFFFF
    xs ^= (xs << 5) & 0xFFFFFFFF
    return xs

def init_dpi():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()

# --- The Shader 11 Logic ---

def execute_payload_11(duration=15):
    hdc = user32.GetDC(0)
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    
    # Create the buffer info
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = SW
    bmi.bmiHeader.biHeight = -SH # Top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB

    # Direct memory pointer for pixels
    ptr = ctypes.c_void_p()
    h_bmp = gdi32.CreateDIBSection(hdc, ctypes.byref(bmi), 0, ctypes.byref(ptr), None, 0)
    gdi32.SelectObject(hdc_mem, h_bmp)
    
    start_time = time.time()
    t = 0
    
    # Performance adjustment: Higher = smoother but more pixelated
    # 2 or 4 is recommended for Python performance
    STEP = 2 

    print(f"Payload 11 Active for {duration}s...")
    try:
        while time.time() - start_time < duration:
            # 1. Capture screen to memory
            gdi32.BitBlt(hdc_mem, 0, 0, SW, SH, hdc, 0, 0, SRCCOPY)
            
            # 2. Access the raw pixel array
            pixels = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_uint32))
            
            # 3. Apply Shader 11 logic
            # Math: u = x + y / (h/16); v = y + u / (w/16)
            for y in range(0, SH, STEP):
                for x in range(0, SW, STEP):
                    # Warping math from the C++ source
                    u = (x + y // (SH // 16)) % SW
                    v = (y + u // (SW // 16)) % SH
                    warp_idx = v * SW + u
                    orig_idx = y * SW + x
                    
                    # Get pixel color (BGR)
                    pixel_color = pixels[warp_idx]
                    b = (pixel_color >> 0) & 0xFF
                    g = (pixel_color >> 8) & 0xFF
                    r = (pixel_color >> 16) & 0xFF
                    
                    # Convert to HSL (Hue, Saturation, Lightness)
                    h_val, l_val, s_val = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
                    
                    # Saturation boost
                    if s_val < 0.5: s_val = 0.5
                    
                    # Hue shifting logic
                    if round(h_val * 10) / 10 != round(((xorshift32() + t) % 257) / 256.0 * 10) / 10:
                        h_val = (h_val + 0.1) % 1.0
                    else:
                        h_val = (h_val + 0.5) % 1.0
                    
                    # Convert back to RGB
                    nr, ng, nb = colorsys.hls_to_rgb(h_val, l_val, s_val)
                    
                    # Write back to pixel buffer
                    new_color = (int(nb*255)) | (int(ng*255) << 8) | (int(nr*255) << 16)
                    
                    # Fill the "STEP" block
                    for sy in range(STEP):
                        for sx in range(STEP):
                            if y + sy < SH and x + sx < SW:
                                pixels[(y + sy) * SW + (x + sx)] = new_color
            
            # 4. Draw buffer back to the real screen
            gdi32.BitBlt(hdc, 0, 0, SW, SH, hdc_mem, 0, 0, SRCCOPY)
            
            t += 1
            if t % 10 == 0:
                user32.InvalidateRect(0, 0, 0) # Clear screen artifacts

    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        gdi32.DeleteObject(h_bmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(0, hdc)
        user32.InvalidateRect(0, 0, 0)
        print("Payload 11 finished.")

if __name__ == "__main__":
    init_dpi()
    # Confirmation for safety
    if user32.MessageBoxW(0, "Run GDI Shader 11 (Safe Visual Only)?", "Warning", 4 | 48) == 6:
        execute_payload_11(15)