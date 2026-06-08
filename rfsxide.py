import ctypes
import math
import time
import random
from ctypes import wintypes

# --- Windows API Constants ---
SRCCOPY = 0x00CC0020
BI_RGB = 0
DIB_RGB_COLORS = 0

# --- Structure Definitions ---
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

# --- DLL Setup ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
SW = user32.GetSystemMetrics(0)
SH = user32.GetSystemMetrics(1)

def init_dpi():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()

# --- The Shader 12 Logic ---

def execute_payload_12(duration=15):
    hdc = user32.GetDC(0)
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = SW
    bmi.bmiHeader.biHeight = -SH # Top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB

    ptr = ctypes.c_void_p()
    h_bmp = gdi32.CreateDIBSection(hdc, ctypes.byref(bmi), DIB_RGB_COLORS, ctypes.byref(ptr), None, 0)
    gdi32.SelectObject(hdc_mem, h_bmp)
    
    start_time = time.time()
    t = 0
    
    # Optimization: Process every 2nd pixel to maintain Python speed
    STEP = 2 

    print(f"Payload 12 (Horizontal Drift) Active for {duration}s...")
    try:
        while time.time() - start_time < duration:
            # 1. Capture the screen to the DIB section
            gdi32.BitBlt(hdc_mem, 0, 0, SW, SH, hdc, 0, 0, SRCCOPY)
            
            # 2. Map the memory bits
            pixels = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_uint32))
            
            # 3. Apply displacement and color shift math
            # Math: u = x + (t + y) * 10
            # Color: B-1, G+1, R-2
            for y in range(0, SH, STEP):
                # Calculate the horizontal offset 'a' for this row
                # We use a sine variation to mimic the "Hydrogen/Monoxide" style
                offset_a = int((t + y % 10) * 5) % SW
                
                for x in range(0, SW, STEP):
                    idx = y * SW + x
                    
                    # Displace coordinate
                    u = (x + offset_a) % SW
                    target_idx = y * SW + u
                    
                    # Get pixel color (BGR format)
                    color = pixels[target_idx]
                    b = (color >> 0) & 0xFF
                    g = (color >> 8) & 0xFF
                    r = (color >> 16) & 0xFF
                    
                    # Apply Payload 12 color shift logic
                    # rgbDst.rgb = ((rgbDst.b - 1) | ((rgbDst.g + 1) << 8) | ((rgbDst.r - 2) << 16))
                    nb = (b - 1) & 0xFF
                    ng = (g + 1) & 0xFF
                    nr = (r - 2) & 0xFF
                    
                    new_color = nb | (ng << 8) | (nr << 16)
                    
                    # Draw the block (based on STEP)
                    for sy in range(STEP):
                        for sx in range(STEP):
                            if y + sy < SH and x + sx < SW:
                                pixels[(y + sy) * SW + (x + sx)] = new_color
            
            # 4. BitBlt the processed buffer back to the screen
            gdi32.BitBlt(hdc, 0, 0, SW, SH, hdc_mem, 0, 0, SRCCOPY)
            
            t += 2
            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        gdi32.DeleteObject(h_bmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(0, hdc)
        # Refresh screen to clear artifacts
        user32.InvalidateRect(0, 0, 0)
        print("Payload 12 finished.")

if __name__ == "__main__":
    init_dpi()
    # Confirmation for safety
    res = user32.MessageBoxW(0, "Run GDI Shader 12 (Safe Visual Only)?", "Warning", 4 | 48)
    if res == 6: # IDYES
        execute_payload_12(15)