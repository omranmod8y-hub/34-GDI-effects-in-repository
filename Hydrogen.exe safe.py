import ctypes
from ctypes import wintypes
import math
import random
import time
import threading
import sys

# Windows constants
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020
PATINVERT = 0x5A0049
NOTSRCCOPY = 0x00330008
NOTSRCERASE = 0x001100A6
AC_SRC_OVER = 0x00
SRCAND = 0x008800C6
SRCPAINT = 0x00EE0086
WHDR_DONE = 0x00000001

# Load Windows libraries
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32
winmm = ctypes.windll.winmm

# Global timer
g_nCounter = 0
PAYLOAD_TIME = 30  # seconds

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class SIZE(ctypes.Structure):
    _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

class RGBQUAD(ctypes.Structure):
    _fields_ = [("rgbBlue", ctypes.c_ubyte), ("rgbGreen", ctypes.c_ubyte),
                ("rgbRed", ctypes.c_ubyte), ("rgbReserved", ctypes.c_ubyte)]
    
    @property
    def rgb(self):
        return (self.rgbRed << 16) | (self.rgbGreen << 8) | self.rgbBlue
    
    @rgb.setter
    def rgb(self, value):
        self.rgbRed = (value >> 16) & 0xFF
        self.rgbGreen = (value >> 8) & 0xFF
        self.rgbBlue = value & 0xFF

class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [("BlendOp", ctypes.c_ubyte),
                ("BlendFlags", ctypes.c_ubyte),
                ("SourceConstantAlpha", ctypes.c_ubyte),
                ("AlphaFormat", ctypes.c_ubyte)]

# Xorshift32 RNG
xs = 0

def seed_xorshift32(seed):
    global xs
    xs = seed

def xorshift32():
    global xs
    xs ^= (xs << 13) & 0xFFFFFFFF
    xs ^= (xs >> 17) & 0xFFFFFFFF
    xs ^= (xs << 5) & 0xFFFFFFFF
    return xs

def random_int(min_val, max_val):
    return min_val + (xorshift32() % (max_val - min_val + 1))

def get_virtual_screen_pos():
    return POINT(0, 0)

def get_virtual_screen_size():
    return SIZE(user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN))

def rotate_dc(hdc, angle, pt_center):
    """Set world transform for rotation"""
    n_graphics_mode = gdi32.SetGraphicsMode(hdc, 2)  # GM_ADVANCED
    if angle != 0:
        rad = angle * 3.141592653589793 / 180.0
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        class XFORM(ctypes.Structure):
            _fields_ = [("eM11", ctypes.c_float), ("eM12", ctypes.c_float),
                       ("eM21", ctypes.c_float), ("eM22", ctypes.c_float),
                       ("eDx", ctypes.c_float), ("eDy", ctypes.c_float)]
        
        xform = XFORM()
        xform.eM11 = cos_a
        xform.eM12 = sin_a
        xform.eM21 = -sin_a
        xform.eM22 = cos_a
        xform.eDx = pt_center.x - cos_a * pt_center.x + sin_a * pt_center.y
        xform.eDy = pt_center.y - cos_a * pt_center.y - sin_a * pt_center.x
        gdi32.SetWorldTransform(hdc, ctypes.byref(xform))
    return n_graphics_mode

def init_dpi():
    """Set DPI awareness"""
    user32.SetProcessDPIAware()

# Audio Sequences (simplified bytebeat)
def audio_sequence1(samples_per_sec, sample_count, samples):
    for t in range(sample_count):
        val = (((t & t >> 8) - (t >> 13 & t)) & ((t & t >> 8) - (t >> 13))) ^ (t >> 8 & t)
        samples[t] = val & 0xFF

def audio_sequence2(samples_per_sec, sample_count, samples):
    for t in range(sample_count):
        val = (t - (t >> 4 & t >> 8) & t >> 12) - 1
        samples[t] = val & 0xFF

def audio_sequence3(samples_per_sec, sample_count, samples):
    for t in range(sample_count):
        val = ((t >> 8 & t >> 4) >> (t >> 16 & t >> 8)) * t
        samples[t] = val & 0xFF

def audio_sequence4(samples_per_sec, sample_count, samples):
    for t in range(sample_count):
        val = (t & (t >> 7 | t >> 8 | t >> 16) ^ t) * t
        samples[t] = val & 0xFF

