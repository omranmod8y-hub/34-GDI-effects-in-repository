"""
jwzyexgnlc.exe REAL GDI Simulation
====================================
Draws directly to the Desktop Device Context (GetDC(0)).
Press the END key at ANY TIME to instantly clear the screen and exit.
"""

import ctypes
import ctypes.wintypes
import threading
import time
import random
import math
import sys
import numpy as np

try:
    import pygame
    # Initialize mixer (try mono first, fallback handled in playback)
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=1024)
    except:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
    AUDIO_ENABLED = True
except Exception as e:
    AUDIO_ENABLED = False
    print(f"Pygame audio failed: {e}. Skipping audio.")

# ─── Windows API Bindings ─────────────────────────────────────────────
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

SRCCOPY    = 0x00CC0020
NOTSRCCOPY = 0x00330008
SRCPAINT   = 0x00EE0086
PATINVERT  = 0x005A0049
MERGECOPY  = 0x00C000CA

MB_YESNO = 0x00000004
MB_ICONEXCLAMATION = 0x00000030
IDNO = 7

VK_END = 0x23 # END key for emergency exit

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
        ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32), ("biYPelsPerMeter", ctypes.c_int32),
        ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)
    ]

# ─── Screen Setup ─────────────────────────────────────────────────────
hdc = user32.GetDC(0) # Real Desktop DC
W = user32.GetSystemMetrics(0)
H = user32.GetSystemMetrics(1)
PAYLOAD_TIME = 15 # 15 seconds per payload for demo

def check_exit():
    """Emergency exit if END key is pressed"""
    if user32.GetAsyncKeyState(VK_END) & 0x8000:
        user32.InvalidateRect(0, None, 1) # Clear screen artifacts
        user32.ReleaseDC(0, hdc)
        sys.exit(0)

# ─── GDI Memory Surface Class ────────────────────────────────────────
class GDISurface:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.hdc_mem = gdi32.CreateCompatibleDC(hdc)

        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = w
        bmi.biHeight = -h # Top-down DIB
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0

        self.ppBits = ctypes.c_void_p()
        self.hBmp = gdi32.CreateDIBSection(self.hdc_mem, ctypes.byref(bmi), 0, ctypes.byref(self.ppBits), None, 0)
        gdi32.SelectObject(self.hdc_mem, self.hBmp)

        array_type = ctypes.c_uint8 * (w * h * 4)
        self.np_array = np.ctypeslib.as_array(array_type.from_address(self.ppBits.value))
        self.np_array = self.np_array.reshape((h, w, 4))

    def grab(self):
        gdi32.BitBlt(self.hdc_mem, 0, 0, self.w, self.h, hdc, 0, 0, SRCCOPY)

    def draw(self):
        gdi32.BitBlt(hdc, 0, 0, self.w, self.h, self.hdc_mem, 0, 0, SRCCOPY)

    def cleanup(self):
        gdi32.DeleteObject(self.hBmp)
        gdi32.DeleteDC(self.hdc_mem)

surface_full = GDISurface(W, H)

# ─── Color Math (HSL Conversion) ─────────────────────────────────────
def rgb2hsl_vec(pixels):
    r, g, b = pixels[:,:,2]/255.0, pixels[:,:,1]/255.0, pixels[:,:,0]/255.0
    cmax, cmin = np.maximum.reduce([r,g,b]), np.minimum.reduce([r,g,b])
    delta = cmax - cmin
    l = (cmax + cmin) / 2.0
    
    s = np.where(delta == 0, 0, np.where(l < 0.5, delta / (cmax + cmin), delta / (2.0 - cmax - cmin)))
    h = np.zeros_like(r)
    mask_r = (cmax == r)
    mask_g = (cmax == g) & ~mask_r
    mask_b = (cmax == b) & ~mask_r & ~mask_g
    
    delta_r = (((cmax - r) / 6.0) + (delta / 2.0)) / delta
    delta_g = (((cmax - g) / 6.0) + (delta / 2.0)) / delta
    delta_b = (((cmax - b) / 6.0) + (delta / 2.0)) / delta
    
    h = np.where(delta == 0, 0, np.where(mask_r, delta_b - delta_g, np.where(mask_g, (1/3)+delta_r-delta_b, (2/3)+delta_g-delta_r)))
    h = np.where(h < 0, h + 1, np.where(h > 1, h - 1, h))
    return h, s, l

