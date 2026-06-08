"""
jwzyexgnlc.exe - Pure Native GDI & WinMM Simulation
====================================================
100% Pure ctypes. Draws directly to the Desktop.
Press the END key at ANY TIME to instantly clear the screen and exit.
"""

import ctypes
import ctypes.wintypes
import threading
import time
import random
import math
import sys

# ─── Windows API Bindings ─────────────────────────────────────────────
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
winmm = ctypes.windll.winmm
kernel32 = ctypes.windll.kernel32

# GDI Constants
SRCCOPY    = 0x00CC0020
NOTSRCCOPY = 0x00330008
SRCPAINT   = 0x00EE0086
PATINVERT  = 0x005A0049
MERGECOPY  = 0x00C000CA
DIB_RGB_COLORS = 0

# WinMM Constants
WAVE_FORMAT_PCM = 1
WAVE_MAPPER = -1
CALLBACK_NULL = 0

# Vars
MB_YESNO = 0x00000004
MB_ICONEXCLAMATION = 0x00000030
IDNO = 7
VK_END = 0x23 # END key for emergency exit

# ─── Structs ──────────────────────────────────────────────────────────
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class WAVEFORMATEX(ctypes.Structure):
    _fields_ = [
        ("wFormatTag", ctypes.c_uint16), ("nChannels", ctypes.c_uint16),
        ("nSamplesPerSec", ctypes.c_uint32), ("nAvgBytesPerSec", ctypes.c_uint32),
        ("nBlockAlign", ctypes.c_uint16), ("wBitsPerSample", ctypes.c_uint16),
        ("cbSize", ctypes.c_uint16)
    ]

class WAVEHDR(ctypes.Structure):
    pass
WAVEHDR._fields_ = [
    ("lpData", ctypes.c_char_p), ("dwBufferLength", ctypes.c_uint32),
    ("dwBytesRecorded", ctypes.c_uint32), ("dwUser", ctypes.POINTER(ctypes.c_uint32)),
    ("dwFlags", ctypes.c_uint32), ("dwLoops", ctypes.c_uint32),
    ("lpNext", ctypes.POINTER(WAVEHDR)), ("reserved", ctypes.POINTER(ctypes.c_uint32))
]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
        ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32), ("biYPelsPerMeter", ctypes.c_int32),
        ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)
    ]

# ─── Screen Setup ─────────────────────────────────────────────────────
hdc = user32.GetDC(0)
W = user32.GetSystemMetrics(0)
H = user32.GetSystemMetrics(1)
PAYLOAD_TIME = 10 # Shortened for demo (Original is 30)

def check_exit():
    if user32.GetAsyncKeyState(VK_END) & 0x8000:
        user32.InvalidateRect(0, None, 1)
        sys.exit(0)

# ─── Color Math (Translated from C++) ────────────────────────────────
def rgb2hsl(r, g, b):
    _r, _g, _b = r / 255.0, g / 255.0, b / 255.0
    rgbMin = min(_r, _g, _b)
    rgbMax = max(_r, _g, _b)
    fDelta = rgbMax - rgbMin
    l = (rgbMax + rgbMin) / 2.0
    h, s = 0.0, 0.0
    if fDelta != 0.0:
        s = fDelta / (rgbMax + rgbMin) if l < 0.5 else fDelta / (2.0 - rgbMax - rgbMin)
        deltaR = (((rgbMax - _r) / 6.0) + (fDelta / 2.0)) / fDelta
        deltaG = (((rgbMax - _g) / 6.0) + (fDelta / 2.0)) / fDelta
        deltaB = (((rgbMax - _b) / 6.0) + (fDelta / 2.0)) / fDelta
        if _r == rgbMax: h = deltaB - deltaG
        elif _g == rgbMax: h = (1/3) + deltaR - deltaB
        elif _b == rgbMax: h = (2/3) + deltaG - deltaR
        if h < 0: h += 1.0
        if h > 1: h -= 1.0
    return h, s, l