def audio_sequence5(samples_per_sec, sample_count, samples):
    for t in range(sample_count):
        val = (t * t / (1 + (t >> 9 & t >> 8))) & 128
        samples[t] = int(val) & 0xFF

def audio_sequence6(samples_per_sec, sample_count, samples):
    for t in range(sample_count):
        val = t >> 5 | (t >> 2) * (t >> 5)
        samples[t] = val & 0xFF

def audio_sequence7(samples_per_sec, sample_count, samples):
    for t in range(sample_count):
        val = 100 * ((t << 2 | t >> 5 | t ^ 63) & (t << 10 | t >> 11))
        samples[t] = (val & 0xFF)

def audio_sequence8(samples_per_sec, sample_count, samples):
    for t in range(sample_count):
        val = t // 8 >> (t >> 9) * t // ((t >> 14 & 3) + 4)
        samples[t] = val & 0xFF

def audio_sequence9(samples_per_sec, sample_count, samples):
    for t in range(sample_count):
        part = -6 * t // 7 if (t & 32768) else (-9 * t & 100) // 11 if (t & 65536) else -9 * (t & 100) // 11
        val = 10 * (t & 5 * t | t >> 6 | part)
        samples[t] = val & 0xFF

def audio_sequence10(samples_per_sec, sample_count, samples):
    for t in range(sample_count):
        val = 10 * (t >> 7 | 3 * t | t >> (t >> 15)) + (t >> 8 & 5)
        samples[t] = val & 0xFF

def execute_audio_sequence(samples_per_sec, sample_count, audio_func):
    """Execute audio sequence using Windows waveOut"""
    import array
    
    # Allocate samples
    samples = array.array('b', [0]) * sample_count
    
    # Generate samples
    audio_func(samples_per_sec, sample_count, samples)
    
    # Play using Windows waveOut (simplified)
    class WAVEFORMATEX(ctypes.Structure):
        _fields_ = [("wFormatTag", ctypes.c_ushort),
                   ("nChannels", ctypes.c_ushort),
                   ("nSamplesPerSec", ctypes.c_ulong),
                   ("nAvgBytesPerSec", ctypes.c_ulong),
                   ("nBlockAlign", ctypes.c_ushort),
                   ("wBitsPerSample", ctypes.c_ushort),
                   ("cbSize", ctypes.c_ushort)]
    
    wfx = WAVEFORMATEX()
    wfx.wFormatTag = 1  # WAVE_FORMAT_PCM
    wfx.nChannels = 1
    wfx.nSamplesPerSec = samples_per_sec
    wfx.nAvgBytesPerSec = samples_per_sec
    wfx.nBlockAlign = 1
    wfx.wBitsPerSample = 8
    wfx.cbSize = 0
    
    h_wave_out = ctypes.c_void_p()
    winmm.waveOutOpen(ctypes.byref(h_wave_out), -1, ctypes.byref(wfx), 0, 0, 0)
    
    # Play and wait
    time.sleep(sample_count / samples_per_sec)
    
    winmm.waveOutClose(h_wave_out)

def audio_payload_thread(audio_sequences):
    """Thread for playing audio sequences"""
    while True:
        for i in range(10):  # AUDIO_NUM = 10
            seq = audio_sequences[i]
            execute_audio_sequence(seq[0], seq[1], seq[2])
            time.sleep(0.1)