def hsl2rgb_vec(h, s, l):
    v = np.where(l <= 0.5, l * (1.0 + s), l + s - l * s)
    m = l + l - v
    sv = np.where(v == 0, 0, (v - m) / v)
    h6 = h * 6.0
    sextant = h6.astype(int)
    fract = h6 - sextant
    vsf = v * sv * fract
    mid1 = m + vsf
    mid2 = v - vsf
    
    r = np.zeros_like(h); g = np.zeros_like(h); b = np.zeros_like(h)
    masks = [(sextant==0, v, mid1, m), (sextant==1, mid2, v, m), (sextant==2, m, v, mid1),
             (sextant==3, m, mid2, v), (sextant==4, mid1, m, v), (sextant==5, v, m, mid2)]
    for mask, rv, gv, bv in masks:
        r = np.where(mask, rv, r); g = np.where(mask, gv, g); b = np.where(mask, bv, b)
        
    pixels = np.zeros((h.shape[0], h.shape[1], 4), dtype=np.uint8)
    pixels[:,:,2] = (r * 255).astype(np.uint8)
    pixels[:,:,1] = (g * 255).astype(np.uint8)
    pixels[:,:,0] = (b * 255).astype(np.uint8)
    return pixels

# ─── Audio Generation ─────────────────────────────────────────────────
def play_bytebeat(sample_rate, duration, formula_func):
    if not AUDIO_ENABLED: return
    def audio_thread():
        try:
            t = np.arange(sample_rate * duration, dtype=np.int64)
            val = formula_func(t) & 0xFFFFFFFF
            val = ((val + 32768) & 0xFFFF) - 32768
            arr = val.astype(np.int16)
            # Fix for Pygame stereo mixer requirements
            if pygame.mixer.get_init()[2] == 2:
                arr = np.column_stack((arr, arr))
            snd = pygame.sndarray.make_sound(arr)
            snd.play()
            time.sleep(duration)
        except Exception as e:
            print(f"Audio error: {e}")
    threading.Thread(target=audio_thread, daemon=True).start()

def sound1_math(t): return (3 * (t >> 6 | t | t >> (t >> 16)) + (7 & t >> 11) * t) % 256
def sound2_math(t): return (3 * (t >> 6 | t | t >> (t >> 16)) + (7 & t >> 11) * t) % 256
def sound3_math(t): return (t & t >> 12) * (t >> 4 | t >> 8)
def sound4_math(t): return (t - (t >> 4 & t >> 8) & t >> 12) - 1
def sound5_math(t): return (9 * (t * ((t >> 9 | t >> 13) & 15) & 16))
def sound6_math(t): return (2 * t & t >> 8 | 5 * t & t >> 7 | 9 * t & t >> 4 | 15 * t & t >> 4)
def sound7_math(t): return (t >> (t >> 12) % 4) + t * (1 + (1 + (t >> 16) % 6) * (t >> 10) * (t >> 11) % 8) ^ t >> 13 ^ t >> 6
def sound8_math(t): return (t * ((t & 4096 != 0) * ((t % 65536 < 59392) * 7 + (t % 65536 >= 59392) * (t >> 6) + ((1 & t >> 14) != 0) * 16) + ((t & 4096 == 0) * 16)) >> (3 & -t >> (t & 2048 != 0) * 2 + (t & 2048 == 0) * 10))
def sound9_math(t): return (t * (t >> 8 * (t >> 15 | t >> 8) & (20 | 5 ^ (t >> 19) >> t | t >> 3)))

# ─── GDI Payload Implementations ──────────────────────────────────────
def shader1():
    start = time.time()
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        surface_full.grab()
        v = random.randint(0, 3)
        surface_full.np_array[:, :, v] = (surface_full.np_array[:, :, v].astype(np.int16) - 25) % 256
        surface_full.draw()
        time.sleep(0.05)