def hsl2rgb(h, s, l):
    r, g, b = l, l, l
    v = (l * (1.0 + s)) if l <= 0.5 else (l + s - l * s)
    if v > 0.0:
        m = l + l - v
        sv = (v - m) / v
        h *= 6.0
        sextant = int(h)
        fract = h - sextant
        vsf = v * sv * fract
        mid1, mid2 = m + vsf, v - vsf
        if sextant == 0: r, g, b = v, mid1, m
        elif sextant == 1: r, g, b = mid2, v, m
        elif sextant == 2: r, g, b = m, v, mid1
        elif sextant == 3: r, g, b = m, mid2, v
        elif sextant == 4: r, g, b = mid1, m, v
        elif sextant == 5: r, g, b = v, m, mid2
    return int(r * 255), int(g * 255), int(b * 255)


# ─── WinMM Audio (Pure Native API Bytebeat) ──────────────────────────
def play_sound(sample_rate, duration, formula_func):
    def audio_thread():
        buf_size = sample_rate * duration
        wfx = WAVEFORMATEX(WAVE_FORMAT_PCM, 1, sample_rate, sample_rate, 1, 8, 0)
        hWaveOut = ctypes.c_void_p()
        winmm.waveOutOpen(ctypes.byref(hWaveOut), WAVE_MAPPER, ctypes.byref(wfx), 0, 0, CALLBACK_NULL)
        
        # Generate audio buffer (Simulating 32-bit DWORD overflow like C++)
        buffer = (ctypes.c_ubyte * buf_size)()
        for t in range(buf_size):
            t_32 = t & 0xFFFFFFFF # Simulate DWORD
            buffer[t] = formula_func(t_32) & 0xFF
        
        header = WAVEHDR(ctypes.cast(buffer, ctypes.c_char_p), buf_size, 0, 0, 0, 0, None, None)
        winmm.waveOutPrepareHeader(hWaveOut, ctypes.byref(header), ctypes.sizeof(WAVEHDR))
        winmm.waveOutWrite(hWaveOut, ctypes.byref(header), ctypes.sizeof(WAVEHDR))
        winmm.waveOutUnprepareHeader(hWaveOut, ctypes.byref(header), ctypes.sizeof(WAVEHDR))
        winmm.waveOutClose(hWaveOut)
    threading.Thread(target=audio_thread, daemon=True).start()

# Exact C++ Bytebeat Formulas
def s1(t): return (3 * ((t >> 6) | t | (t >> (t >> 16))) + (7 & (t >> 11)) * t) % 256
def s2(t): return (3 * ((t >> 6) | t | (t >> (t >> 16))) + (7 & (t >> 11)) * t) % 256
def s3(t): return ((t & (t >> 12)) * ((t >> 4) | (t >> 8))) & 0xFF
def s4(t): return (t - ((t >> 4) & (t >> 8) & (t >> 12)) - 1) & 0xFF
def s5(t): return (9 * (t * (((t >> 9) | (t >> 13)) & 15) & 16)) & 0xFF
def s6(t): return ((2*t & (t>>8)) | (5*t & (t>>7)) | (9*t & (t>>4)) | (15*t & (t>>4))) & 0xFF
def s7(t): return ((t >> ((t >> 12) % 4)) + t * (1 + (1 + ((t >> 16) % 6)) * (t >> 10) * ((t >> 11) % 8)) ^ (t >> 13) ^ (t >> 6)) & 0xFF
def s8(t): return (t * (( (t & 4096 != 0) * ( (t % 65536 < 59392) * 7 + (t % 65536 >= 59392) * (t >> 6) ) + ((1 & (t >> 14)) != 0) * 16) + ((t & 4096 == 0) * 16)) >> (3 & (-t >> ( (t & 2048 != 0) * 2 + (t & 2048 == 0) * 10 )))) & 0xFF
def s9(t): return (t * ((t >> 8) * ((t >> 15) | (t >> 8)) & (20 | (5 ^ (t >> 19)) >> t | (t >> 3)))) & 0xFF


