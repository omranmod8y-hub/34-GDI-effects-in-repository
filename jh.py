import ctypes
from ctypes import wintypes
import math
import random
import time
import threading
import sys
import array

# --- Windows API Constants ---
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020
PATINVERT = 0x5A0049
NOTSRCCOPY = 0x00330008
NOTSRCERASE = 0x001100A6
SRCAND = 0x008800C6
SRCINVERT = 0x00660046
MERGECOPY = 0x00C000CA
MERGEPAINT = 0x00BB0226
GM_ADVANCED = 2
RDW_INVALIDATE = 0x0001
RDW_ERASE = 0x0004
RDW_ALLCHILDREN = 0x0080
CAPTUREBLT = 0x40000000

# --- Libraries ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
winmm = ctypes.windll.winmm
kernel32 = ctypes.windll.kernel32
msimg32 = ctypes.windll.msimg32

# --- Structures ---
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class XFORM(ctypes.Structure):
    _fields_ = [("eM11", ctypes.c_float), ("eM12", ctypes.c_float),
                ("eM21", ctypes.c_float), ("eM22", ctypes.c_float),
                ("eDx", ctypes.c_float), ("eDy", ctypes.c_float)]

class RGBQUAD(ctypes.Structure):
    _fields_ = [("rgbBlue", ctypes.c_ubyte), ("rgbGreen", ctypes.c_ubyte),
                ("rgbRed", ctypes.c_ubyte), ("rgbReserved", ctypes.c_ubyte)]
    @property
    def rgb(self): return (self.rgbRed << 16) | (self.rgbGreen << 8) | self.rgbBlue
    @rgb.setter
    def rgb(self, v): 
        self.rgbRed = (v >> 16) & 0xFF
        self.rgbGreen = (v >> 8) & 0xFF
        self.rgbBlue = v & 0xFF

class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [("BlendOp", ctypes.c_ubyte), ("BlendFlags", ctypes.c_ubyte),
                ("SourceConstantAlpha", ctypes.c_ubyte), ("AlphaFormat", ctypes.c_ubyte)]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", ctypes.c_ulong), ("biWidth", ctypes.c_long), ("biHeight", ctypes.c_long),
                ("biPlanes", ctypes.c_ushort), ("biBitCount", ctypes.c_ushort), ("biCompression", ctypes.c_ulong),
                ("biSizeImage", ctypes.c_ulong), ("biXPelsPerMeter", ctypes.c_long), 
                ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", ctypes.c_ulong), 
                ("biClrImportant", ctypes.c_ulong)]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", RGBQUAD * 1)]

# --- Helper Functions ---
def xorshift32():
    global xs
    xs ^= (xs << 13) & 0xFFFFFFFF
    xs ^= (xs >> 17) & 0xFFFFFFFF
    xs ^= (xs << 5) & 0xFFFFFFFF
    return xs

def rotate_dc(hdc, angle, cx, cy):
    gdi32.SetGraphicsMode(hdc, GM_ADVANCED)
    if angle != 0:
        rad = angle * math.pi / 180.0
        xf = XFORM()
        xf.eM11 = math.cos(rad)
        xf.eM12 = math.sin(rad)
        xf.eM21 = -math.sin(rad)
        xf.eM22 = math.cos(rad)
        xf.eDx = cx - math.cos(rad) * cx + math.sin(rad) * cy
        xf.eDy = cy - math.cos(rad) * cy - math.sin(rad) * cx
        gdi32.SetWorldTransform(hdc, ctypes.byref(xf))

def gen_unicode(length):
    return "".join(chr(random.randint(1024, 1280)) for _ in range(length))

