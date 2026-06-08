import ctypes
import ctypes.wintypes
import math
import random
import threading
import time
import winsound
import tempfile
import numpy as np

# --- Setup Windows API ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
msimg32 = ctypes.windll.msimg32
sw = user32.GetSystemMetrics(0)
sh = user32.GetSystemMetrics(1)

# GDI Constants
SRCCOPY = 0x00CC0020
SRCINVERT = 0x00660046
PATINVERT = 0x005A0049
IDI_ERROR = 32513

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32), ("biYPelsPerMeter", ctypes.c_int32),
                ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)]

# --- State Management ---
current_shader = 0  # Controls which shader logic runs
shader_time_var = 0 # Incrementor for shaders that need 't' or 'i'

# --- Hue Function ---
class HueCycler:
    def __init__(self):
        self.r, self.g, self.b = 255, 0, 0
        self.stage = 0
    def get(self, shift):
        if self.stage == 0:
            if self.g < 255: self.g += shift
            else: self.stage = 1
        elif self.stage == 1:
            if self.r > 0: self.r -= shift
            else: self.stage = 2
        elif self.stage == 2:
            if self.b < 255: self.b += shift
            else: self.stage = 3
        elif self.stage == 3:
            if self.g > 0: self.g -= shift
            else: self.stage = 4
        elif self.stage == 4:
            if self.r < 255: self.r += shift
            else: self.stage = 5
        elif self.stage == 5:
            if self.b > 0: self.b -= shift
            else: self.stage = 0
        return (self.r & 0xff) | ((self.g & 0xff) << 8) | ((self.b & 0xff) << 16)

hue = HueCycler()

# --- Audio Engine ---
def play_audio(formula_id):
    rate = 32000 if formula_id == 10 else 8000
    duration = 31
    buf = bytearray()
    for t in range(rate * duration):
        if formula_id == 1: v = t & t >> 8
        elif formula_id == 2: v = t >> 5 | (t >> 2) * (t >> 5)
        elif formula_id == 3: v = 2 * (t >> 5 & t) - (t >> 5) + t * (t >> 14 & 14)
        elif formula_id == 4: v = t + (t & t ^ t >> 6) - t * (t >> 9 & (2 if t % 16 else 6) & t >> 9)
        elif formula_id == 5: v = t * (t ^ t + (t >> 15 | 1) ^ (t - 1280 ^ t) >> 10)
        elif formula_id == 6: v = t * ((t // 2 >> 10 | t % 16 * t >> 8) & 8 * t >> 12 & 18) | -(t // 16) + 64
        elif formula_id == 7: v = t * (6 if t & 16384 else 5) * (4 - (1 & t >> 8)) >> (3 & t >> 9) | (t | t * 3) >> 5
        elif formula_id == 8: v = t * ((6 if t & 4096 else 16) + (1 & t >> 14)) >> (3 & t >> 8) | t >> (3 if t & 4096 else 4)
        elif formula_id == 9: v = t * ((7 if t % 65536 < 59392 else t & 7 if t & 4096 else 16) ^ (1 & t >> 14)) >> (3 & -t >> (2 if t & 2048 else 10))
        elif formula_id == 10: v = t * random.randint(0, 255)
        buf.append(v & 0xff)
    
    header = b'RIFF' + (len(buf) + 36).to_bytes(4, 'little') + b'WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00' + \
             rate.to_bytes(4, 'little') + rate.to_bytes(4, 'little') + b'\x01\x00\x08\x00data' + \
             len(buf).to_bytes(4, 'little')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(header + buf)
        winsound.PlaySound(f.name, winsound.SND_FILENAME | winsound.SND_ASYNC)

# --- The "Master" Shader Thread ---
def shader_master():
    global shader_time_var
    hdc = user32.GetDC(0)
    hmem = gdi32.CreateCompatibleDC(hdc)
    bmi = BITMAPINFOHEADER(biSize=ctypes.sizeof(BITMAPINFOHEADER), biWidth=sw, biHeight=-sh, biPlanes=1, biBitCount=32)
    ptr = ctypes.c_void_p()
    hbit = gdi32.CreateDIBSection(hdc, ctypes.byref(bmi), 0, ctypes.byref(ptr), None, 0)
    gdi32.SelectObject(hmem, hbit)
    
    grid_x, grid_y = np.meshgrid(np.arange(sw), np.arange(sh))
    indices = (grid_y * sw + grid_x).astype(np.uint32)

    while True:
        if current_shader == 0: 
            time.sleep(0.1)
            continue
            
        gdi32.BitBlt(hmem, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)
        arr = np.frombuffer((ctypes.c_byte * (sw * sh * 4)).from_address(ptr.value), dtype=np.uint32)
        
        if current_shader == 1: arr += (grid_x + grid_y).flatten().astype(np.uint32)
        elif current_shader == 2: arr += 360
        elif current_shader == 3: arr += (grid_x ^ grid_y).flatten().astype(np.uint32)
        elif current_shader == 4: arr[:] = (arr * 2) % 0xFFFFFF
        elif current_shader == 5: arr[:] += (shader_time_var * indices.flatten()) % 0xFFFFFF
        elif current_shader == 6: arr[:] = (shader_time_var * indices.flatten()) % hue.get(3)
        elif current_shader == 7: arr[:] = np.random.randint(0, 0xFFFFFF, size=sw*sh, dtype=np.uint32)
        
        gdi32.BitBlt(hdc, 0, 0, sw, sh, hmem, 0, 0, SRCCOPY)
        shader_time_var += 1
        time.sleep(0.01)

# --- Other Payloads ---
def payload_cur():
    hdc = user32.GetDC(0)
    icon = user32.LoadIconW(0, IDI_ERROR)
    while True:
        pos = ctypes.wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pos))
        user32.SetCursorPos(pos.x + random.randint(-1, 1), pos.y + random.randint(-1, 1))
        user32.DrawIcon(hdc, pos.x - 16, pos.y - 16, icon)
        time.sleep(0.01)

def payload_balls():
    hdc = user32.GetDC(0)
    x, y, sx, sy = 10, 10, 10, 10
    while True:
        brush = gdi32.CreateSolidBrush(hue.get(239))
        gdi32.SelectObject(hdc, brush)
        gdi32.Ellipse(hdc, x, y, x+100, y+100)
        x += sx; y += sy
        if x >= sw or x <= 0: sx *= -1
        if y >= sh or y <= 0: sy *= -1
        gdi32.DeleteObject(brush)
        time.sleep(0.01)

# --- Execution Controller ---
def main():
    global current_shader
    time.sleep(5) # Start delay
    
    # Background Persistent Payloads
    threading.Thread(target=payload_cur, daemon=True).start()
    threading.Thread(target=shader_master, daemon=True).start()
    
    # The Sequence
    phases = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    for p in phases:
        print(f"Starting Phase {p}")
        if p in [1, 2, 3]: current_shader = p
        elif p == 4: current_shader = 0 # shader4 is replaced by BitBlt mess in your C++ code
        elif p == 6: current_shader = 4
        elif p == 7: current_shader = 5
        elif p == 8: current_shader = 6
        elif p == 10: current_shader = 7
        
        play_audio(p)
        
        if p == 3: threading.Thread(target=payload_balls, daemon=True).start()
        
        time.sleep(30) # Wait 30s per phase
        user32.InvalidateRect(0, 0, 0)
        time.sleep(0.1)

if __name__ == "__main__":
    main()