# Payloads
def payload1(t, hdc):
    pt = get_virtual_screen_pos()
    sz = get_virtual_screen_size()
    brush = gdi32.CreateSolidBrush(((t % 256) << 16) | ((t // 2 % 256) << 8) | (t // 2 % 256))
    gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, pt.x, pt.y, sz.cx, sz.cy, PATINVERT)
    gdi32.DeleteObject(brush)
    time.sleep(0.015)

def payload2(t, hdc):
    pt = get_virtual_screen_pos()
    sz = get_virtual_screen_size()
    t_val = t * 10
    gdi32.BitBlt(hdc, pt.x, pt.y, sz.cx, sz.cy, hdc, pt.x + t_val % sz.cx, pt.y + t_val % sz.cy, NOTSRCERASE)
    brush = gdi32.CreateSolidBrush((random_int(0, 255) << 16) | (random_int(0, 255) << 8) | random_int(0, 255))
    gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, pt.x, pt.y, sz.cx, sz.cy, PATINVERT)
    gdi32.DeleteObject(brush)
    time.sleep(0.015)

def payload3(t, hdc):
    pt = get_virtual_screen_pos()
    sz = get_virtual_screen_size()
    hcdc = gdi32.CreateCompatibleDC(hdc)
    hbitmap = gdi32.CreateCompatibleBitmap(hdc, sz.cx, sz.cy)
    gdi32.SelectObject(hcdc, hbitmap)
    gdi32.BitBlt(hcdc, pt.x, pt.y, sz.cx, sz.cy, hdc, pt.x, pt.y, SRCCOPY)
    
    for i in range(sz.cx // 10):
        for j in range(sz.cy // 10):
            gdi32.StretchBlt(hcdc, i * 10, j * 10, 10, 10, hcdc, i * 10, j * 10, 1, 1, SRCCOPY)
    
    gdi32.BitBlt(hdc, pt.x, pt.y, sz.cx, sz.cy, hcdc, pt.x, pt.y, SRCCOPY)
    gdi32.DeleteObject(hcdc)
    gdi32.DeleteObject(hbitmap)
    time.sleep(0.1)

def payload4(t, hdc):
    pt = get_virtual_screen_pos()
    sz = get_virtual_screen_size()
    hcdc = gdi32.CreateCompatibleDC(hdc)
    hbitmap = gdi32.CreateCompatibleBitmap(hdc, sz.cx, sz.cy)
    gdi32.SelectObject(hcdc, hbitmap)
    gdi32.BitBlt(hcdc, 0, 0, sz.cx, sz.cy, hdc, 0, 0, SRCCOPY)
    
    blf = BLENDFUNCTION()
    blf.BlendOp = AC_SRC_OVER
    blf.SourceConstantAlpha = 128
    
    win32gui_alpha = ctypes.windll.msimg32.AlphaBlend
    win32gui_alpha(hdc, pt.x + t % 200 + 10, pt.y - t % 25, sz.cx, sz.cy, 
                   hcdc, pt.x, pt.y, sz.cx, sz.cy, ctypes.byref(blf))
    
    gdi32.DeleteObject(hcdc)
    gdi32.DeleteObject(hbitmap)
    time.sleep(0.02)

def payload5(t, hdc):
    sz = get_virtual_screen_size()
    t_val = t * 3
    x = random_int(0, sz.cx - 1)
    y = random_int(0, sz.cy - 1)
    gdi32.BitBlt(hdc, x, y, t_val % sz.cx, t_val % sz.cy, hdc, (x + t_val // 2) % sz.cx, y % sz.cy, SRCCOPY)

def payload6(t, hdc):
    pt = get_virtual_screen_pos()
    sz = get_virtual_screen_size()
    hcdc = gdi32.CreateCompatibleDC(hdc)
    hbitmap = gdi32.CreateCompatibleBitmap(hdc, sz.cx, sz.cy)
    gdi32.SelectObject(hcdc, hbitmap)
    gdi32.BitBlt(hcdc, 0, 0, sz.cx, sz.cy, hdc, 0, 0, SRCCOPY)
    
    p = POINT(sz.cx // 2, sz.cy // 2)
    blf = BLENDFUNCTION()
    blf.BlendOp = AC_SRC_OVER
    blf.SourceConstantAlpha = 128
    
    rotate_dc(hdc, 10, p)
    
    win32gui_alpha = ctypes.windll.msimg32.AlphaBlend
    win32gui_alpha(hdc, 0, t, sz.cx, sz.cy, hcdc, 0, 0, sz.cx, sz.cy, ctypes.byref(blf))
    
    gdi32.DeleteObject(hcdc)
    gdi32.DeleteObject(hbitmap)

def payload7(t, hdc):
    pt = get_virtual_screen_pos()
    sz = get_virtual_screen_size()
    hcdc = gdi32.CreateCompatibleDC(hdc)
    hbitmap = gdi32.CreateCompatibleBitmap(hdc, sz.cx, sz.cy)
    gdi32.SelectObject(hcdc, hbitmap)
    gdi32.BitBlt(hcdc, 0, 0, sz.cx, sz.cy, hdc, 0, 0, SRCCOPY)
    
    p = POINT(sz.cx // 2, sz.cy // 2)
    blf = BLENDFUNCTION()
    blf.BlendOp = AC_SRC_OVER
    blf.SourceConstantAlpha = 128
    
    if t % 2 == 0:
        rotate_dc(hdc, 1, p)
    else:
        rotate_dc(hdc, -1, p)
    
    gdi32.SetBkColor(hdc, (random_int(0, 255) << 16) | (random_int(0, 255) << 8) | random_int(0, 255))
    gdi32.SetTextColor(hdc, (random_int(0, 255) << 16) | (random_int(0, 255) << 8) | random_int(0, 255))
    
    font = gdi32.CreateFontW(32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
    gdi32.SelectObject(hdc, font)
    gdi32.TextOutW(hdc, random_int(0, sz.cx), random_int(0, sz.cy), "HYDROGEN", 8)
    gdi32.DeleteObject(font)
    
    win32gui_alpha = ctypes.windll.msimg32.AlphaBlend
    win32gui_alpha(hdc, 0, 0, sz.cx, sz.cy, hcdc, 0, 0, sz.cx, sz.cy, ctypes.byref(blf))
    
    gdi32.DeleteObject(hcdc)
    gdi32.DeleteObject(hbitmap)

def payload8(t, hdc):
    pt = get_virtual_screen_pos()
    sz = get_virtual_screen_size()
    hcdc = gdi32.CreateCompatibleDC(hdc)
    hbitmap = gdi32.CreateCompatibleBitmap(hdc, sz.cx, sz.cy)
    gdi32.SelectObject(hcdc, hbitmap)
    gdi32.BitBlt(hcdc, 0, 0, sz.cx, sz.cy, hdc, 0, 0, SRCCOPY)
    
    gdi32.SetGraphicsMode(hdc, 2)
    
    class XFORM(ctypes.Structure):
        _fields_ = [("eM11", ctypes.c_float), ("eM12", ctypes.c_float),
                   ("eM21", ctypes.c_float), ("eM22", ctypes.c_float),
                   ("eDx", ctypes.c_float), ("eDy", ctypes.c_float)]
    
    xform = XFORM()
    xform.eM11 = 1
    xform.eM12 = 0.1
    xform.eM21 = 0
    xform.eM22 = 1
    gdi32.SetWorldTransform(hdc, ctypes.byref(xform))
    
    blf = BLENDFUNCTION()
    blf.BlendOp = AC_SRC_OVER
    blf.SourceConstantAlpha = 128
    
    gdi32.SetBkColor(hdc, (random_int(0, 255) << 16) | (random_int(0, 255) << 8) | random_int(0, 255))
    gdi32.SetTextColor(hdc, (random_int(0, 255) << 16) | (random_int(0, 255) << 8) | random_int(0, 255))
    
    font = gdi32.CreateFontW(32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
    gdi32.SelectObject(hdc, font)
    
    for i in range(5):
        gdi32.TextOutW(hdc, random_int(0, sz.cx), random_int(0, sz.cy), "ӉӬլҏ ӎӬ !!!", 11)
    
    gdi32.DeleteObject(font)
    
    win32gui_alpha = ctypes.windll.msimg32.AlphaBlend
    win32gui_alpha(hdc, 0, 0, sz.cx, sz.cy, hcdc, 0, 0, sz.cx, sz.cy, ctypes.byref(blf))
    
    gdi32.DeleteObject(hcdc)
    gdi32.DeleteObject(hbitmap)
    time.sleep(0.05)

def payload9(t, hdc):
    pt = get_virtual_screen_pos()
    sz = get_virtual_screen_size()
    
    points = (POINT * 3)()
    points[0] = POINT(0, 0)
    points[1] = POINT(sz.cx, 0)
    points[2] = POINT(25, sz.cy)
    
    gdi32.PlgBlt(hdc, points, hdc, pt.x, pt.y, sz.cx + 25, sz.cy, None, 0, 0)
    
    brush = gdi32.CreateSolidBrush((random_int(0, 255) << 16) | (random_int(0, 255) << 8) | random_int(0, 255))
    gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, pt.x, pt.y, sz.cx, sz.cy, PATINVERT)
    gdi32.DeleteObject(brush)
    time.sleep(0.05)

def payload10(t, hdc):
    pt = get_virtual_screen_pos()
    sz = get_virtual_screen_size()
    t_val = t * 30
    
    user32.RedrawWindow(None, None, None, 0x0085)  # RDW_ERASE | RDW_INVALIDATE | RDW_ALLCHILDREN
    
    hcdc = gdi32.CreateCompatibleDC(hdc)
    hbitmap = gdi32.CreateCompatibleBitmap(hdc, sz.cx, sz.cy)
    gdi32.SelectObject(hcdc, hbitmap)
    time.sleep(0.05)
    gdi32.BitBlt(hcdc, 0, 0, sz.cx, sz.cy, hdc, 0, 0, NOTSRCCOPY)
    
    pattern_brush = gdi32.CreatePatternBrush(hbitmap)
    gdi32.SelectObject(hdc, pattern_brush)
    gdi32.Ellipse(hdc, t_val % sz.cx + 20, t_val % sz.cy + 20, 
                  t_val % sz.cx + t_val % 101 + 180, t_val % sz.cy + t_val % 101 + 180)
    gdi32.DeleteObject(pattern_brush)
    
    gdi32.BitBlt(hcdc, 0, 0, sz.cx, sz.cy, hdc, 0, 0, NOTSRCCOPY)
    pattern_brush = gdi32.CreatePatternBrush(hbitmap)
    gdi32.SelectObject(hdc, pattern_brush)
    gdi32.Ellipse(hdc, t_val % sz.cx + 10, t_val % sz.cy + 10,
                  t_val % sz.cx + t_val % 101 + 190, t_val % sz.cy + t_val % 101 + 190)
    gdi32.Ellipse(hdc, t_val % sz.cx, t_val % sz.cy,
                  t_val % sz.cx + t_val % 101 + 200, t_val % sz.cy + t_val % 101 + 200)
    gdi32.DeleteObject(pattern_brush)
    
    gdi32.BitBlt(hcdc, 0, 0, sz.cx, sz.cy, hdc, 0, 0, NOTSRCCOPY)
    pattern_brush = gdi32.CreatePatternBrush(hbitmap)
    gdi32.SelectObject(hdc, pattern_brush)
    gdi32.Ellipse(hdc, t_val % sz.cx, t_val % sz.cy,
                  t_val % sz.cx + t_val % 101 + 200, t_val % sz.cy + t_val % 101 + 200)
    gdi32.DeleteObject(pattern_brush)
    
    gdi32.SetBkColor(hdc, (random_int(0, 255) << 16) | (random_int(0, 255) << 8) | random_int(0, 255))
    gdi32.SetTextColor(hdc, (random_int(0, 255) << 16) | (random_int(0, 255) << 8) | random_int(0, 255))
    
    font = gdi32.CreateFontW(32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
    gdi32.SelectObject(hdc, font)
    for i in range(5):
        gdi32.TextOutW(hdc, random_int(0, sz.cx), random_int(0, sz.cy), "     ", 5)
    gdi32.DeleteObject(font)
    
    gdi32.DeleteObject(hcdc)
    gdi32.DeleteObject(hbitmap)

def execute_payload(payload_func, n_time):
    """Execute a payload for specified time"""
    start_time = time.time()
    i = 0
    while time.time() - start_time < n_time:
        hdc_screen = user32.GetDC(0)
        if hdc_screen:
            payload_func(i, hdc_screen)
            user32.ReleaseDC(0, hdc_screen)
        i += 1
        time.sleep(0.01)
    user32.RedrawWindow(None, None, None, 0x0085)
    time.sleep(0.1)

# Simple shaders (simplified versions)
def shader1(t, w, h, prgb_screen):
    for i in range(w * h):
        prgb_screen[i].rgb = (prgb_screen[i].rgb * 2) % 0xFFFFFF

def shader2(t, w, h, prgb_screen):
    for i in range(w * h):
        r = prgb_screen[i].rgbRed
        g = prgb_screen[i].rgbGreen
        b = prgb_screen[i].rgbBlue
        avg = (r + g + b) // 4
        prgb_screen[i].rgb = (((r + 100) % 256) << 16) | (((avg + t) % 256) << 8) | ((avg + i) % 256)

def shader3(t, w, h, prgb_screen):
    for i in range(w * h):
        r = prgb_screen[i].rgbRed
        g = prgb_screen[i].rgbGreen
        b = prgb_screen[i].rgbBlue
        prgb_screen[i].rgb = (((2 * r) % 256) << 16) | (((b + t) % 256) << 8) | ((g + i) % 256)

def shader4(t, w, h, prgb_screen):
    for i in range(w * h):
        r = prgb_screen[i].rgbRed
        g = prgb_screen[i].rgbGreen
        b = prgb_screen[i].rgbBlue
        avg = (r + g + b) // 3
        val = (avg << 16) | (avg << 8) | avg
        prgb_screen[i].rgb = (val + t) % 0xFFFFFF

def shader5(t, w, h, prgb_screen):
    for i in range(w * h):
        if i > 0:
            prgb_screen[i].rgb = (prgb_screen[i].rgb - (xorshift32() % int(i ** 0.5))) % 0xFFFFFF

def shader6(t, w, h, prgb_screen):
    for i in range(w * h):
        if i // 3 < w * h:
            temp = prgb_screen[i].rgb
            prgb_screen[i].rgb = prgb_screen[i // 3].rgb
            prgb_screen[i // 3].rgb = temp

def shader7(t, w, h, prgb_screen):
    for i in range(w * h):
        rand_pixel = xorshift32() % w
        temp_b = prgb_screen[i].rgbBlue
        val = prgb_screen[rand_pixel].rgbBlue
        prgb_screen[i].rgb = (val << 16) | (val << 8) | val
        prgb_screen[rand_pixel].rgb = (temp_b << 16) | (temp_b << 8) | temp_b

def shader8(t, w, h, prgb_screen):
    t_val = t * 10
    for i in range(w):
        for j in range(h):
            if i * j < w * h:
                prgb_screen[i * j].rgb = (i % 256) << 16 | (j % 256) << 8 | (t_val % 256)

def shader9(t, w, h, prgb_screen):
    t_val = t * 50
    for i in range(h):
        for j in range(w):
            idx = i * w + j
            prgb_screen[idx].rgb = (((prgb_screen[idx].rgbRed + i // 10) % 256) << 16) | \
                                   (((prgb_screen[idx].rgbGreen + j // 10) % 256) << 8) | \
                                   ((prgb_screen[idx].rgbBlue + t_val) % 256)

def shader10(t, w, h, prgb_screen):
    for i in range(h):
        for j in range(w):
            temp1 = abs(i + (xorshift32() % 11 - 5))
            temp2 = abs(j + (xorshift32() % 11 - 5))
            src_idx = (temp1 * w + temp2) % (w * h)
            prgb_screen[i * w + j].rgb = prgb_screen[src_idx].rgb

def shader11(t, w, h, prgb_screen):
    for i in range(w * h):
        if i // 3 * 2 < w * h:
            temp = prgb_screen[i].rgb
            prgb_screen[i].rgb = prgb_screen[i // 3 * 2].rgb
            prgb_screen[i // 3 * 2].rgb = temp

def shader12(t, w, h, prgb_screen):
    temp = (RGBQUAD * (w * h))()
    for i in range(w * h):
        temp[i] = prgb_screen[i]
    for i in range(h // 2):
        for j in range(w):
            idx = i * w + j
            new_idx = int(idx + (2 * (h // 2) * i - i * i) ** 0.5) % (w * h)
            prgb_screen[idx].rgb = temp[new_idx].rgb
    for i in range(h // 2, h):
        for j in range(w):
            idx = i * w + j
            new_idx = int(idx + (2 * (h // 2) * i - i * i) ** 0.5) % (w * h)
            prgb_screen[idx].rgb = temp[new_idx].rgb
    time.sleep(0.05)

def shader13(t, w, h, prgb_screen):
    temp = (RGBQUAD * (w * h))()
    for i in range(w * h):
        temp[i] = prgb_screen[i]
    for i in range(h):
        for j in range(w):
            idx = i * w + j
            new_idx = int(j * w + i + (2 * h * i - i * i) ** 0.5) % (w * h)
            prgb_screen[idx].rgb = temp[new_idx].rgb
    time.sleep(0.1)

def shader14(t, w, h, prgb_screen):
    temp = (RGBQUAD * (w * h))()
    for i in range(w * h):
        temp[i] = prgb_screen[i]
    for i in range(h):
        for j in range(w):
            idx = i * w + j
            new_idx = int(j * w + i + (2 * h * j - j * j) ** 0.5) % (w * h)
            prgb_screen[idx].rgb = temp[new_idx].rgb
    time.sleep(0.1)

def shader15(t, w, h, prgb_screen):
    for i in range(w * h):
        prgb_screen[i].rgb = (t * i) % 0xFFFFFF

def shader16(t, w, h, prgb_screen):
    for i in range(w * h):
        val = xorshift32() % 0x100
        prgb_screen[i].rgb = (val << 16) | (val << 8) | val

def execute_shader(shader_func, n_time):
    """Execute a shader for specified time"""
    w = user32.GetSystemMetrics(SM_CXSCREEN)
    h = user32.GetSystemMetrics(SM_CYSCREEN)
    
    start_time = time.time()
    
    # Create DIB section
    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [("biSize", ctypes.c_ulong),
                   ("biWidth", ctypes.c_long),
                   ("biHeight", ctypes.c_long),
                   ("biPlanes", ctypes.c_ushort),
                   ("biBitCount", ctypes.c_ushort),
                   ("biCompression", ctypes.c_ulong),
                   ("biSizeImage", ctypes.c_ulong),
                   ("biXPelsPerMeter", ctypes.c_long),
                   ("biYPelsPerMeter", ctypes.c_long),
                   ("biClrUsed", ctypes.c_ulong),
                   ("biClrImportant", ctypes.c_ulong)]
    
    class BITMAPINFO(ctypes.Structure):
        _fields_ = [("bmiHeader", BITMAPINFOHEADER)]
    
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = w
    bmi.bmiHeader.biHeight = h
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    
    hdc_screen = user32.GetDC(0)
    hdc_temp = gdi32.CreateCompatibleDC(hdc_screen)
    
    prgb_screen_ptr = ctypes.POINTER(RGBQUAD)()
    hbm = gdi32.CreateDIBSection(hdc_screen, ctypes.byref(bmi), 0, ctypes.byref(prgb_screen_ptr), None, 0)
    gdi32.SelectObject(hdc_temp, hbm)
    
    i = 0
    while time.time() - start_time < n_time:
        gdi32.BitBlt(hdc_temp, 0, 0, w, h, hdc_screen, 0, 0, SRCCOPY)
        shader_func(i, w, h, prgb_screen_ptr)
        gdi32.BitBlt(hdc_screen, 0, 0, w, h, hdc_temp, 0, 0, SRCCOPY)
        i += 1
        time.sleep(0.01)
    
    user32.ReleaseDC(0, hdc_screen)
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_temp)
    user32.RedrawWindow(None, None, None, 0x0085)
    time.sleep(0.1)

def windows_corruption_payload():
    """Corrupt windows by renaming and moving them"""
    def enum_windows_proc(hwnd, lparam):
        try:
            # Generate random text
            random_text = ''.join(chr(xorshift32() % 0x9FFF + 0x4E00) for _ in range(random_int(5, 15)))
            user32.SetWindowTextW(hwnd, random_text)
            
            # Move window slightly
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            
            new_left = rect.left + (xorshift32() % 3 - 1)
            new_top = rect.top + (xorshift32() % 3 - 1)
            user32.MoveWindow(hwnd, new_left, new_top, w, h, 1)
            
            # BitBlt on window
            hdc = user32.GetDC(hwnd)
            if xorshift32() % 2 == 0:
                gdi32.BitBlt(hdc, rect.left, rect.top, w, h, hdc, rect.left, rect.top, SRCAND)
            else:
                sz = get_virtual_screen_size()
                gdi32.StretchBlt(hdc, rect.left, rect.top, w, h, hdc, 0, 0, sz.cx, sz.cy, SRCAND)
            user32.ReleaseDC(hwnd, hdc)
            
            user32.EnumChildWindows(hwnd, enum_windows_proc, 0)
        except:
            pass
        return 1
    
    while True:
        user32.EnumWindows(enum_windows_proc, 1)
        time.sleep(0.1)

def message_box_payload():
    """Create message box threads"""
    def msgbox_thread():
        text = ''.join(chr(xorshift32() % 0x9FFF + 0x4E00) for _ in range(random_int(5, 15)))
        title = ''.join(chr(xorshift32() % 0x9FFF + 0x4E00) for _ in range(random_int(5, 15)))
        if xorshift32() % 2 == 0:
            user32.MessageBoxW(0, text, title, 0x00000001 | 0x00000030)  # MB_OKCANCEL | MB_ICONWARNING
        else:
            user32.MessageBoxW(0, text, title, 0x00000005 | 0x00000010)  # MB_RETRYCANCEL | MB_ICONERROR
    
    while True:
        threading.Thread(target=msgbox_thread, daemon=True).start()
        time.sleep(1.5)

def main():
    # Show warning dialogs
    result = user32.MessageBoxW(0, "Gdlonly you have just executed is a safetty.\nYou might safe!\nStill execute it?", 
                                "Hydrogen.exe", 0x00000004 | 0x00000030 | 0x00040000)  # MB_YESNO | MB_ICONWARNING | MB_TOPMOST
    if result != 6:  # IDYES = 6
        return
    
    result = user32.MessageBoxW(0, "THIS IS THE LAST WARNING!\nTHE CREATOR OF THIS safe made by omran !\nSTILL CONTINUE?",
                                "Hydrogen.exe - LAST WARNING", 0x00000004 | 0x00000030 | 0x00040000)
    if result != 6:
        return
    
    # Initialize
    seed_xorshift32(int(time.time() * 1000) & 0xFFFFFFFF)
    user32.SetProcessDPIAware()
    
    # Setup audio sequences
    audio_sequences = [
        (8000, 8000 * PAYLOAD_TIME, audio_sequence1),
        (8000, 8000 * PAYLOAD_TIME, audio_sequence2),
        (8000, 8000 * PAYLOAD_TIME, audio_sequence3),
        (8000, 8000 * PAYLOAD_TIME, audio_sequence4),
        (8000, 8000 * PAYLOAD_TIME, audio_sequence5),
        (8000, 8000 * PAYLOAD_TIME, audio_sequence6),
        (8000, 8000 * PAYLOAD_TIME, audio_sequence7),
        (8000, 8000 * PAYLOAD_TIME, audio_sequence8),
        (8000, 8000 * PAYLOAD_TIME, audio_sequence9),
        (8000, 8000 * PAYLOAD_TIME, audio_sequence10),
    ]
    
    # Start audio thread
    audio_thread = threading.Thread(target=audio_payload_thread, args=(audio_sequences,), daemon=True)
    audio_thread.start()
    
    # Execute all payloads
    payloads = [payload1, payload2, payload3, payload4, payload5,
                payload6, payload7, payload8, payload9, payload10]
    
    print("Starting GDI payloads (each runs for 30 seconds)...")
    for i, payload in enumerate(payloads):
        print(f"Payload {i+1}/10 running...")
        execute_payload(payload, PAYLOAD_TIME)
    
    # Execute all shaders
    shaders = [shader1, shader2, shader3, shader4, shader5,
               shader6, shader7, shader8, shader9, shader10,
               shader11, shader12, shader13, shader14, shader15, shader16]
    
    for i, shader in enumerate(shaders):
        print(f"Shader {i+1}/{len(shaders)} running...")
        execute_shader(shader, PAYLOAD_TIME)
    
    # Start corruption threads
    print("Starting corruption payloads...")
    threading.Thread(target=windows_corruption_payload, daemon=True).start()
    threading.Thread(target=message_box_payload, daemon=True).start()
    
    print("Running corruption for 20 seconds...")
    time.sleep(20)
    
    print("All payloads completed!")
    user32.RedrawWindow(None, None, None, 0x0085)

if __name__ == "__main__":
    print("=" * 60)
    print("GDI HYDROGEN PAYLOAD SYSTEM")
    print("This will affect your actual desktop!")
    print("Press Ctrl+C to stop at any time")
    print("=" * 60)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")
        user32.RedrawWindow(None, None, None, 0x0085)