# --- GDI Payload System ---
class GDIPayload:
    def __init__(self, sw, sh):
        self.sw = sw
        self.sh = sh
        self.hdc_screen = user32.GetDC(0)
        self.hdc_mem = gdi32.CreateCompatibleDC(self.hdc_screen)
        self.hbm = gdi32.CreateCompatibleBitmap(self.hdc_screen, sw, sh)
        gdi32.SelectObject(self.hdc_mem, self.hbm)
        
    def cleanup(self):
        gdi32.DeleteObject(self.hbm)
        gdi32.DeleteDC(self.hdc_mem)
        user32.ReleaseDC(0, self.hdc_screen)
    
    # Payload 1: Color Cycling + Scanlines
    def payload_cycle_scan(self, t):
        for y in range(0, self.sh, 2):
            color = ((t * 4) % 256) << 16 | ((t * 2) % 256) << 8 | (t % 256)
            pen = gdi32.CreatePen(0, 1, color)
            old_pen = gdi32.SelectObject(self.hdc_screen, pen)
            gdi32.MoveToEx(self.hdc_screen, 0, y, None)
            gdi32.LineTo(self.hdc_screen, self.sw, y)
            gdi32.SelectObject(self.hdc_screen, old_pen)
            gdi32.DeleteObject(pen)
        time.sleep(0.01)
    
    # Payload 2: Pixel Sorting Effect
    def payload_pixel_sort(self, t):
        gdi32.BitBlt(self.hdc_mem, 0, 0, self.sw, self.sh, self.hdc_screen, 0, 0, SRCCOPY)
        sort_width = 20 + (t % 100)
        for x in range(0, self.sw, sort_width):
            for y in range(0, self.sh, 2):
                gdi32.StretchBlt(self.hdc_mem, x, y, sort_width, 1, 
                                 self.hdc_mem, x, y, sort_width, 1, SRCCOPY)
        gdi32.BitBlt(self.hdc_screen, 0, 0, self.sw, self.sh, self.hdc_mem, 0, 0, SRCCOPY)
        time.sleep(0.02)
    
    # Payload 3: Wave Distortion
    def payload_wave_distort(self, t):
        offset = int(math.sin(t * 0.1) * 50)
        for y in range(0, self.sh, 2):
            wave = int(math.sin(y * 0.05 + t * 0.2) * 30)
            gdi32.BitBlt(self.hdc_screen, wave, y, self.sw - abs(wave), 1,
                        self.hdc_screen, 0, y, SRCCOPY)
        time.sleep(0.015)
    
    # Payload 4: XOR Chaos
    def payload_xor_chaos(self, t):
        brush = gdi32.CreateSolidBrush(random.randint(0, 0xFFFFFF))
        gdi32.SelectObject(self.hdc_screen, brush)
        gdi32.PatBlt(self.hdc_screen, random.randint(0, self.sw), random.randint(0, self.sh),
                    random.randint(50, 200), random.randint(50, 200), PATINVERT)
        gdi32.DeleteObject(brush)
        
        gdi32.BitBlt(self.hdc_screen, random.randint(-50, 50), random.randint(-50, 50),
                    self.sw, self.sh, self.hdc_screen, 0, 0, SRCINVERT)
        time.sleep(0.01)
    
    # Payload 5: Zooming Effect
    def payload_zoom(self, t):
        zoom = 1 + (t % 20) / 10.0
        zoom_w = int(self.sw / zoom)
        zoom_h = int(self.sh / zoom)
        x_off = (self.sw - zoom_w) // 2
        y_off = (self.sh - zoom_h) // 2
        gdi32.StretchBlt(self.hdc_screen, 0, 0, self.sw, self.sh,
                        self.hdc_screen, x_off, y_off, zoom_w, zoom_h, SRCCOPY)
        time.sleep(0.02)
    
    # Payload 6: Color Channel Shuffle
    def payload_color_shuffle(self, t):
        gdi32.BitBlt(self.hdc_mem, 0, 0, self.sw, self.sh, self.hdc_screen, 0, 0, SRCCOPY)
        
        class BITMAPINFO(ctypes.Structure):
            _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", RGBQUAD * 1)]
        
        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = self.sw
        bmi.bmiHeader.biHeight = -self.sh
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = 0
        
        pixels = (RGBQUAD * (self.sw * self.sh))()
        gdi32.GetDIBits(self.hdc_mem, self.hbm, 0, self.sh, pixels, ctypes.byref(bmi), 0)
        
        channel_map = [(t >> shift) & 3 for shift in range(0, 6, 2)]
        for i in range(len(pixels)):
            r, g, b = pixels[i].rgbRed, pixels[i].rgbGreen, pixels[i].rgbBlue
            channels = [r, g, b]
            pixels[i].rgbRed = channels[channel_map[0] % 3]
            pixels[i].rgbGreen = channels[channel_map[1] % 3]
            pixels[i].rgbBlue = channels[channel_map[2] % 3]
        
        gdi32.SetDIBits(self.hdc_mem, self.hbm, 0, self.sh, pixels, ctypes.byref(bmi), 0)
        gdi32.BitBlt(self.hdc_screen, 0, 0, self.sw, self.sh, self.hdc_mem, 0, 0, SRCCOPY)
        time.sleep(0.05)
    
    # Payload 7: Rotating Blocks
    def payload_rotating_blocks(self, t):
        block_size = 50 + (t % 100)
        for x in range(0, self.sw, block_size):
            for y in range(0, self.sh, block_size):
                angle = (x + y + t * 10) % 360
                gdi32.SetGraphicsMode(self.hdc_screen, GM_ADVANCED)
                rad = angle * math.pi / 180.0
                xf = XFORM()
                cx = x + block_size//2
                cy = y + block_size//2
                xf.eM11 = math.cos(rad)
                xf.eM12 = math.sin(rad)
                xf.eM21 = -math.sin(rad)
                xf.eM22 = math.cos(rad)
                xf.eDx = cx - math.cos(rad) * cx + math.sin(rad) * cy
                xf.eDy = cy - math.cos(rad) * cy - math.sin(rad) * cx
                gdi32.SetWorldTransform(self.hdc_screen, ctypes.byref(xf))
                
                brush = gdi32.CreateSolidBrush(random.randint(0, 0xFFFFFF))
                gdi32.SelectObject(self.hdc_screen, brush)
                gdi32.Rectangle(self.hdc_screen, x, y, x + block_size, y + block_size)
                gdi32.DeleteObject(brush)
                gdi32.ModifyWorldTransform(self.hdc_screen, None, 2)
        time.sleep(0.03)
    
    # Payload 8: Noise Injection
    def payload_noise_inject(self, t):
        noise_density = 100 + (t % 900)
        for _ in range(noise_density):
            x = random.randint(0, self.sw)
            y = random.randint(0, self.sh)
            color = random.randint(0, 0xFFFFFF)
            for i in range(3):
                gdi32.SetPixel(self.hdc_screen, x + i, y, color)
        time.sleep(0.01)
    
    # Payload 9: Ripple Effect
    def payload_ripple(self, t):
        gdi32.BitBlt(self.hdc_mem, 0, 0, self.sw, self.sh, self.hdc_screen, 0, 0, SRCCOPY)
        for y in range(self.sh):
            offset = int(math.sin(y * 0.05 + t * 0.3) * 20)
            gdi32.BitBlt(self.hdc_screen, offset, y, self.sw - abs(offset), 1,
                        self.hdc_mem, 0, y, SRCCOPY)
        time.sleep(0.02)
    
    # Payload 10: Mosaic Effect
    def payload_mosaic(self, t):
        tile_size = 10 + (t % 40)
        for x in range(0, self.sw, tile_size):
            for y in range(0, self.sh, tile_size):
                gdi32.StretchBlt(self.hdc_screen, x, y, tile_size, tile_size,
                                self.hdc_screen, x, y, 1, 1, SRCCOPY)
        time.sleep(0.02)
    
    # Payload 11: Negative Inversion Wave
    def payload_negative_wave(self, t):
        height = 20 + int(math.sin(t * 0.1) * 10)
        for y in range(0, self.sh, height):
            wave_x = int(math.sin(y * 0.03 + t * 0.2) * 50)
            gdi32.BitBlt(self.hdc_screen, wave_x, y, self.sw - wave_x, height,
                        self.hdc_screen, 0, y, NOTSRCCOPY)
        time.sleep(0.015)
    
    # Payload 12: Color Cycle Gradient
    def payload_gradient_cycle(self, t):
        for y in range(self.sh):
            color = (((y * 255 // self.sh) + t * 2) % 256)
            color_val = (color << 16) | ((color * 2) % 256 << 8) | ((color * 3) % 256)
            pen = gdi32.CreatePen(0, 1, color_val)
            old_pen = gdi32.SelectObject(self.hdc_screen, pen)
            gdi32.MoveToEx(self.hdc_screen, 0, y, None)
            gdi32.LineTo(self.hdc_screen, self.sw, y)
            gdi32.SelectObject(self.hdc_screen, old_pen)
            gdi32.DeleteObject(pen)
        time.sleep(0.01)

# --- Shader Engine (Enhanced) ---
class ShaderEngine:
    def __init__(self):
        self.sw = user32.GetSystemMetrics(0)
        self.sh = user32.GetSystemMetrics(1)
        self.hdc_screen = user32.GetDC(0)
        self.hdc_mem = gdi32.CreateCompatibleDC(self.hdc_screen)
        
        self.bmi = BITMAPINFO()
        self.bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        self.bmi.bmiHeader.biWidth = self.sw
        self.bmi.bmiHeader.biHeight = -self.sh
        self.bmi.bmiHeader.biPlanes = 1
        self.bmi.bmiHeader.biBitCount = 32
        self.bmi.bmiHeader.biCompression = 0
        
        self.pixel_ptr = ctypes.POINTER(RGBQUAD)()
        self.hbm = gdi32.CreateDIBSection(self.hdc_screen, ctypes.byref(self.bmi), 0, 
                                          ctypes.byref(self.pixel_ptr), None, 0)
        gdi32.SelectObject(self.hdc_mem, self.hbm)
    
    def cleanup(self):
        gdi32.DeleteObject(self.hbm)
        gdi32.DeleteDC(self.hdc_mem)
        user32.ReleaseDC(0, self.hdc_screen)
    
    def run_shader(self, shader_func, duration=10):
        start = time.time()
        t = 0
        while time.time() - start < duration:
            gdi32.BitBlt(self.hdc_mem, 0, 0, self.sw, self.sh, self.hdc_screen, 0, 0, SRCCOPY)
            shader_func(t, self.sw, self.sh, self.pixel_ptr)
            gdi32.BitBlt(self.hdc_screen, 0, 0, self.sw, self.sh, self.hdc_mem, 0, 0, SRCCOPY)
            t += 1
            time.sleep(0.016)
    
    # Shader 1: Psychedelic Color Shift
    def shader_psychedelic(self, t, w, h, ptr):
        shift_r = (t * 2) & 0xFF
        shift_g = (t * 3) & 0xFF
        shift_b = (t * 5) & 0xFF
        for i in range(w * h):
            ptr[i].rgbRed = (ptr[i].rgbRed + shift_r) & 0xFF
            ptr[i].rgbGreen = (ptr[i].rgbGreen + shift_g) & 0xFF
            ptr[i].rgbBlue = (ptr[i].rgbBlue + shift_b) & 0xFF
    
    # Shader 2: Solarize Effect
    def shader_solarize(self, t, w, h, ptr):
        threshold = 128 + int(math.sin(t * 0.05) * 64)
        for i in range(w * h):
            r = ptr[i].rgbRed
            g = ptr[i].rgbGreen
            b = ptr[i].rgbBlue
            ptr[i].rgbRed = 255 - r if r > threshold else r
            ptr[i].rgbGreen = 255 - g if g > threshold else g
            ptr[i].rgbBlue = 255 - b if b > threshold else b
    
    # Shader 3: Posterize
    def shader_posterize(self, t, w, h, ptr):
        levels = 4 + (t % 8)
        step = 256 // levels
        for i in range(w * h):
            ptr[i].rgbRed = (ptr[i].rgbRed // step) * step
            ptr[i].rgbGreen = (ptr[i].rgbGreen // step) * step
            ptr[i].rgbBlue = (ptr[i].rgbBlue // step) * step
    
    # Shader 4: Edge Detection (Sobel-like)
    def shader_edge_detect(self, t, w, h, ptr):
        if w * h < 1000: return
        temp = (RGBQUAD * (w * h))()
        for i in range(w * h):
            temp[i] = ptr[i]
        
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                idx = y * w + x
                gx = abs(temp[idx - 1].rgbRed - temp[idx + 1].rgbRed)
                gy = abs(temp[idx - w].rgbRed - temp[idx + w].rgbRed)
                edge = min(255, (gx + gy) * 2)
                ptr[idx].rgbRed = edge
                ptr[idx].rgbGreen = edge
                ptr[idx].rgbBlue = edge
    
    # Shader 5: Pixelate
    def shader_pixelate(self, t, w, h, ptr):
        size = 4 + (t % 12)
        for y in range(0, h, size):
            for x in range(0, w, size):
                r_sum = g_sum = b_sum = count = 0
                for dy in range(size):
                    for dx in range(size):
                        if x + dx < w and y + dy < h:
                            idx = (y + dy) * w + (x + dx)
                            r_sum += ptr[idx].rgbRed
                            g_sum += ptr[idx].rgbGreen
                            b_sum += ptr[idx].rgbBlue
                            count += 1
                if count > 0:
                    r_avg = r_sum // count
                    g_avg = g_sum // count
                    b_avg = b_sum // count
                    for dy in range(size):
                        for dx in range(size):
                            if x + dx < w and y + dy < h:
                                idx = (y + dy) * w + (x + dx)
                                ptr[idx].rgbRed = r_avg
                                ptr[idx].rgbGreen = g_avg
                                ptr[idx].rgbBlue = b_avg
    
    # Shader 6: RGB Split
    def shader_rgb_split(self, t, w, h, ptr):
        offset = int(math.sin(t * 0.2) * 10)
        if w * h < 1000: return
        temp = (RGBQUAD * (w * h))()
        for i in range(w * h):
            temp[i] = ptr[i]
        
        for y in range(h):
            for x in range(w):
                idx = y * w + x
                r_idx = y * w + min(w - 1, x + offset)
                b_idx = y * w + max(0, x - offset)
                ptr[idx].rgbRed = temp[r_idx].rgbRed if 0 <= r_idx < w * h else 0
                ptr[idx].rgbGreen = temp[idx].rgbGreen
                ptr[idx].rgbBlue = temp[b_idx].rgbBlue if 0 <= b_idx < w * h else 0
    
    # Shader 7: Wave Distortion
    def shader_wave(self, t, w, h, ptr):
        if w * h < 1000: return
        temp = (RGBQUAD * (w * h))()
        for i in range(w * h):
            temp[i] = ptr[i]
        
        for y in range(h):
            offset = int(math.sin(y * 0.02 + t * 0.1) * 15)
            for x in range(w):
                src_x = max(0, min(w - 1, x + offset))
                idx = y * w + x
                src_idx = y * w + src_x
                ptr[idx] = temp[src_idx]

# --- Corruption Threads ---
EnumProcType = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

def EnumProc(hwnd, lp):
    user32.SetWindowTextW(hwnd, gen_unicode(15))
    hdc = user32.GetDC(hwnd)
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    if w > 0 and h > 0:
        gdi32.BitBlt(hdc, 0, 0, w, h, hdc, random.randint(-20, 20), 
                    random.randint(-20, 20), SRCCOPY | CAPTUREBLT)
    user32.ReleaseDC(hwnd, hdc)
    return True

def corruption_loop():
    enum_windows = user32.EnumChildWindows
    desktop = user32.GetDesktopWindow()
    enum_callback = EnumProcType(EnumProc)
    
    while True:
        enum_windows(desktop, enum_callback, 0)
        time.sleep(0.3)

def msg_loop():
    while True:
        threading.Thread(target=lambda: user32.MessageBoxW(0, gen_unicode(10), 
                          gen_unicode(10), random.choice([0x2, 0x5]) | 0x10), daemon=True).start()
        time.sleep(1.0)

# --- Main Execution ---
def main():
    if user32.MessageBoxW(0, "Execute GDI Payload Demo?", "Warning", 0x4 | 0x30) != 6:
        return
    
    user32.SetProcessDPIAware()
    sw = user32.GetSystemMetrics(SM_CXSCREEN)
    sh = user32.GetSystemMetrics(SM_CYSCREEN)
    
    print(f"[*] Screen Resolution: {sw}x{sh}")
    print("[*] Starting GDI Payload System...")
    
    # Initialize GDI Payload System
    gdi = GDIPayload(sw, sh)
    
    # Payload Sequence (each runs for ~5 seconds)
    payloads = [
        ("Color Cycle + Scanlines", gdi.payload_cycle_scan),
        ("Pixel Sorting", gdi.payload_pixel_sort),
        ("Wave Distortion", gdi.payload_wave_distort),
        ("XOR Chaos", gdi.payload_xor_chaos),
        ("Zoom Effect", gdi.payload_zoom),
        ("Color Channel Shuffle", gdi.payload_color_shuffle),
        ("Rotating Blocks", gdi.payload_rotating_blocks),
        ("Noise Injection", gdi.payload_noise_inject),
        ("Ripple Effect", gdi.payload_ripple),
        ("Mosaic Effect", gdi.payload_mosaic),
        ("Negative Wave", gdi.payload_negative_wave),
        ("Gradient Cycle", gdi.payload_gradient_cycle)
    ]
    
    for name, payload in payloads:
        print(f"  Running: {name}")
        start = time.time()
        t = 0
        while time.time() - start < 5:
            payload(t)
            t += 1
        user32.RedrawWindow(0, None, None, RDW_INVALIDATE | RDW_ERASE | RDW_ALLCHILDREN)
        time.sleep(0.5)
    
    print("[*] Starting Shader Engine...")
    
    # Initialize Shader Engine
    shader_engine = ShaderEngine()
    
    shaders = [
        ("Psychedelic Color Shift", shader_engine.shader_psychedelic),
        ("Solarize Effect", shader_engine.shader_solarize),
        ("Posterize", shader_engine.shader_posterize),
        ("Edge Detection", shader_engine.shader_edge_detect),
        ("Pixelate", shader_engine.shader_pixelate),
        ("RGB Split", shader_engine.shader_rgb_split),
        ("Wave Distortion", shader_engine.shader_wave)
    ]
    
    for name, shader in shaders:
        print(f"  Running Shader: {name}")
        shader_engine.run_shader(shader, duration=5)
        time.sleep(0.5)
    
    shader_engine.cleanup()
    gdi.cleanup()
    
    print("[*] Final Chaos Mode...")
    threading.Thread(target=corruption_loop, daemon=True).start()
    threading.Thread(target=msg_loop, daemon=True).start()
    
    time.sleep(10)
    print("[*] Demo Complete")

if __name__ == "__main__":
    xs = int(time.time())
    main()