def payload2():
    start = time.time()
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        gdi32.StretchBlt(hdc, 10, 10, W - 20, H - 20, hdc, 0, 0, W, H, 0x9273ecef)
        gdi32.StretchBlt(hdc, -10, -10, W + 20, H + 20, hdc, 0, 0, W, H, 0x9273ecef)
        time.sleep(0.05)

def shader2():
    start = time.time()
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        surface_full.grab()
        v = random.randint(0, 2)
        surface_full.np_array[:, :, v] = np.roll(surface_full.np_array[:, :, v], shift=1, axis=1)
        surface_full.draw()
        time.sleep(0.05)

def sines1():
    start = time.time()
    angle = 0.0
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        a = int(math.sin(angle) * 360)
        gdi32.BitBlt(hdc, a, 0, W, H, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, a, W, H, hdc, 0, 0, SRCPAINT)
        angle += math.pi / 3.0
        time.sleep(0.01)

def shader3_4_5(shader_id):
    start = time.time()
    i = 0
    # Use a smaller buffer to make heavy HSL math run at viewable speed in Python
    sw, sh = 640, 480
    surface_small = GDISurface(sw, sh)
    y_grid, x_grid = np.mgrid[0:sh, 0:sw]
    
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        gdi32.StretchBlt(surface_small.hdc_mem, 0, 0, sw, sh, hdc, 0, 0, W, H, SRCCOPY)
        
        if shader_id == 3:
            fx = i * x_grid * y_grid
            h_val = (fx / 300.0 + y_grid / sh * 0.1) % 1.0
        elif shader_id == 4:
            cx = x_grid * (2.5 / sw) - 2.0
            cy = y_grid * (1.9 / sh) - 0.95
            zx, zy, fx = np.zeros_like(cx, dtype=float), np.zeros_like(cy, dtype=float), np.zeros_like(cx, dtype=int)
            for _ in range(50):
                mask = (zx*zx + zy*zy) < 10
                fczx = zx*zx - zy*zy + cx
                zy = np.where(mask, 2*zx*zy + cy, zy)
                zx = np.where(mask, fczx, zx)
                fx += mask
            h_val = (fx / 300.0 + y_grid / sh * 0.1) % 1.0
        elif shader_id == 5:
            fx = ((4*i) + ((4*i) * np.sin(x_grid/32.0)) + (4*i) + ((4*i) * np.sin(y_grid/24.0))).astype(int)
            h_val = (fx / 300.0 + y_grid / sh * 0.1) % 1.0

        h, s, l = rgb2hsl_vec(surface_small.np_array)
        h = h_val
        surface_small.np_array[:] = hsl2rgb_vec(h, s, l)

        i += 1
        gdi32.StretchBlt(hdc, 0, 0, W, H, surface_small.hdc_mem, 0, 0, sw, sh, SRCCOPY)
        
        if shader_id == 4:
            gdi32.StretchBlt(hdc, 10, 10, W-20, H-20, hdc, 0, 0, W, H, SRCCOPY)
            gdi32.StretchBlt(hdc, -10, -10, W+20, H+20, hdc, 0, 0, W, H, SRCCOPY)
            
    surface_small.cleanup()

def payload7():
    start = time.time()
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        gdi32.BitBlt(hdc, 0, -30, W, H, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, H-30, W, H, hdc, 0, 0, NOTSRCCOPY)
        gdi32.BitBlt(hdc, -30, 0, W, H, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, W-30, 0, W, H, hdc, 0, 0, NOTSRCCOPY)
        time.sleep(0.01)

def profect():
    start = time.time()
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        gdi32.BitBlt(hdc, 0, 0, W, H, hdc, -30, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, 0, W, H, hdc, W - 30, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, 0, W, H, hdc, 0, -30, SRCCOPY)
        gdi32.BitBlt(hdc, 0, 0, W, H, hdc, 0, H - 30, SRCCOPY)
        
        brush1 = gdi32.CreateSolidBrush(0xFFFFFF)
        gdi32.SelectObject(hdc, brush1)
        gdi32.BitBlt(hdc, 0, 0, W, H, hdc, 0, 0, MERGECOPY)
        gdi32.DeleteObject(brush1)
        
        brush2 = gdi32.CreateSolidBrush(random.randint(0, 0xFFFFFF))
        gdi32.SelectObject(hdc, brush2)
        gdi32.BitBlt(hdc, 0, 0, W, H, hdc, 0, 0, PATINVERT)
        gdi32.DeleteObject(brush2)
        time.sleep(0.01)