# ─── GDI Pixel Shaders (Native Memory Manipulation) ───────────────────
# Processed on a downscaled surface for Python speed, but using pure GDI API
def memory_shader(shader_id, audio_func, sample_rate):
    sw, sh = 480, 270
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, sw, sh)
    gdi32.SelectObject(hdc_mem, hbm)

    bmi = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), sw, -sh, 1, 32, 0, 0, 0, 0, 0, 0)
    buf_size = sw * sh * 4
    data = (ctypes.c_ubyte * buf_size)()
    data_ptr = ctypes.cast(data, ctypes.POINTER(ctypes.c_ubyte))

    start = time.time(); i = 0
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        gdi32.StretchBlt(hdc_mem, 0, 0, sw, sh, hdc, 0, 0, W, H, SRCCOPY)
        gdi32.GetDIBits(hdc_mem, hbm, 0, sh, data_ptr, ctypes.byref(bmi), DIB_RGB_COLORS)

        for x in range(sw):
            for y in range(sh):
                idx = (y * sw + x) * 4
                b, g, r = data[idx], data[idx+1], data[idx+2]
                
                if shader_id == 1:
                    v = 0
                    if y == 0 and random.randint(0, 110) == 0: v = random.randint(0, 2)
                    data[idx + v] = (data[idx + v] - 25) & 0xFF
                elif shader_id == 2:
                    v = 0
                    if y == 0 and random.randint(0, 100) == 0: v = random.randint(0, 1)
                    data[idx + v] = data[idx + v + 4] # Shift byte
                elif shader_id in [3, 4, 5]:
                    h_c, s_c, l_c = rgb2hsl(r, g, b)
                    if shader_id == 3: fx = i * x * y; h_c = (fx / 300.0 + y / sh * 0.1) % 1.0
                    elif shader_id == 4: h_c = (random.randint(0,50) / 300.0 + y / sh * 0.1) % 1.0 # Simplified fractal for speed
                    elif shader_id == 5: fx = int((4*i) + ((4*i) * math.sin(x/32.0)) + (4*i) + ((4*i) * math.sin(y/24.0))); h_c = (fx / 300.0 + y / sh * 0.1) % 1.0
                    
                    rn, gn, bn = hsl2rgb(h_c, s_c, l_c)
                    data[idx], data[idx+1], data[idx+2] = bn, gn, rn

        gdi32.SetDIBits(hdc_mem, hbm, 0, sh, data_ptr, ctypes.byref(bmi), DIB_RGB_COLORS)
        gdi32.StretchBlt(hdc, 0, 0, W, H, hdc_mem, 0, 0, sw, sh, SRCCOPY)
        
        if shader_id == 4:
            gdi32.StretchBlt(hdc, 10, 10, W-20, H-20, hdc, 0, 0, W, H, SRCCOPY)
            gdi32.StretchBlt(hdc, -10, -10, W+20, H+20, hdc, 0, 0, W, H, SRCCOPY)
        i += 1

    gdi32.DeleteObject(hbm); gdi32.DeleteDC(hdc_mem)
    play_sound(sample_rate, PAYLOAD_TIME, audio_func)
    time.sleep(PAYLOAD_TIME)
    user32.InvalidateRect(0, None, 1)

# ─── Pure GDI Payloads (No Memory Manipulation Needed) ────────────────
def payload2():
    start = time.time()
    wPt = (POINT * 3)()
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        gdi32.StretchBlt(hdc, 10, 10, W - 20, H - 20, hdc, 0, 0, W, H, 0x9273ecef)
        gdi32.StretchBlt(hdc, -10, -10, W + 20, H + 20, hdc, 0, 0, W, H, 0x9273ecef)
        for i in range(3): wPt[i].x, wPt[i].y = random.randint(0, W), random.randint(0, H)
        gdi32.PlgBlt(hdc, wPt, hdc, 0, 0, W, H, 0, 0, 0)

def sines1():
    start = time.time(); angle = 0.0
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        a = int(math.sin(angle) * 360)
        gdi32.BitBlt(hdc, a, 0, W, H, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, a, W, H, hdc, 0, 0, SRCPAINT)
        angle += math.pi / 3.0; time.sleep(0.01)