def last():
    start = time.time()
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        gdi32.BitBlt(hdc, random.randint(0,2), random.randint(0,2), W, H, hdc, random.randint(0,2), random.randint(0,2), SRCPAINT)
        time.sleep(0.001)

def last2():
    start = time.time()
    texts = ["jwzyexgnlc.exe", "R.I.P PC"]
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        color = random.randint(0, 0xFFFFFF)
        gdi32.SetTextColor(hdc, color)
        gdi32.SetBkMode(hdc, 0)
        font = gdi32.CreateFontA(43, 32, 0, 0, 100, 0, 1, 0, 0, 0, 0, 0, 0, b"Arial")
        gdi32.SelectObject(hdc, font)
        for txt in texts:
            b_txt = txt.encode('ascii')
            gdi32.TextOutA(hdc, random.randint(0, W), random.randint(0, H), b_txt, len(b_txt))
        gdi32.DeleteObject(font)
        time.sleep(0.01)

def run_payload(target, *args):
    t = threading.Thread(target=target, args=args, daemon=True)
    t.start()
    time.sleep(PAYLOAD_TIME)
    user32.InvalidateRect(0, None, 1) # Clear desktop between payloads

# ─── Main Execution Flow ─────────────────────────────────────────────
if __name__ == "__main__":
    res = user32.MessageBoxW(0, "This is a GDI Only, Run? (REAL Desktop Drawing)", "jwzyexgnlc.exe by pankoza", MB_YESNO | MB_ICONEXCLAMATION)
    if res == IDNO:
        sys.exit(0)
    
    res = user32.MessageBoxW(0, "Are you sure? It contains flashing lights - NOT for epilepsy\n\n(Press END key at any time to clear screen and exit)", "jwzyexgnlc.exe - Last Warning", MB_YESNO | MB_ICONEXCLAMATION)
    if res == IDNO:
        sys.exit(0)

    print("Starting Real GDI Simulation... Press END key to clear screen and exit.")

    run_payload(shader1); play_bytebeat(16000, PAYLOAD_TIME, sound1_math)
    run_payload(payload2); play_bytebeat(22050, PAYLOAD_TIME, sound2_math)
    run_payload(shader2); play_bytebeat(22050, PAYLOAD_TIME, sound3_math)
    
    t_sines = threading.Thread(target=sines1, daemon=True); t_sines.start()
    play_bytebeat(22050, PAYLOAD_TIME, sound3_math)
    time.sleep(PAYLOAD_TIME)
    user32.InvalidateRect(0, None, 1)

    run_payload(shader3_4_5, 3); play_bytebeat(22050, PAYLOAD_TIME, sound4_math)
    run_payload(shader3_4_5, 4); play_bytebeat(22050, PAYLOAD_TIME, sound5_math)
    run_payload(shader3_4_5, 5); play_bytebeat(11025, PAYLOAD_TIME, sound6_math)
    run_payload(payload7); play_bytebeat(8000, PAYLOAD_TIME, sound7_math)
    run_payload(profect); play_bytebeat(8000, PAYLOAD_TIME, sound8_math)
    run_payload(last); play_bytebeat(8000, PAYLOAD_TIME, sound9_math)
    
    t_last2 = threading.Thread(target=last2, daemon=True); t_last2.start()
    play_bytebeat(8000, PAYLOAD_TIME, sound9_math)
    time.sleep(PAYLOAD_TIME)
    
    # Final Cleanup
    user32.InvalidateRect(0, None, 1)
    surface_full.cleanup()
    user32.ReleaseDC(0, hdc)
    print("Simulation finished. Screen cleared.")