def payload7():
    start = time.time()
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        gdi32.BitBlt(hdc, 0, -30, W, H, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, H-30, W, H, hdc, 0, 0, NOTSRCCOPY)
        gdi32.BitBlt(hdc, -30, 0, W, H, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, W-30, 0, W, H, hdc, 0, 0, NOTSRCCOPY)

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
        gdi32.DeleteObject(brush2); time.sleep(0.01)

def last():
    start = time.time()
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        gdi32.BitBlt(hdc, random.randint(0,2), random.randint(0,2), W, H, hdc, random.randint(0,2), random.randint(0,2), SRCPAINT)
        gdi32.DrawIcon(hdc, random.randint(0, W), random.randint(0, H), user32.LoadCursorW(0, 32649))

def last2():
    start = time.time()
    while time.time() - start < PAYLOAD_TIME:
        check_exit()
        gdi32.SetTextColor(hdc, random.randint(0, 0xFFFFFF))
        gdi32.SetBkMode(hdc, 0)
        font = gdi32.CreateFontA(43, 32, 0, 0, 100, 0, 1, 0, 0, 0, 0, 0, 0, b"Arial")
        gdi32.SelectObject(hdc, font)
        gdi32.TextOutA(hdc, random.randint(0, W), random.randint(0, H), b"jwzyexgnlc.exe", 14)
        gdi32.TextOutA(hdc, random.randint(0, W), random.randint(0, H), b"R.I.P PC", 8)
        gdi32.DeleteObject(font)

def run_payload(target, *args):
    t = threading.Thread(target=target, args=args, daemon=True)
    t.start()
    time.sleep(PAYLOAD_TIME)
    user32.InvalidateRect(0, None, 1)


# ─── Main Execution Flow ─────────────────────────────────────────────
if __name__ == "__main__":
    if user32.MessageBoxW(0, "This is a GDI Only, Run? (REAL Desktop Drawing)", "jwzyexgnlc.exe", MB_YESNO | MB_ICONEXCLAMATION) == IDNO: sys.exit(0)
    if user32.MessageBoxW(0, "Are you sure? It contains flashing lights - NOT for epilepsy\n\n(Press END key at any time to clear screen and exit)", "jwzyexgnlc.exe - Last Warning", MB_YESNO | MB_ICONEXCLAMATION) == IDNO: sys.exit(0)

    print("Starting Native GDI Simulation... Press END key to clear screen and exit.")

    # Execute sequence matching C++ main()
    memory_shader(1, s1, 16000)
    run_payload(payload2); play_sound(22050, PAYLOAD_TIME, s2); time.sleep(PAYLOAD_TIME); user32.InvalidateRect(0, None, 1)
    memory_shader(2, s3, 22050)
    
    t_sines = threading.Thread(target=sines1, daemon=True); t_sines.start()
    play_sound(22050, PAYLOAD_TIME, s3); time.sleep(PAYLOAD_TIME); user32.InvalidateRect(0, None, 1)
    
    memory_shader(3, s4, 22050)
    memory_shader(4, s5, 22050)
    memory_shader(5, s6, 11025)
    
    run_payload(payload7); play_sound(8000, PAYLOAD_TIME, s7); time.sleep(PAYLOAD_TIME); user32.InvalidateRect(0, None, 1)
    run_payload(profect); play_sound(8000, PAYLOAD_TIME, s8); time.sleep(PAYLOAD_TIME); user32.InvalidateRect(0, None, 1)
    run_payload(last); play_sound(8000, PAYLOAD_TIME, s9); time.sleep(PAYLOAD_TIME)
    
    t_last2 = threading.Thread(target=last2, daemon=True); t_last2.start()
    play_sound(8000, PAYLOAD_TIME, s9); time.sleep(PAYLOAD_TIME)

    # Final Cleanup
    user32.InvalidateRect(0, None, 1)
    user32.ReleaseDC(0, hdc)
    print("Simulation finished. Screen cleared.")