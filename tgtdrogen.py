import ctypes
import math
import random
import time
import threading
from ctypes import wintypes

# --- Windows API Definitions ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
winmm = ctypes.windll.winmm
kernel32 = ctypes.windll.kernel32
msimg32 = ctypes.windll.msimg32

# Constants
SRCCOPY = 0x00CC0020
PATINVERT = 0x005A0049
SRCINVERT = 0x00660046
NOTSRCERASE = 0x001100A6
NOTSRCCOPY = 0x00330008
GM_ADVANCED = 2
AC_SRC_OVER = 0x00

# Structures
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class SIZE(ctypes.Structure):
    _fields_ = [("cx", wintypes.LONG), ("cy", wintypes.LONG)]

class XFORM(ctypes.Structure):
    _fields_ = [("eM11", ctypes.c_float), ("eM12", ctypes.c_float),
                ("eM21", ctypes.c_float), ("eM22", ctypes.c_float),
                ("eDx", ctypes.c_float), ("eDy", ctypes.c_float)]

class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [("BlendOp", ctypes.c_byte), ("BlendFlags", ctypes.c_byte),
                ("SourceConstantAlpha", ctypes.c_byte), ("AlphaFormat", ctypes.c_byte)]

# --- Global Logic ---
sw = user32.GetSystemMetrics(0)
sh = user32.GetSystemMetrics(1)
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

# --- Audio Engine (Bytebeat) ---
def audio_thread_manager():
    # Formulas ported from the C++ AudioSequences
    formulas = [
        lambda t: (((t & t >> 8) - (t >> 13 & t)) & ((t & t >> 8) - (t >> 13))) ^ (t >> 8 & t), # Seq 1
        lambda t: (t - (t >> 4 & t >> 8) & t >> 12) - 1, # Seq 2
        lambda t: ((t >> 8 & t >> 4) >> (t >> 16 & t >> 8)) * t, # Seq 3
        lambda t: (t & (t >> 7 | t >> 8 | t >> 16) ^ t) * t, # Seq 4
        lambda t: (t * t // (1 + (t >> 9 & t >> 8))) & 128, # Seq 5
    ]
    
    sample_rate = 8000
    duration = 5 # seconds per formula
    
    # WaveOut initialization: 1 channel, 8000Hz, 8-bit
    wfx = bytes([1, 0, 1, 0, 64, 31, 0, 0, 64, 31, 0, 0, 1, 0, 8, 0, 0, 0])
    h_waveout = wintypes.HANDLE()
    winmm.waveOutOpen(ctypes.byref(h_waveout), -1, wfx, 0, 0, 0)

    while True:
        for formula in formulas:
            num_samples = sample_rate * duration
            audio_buffer = bytearray([formula(t) & 0xFF for t in range(num_samples)])
            header = ctypes.create_string_buffer(bytes(audio_buffer))
            winmm.waveOutWrite(h_waveout, header, len(header))
            time.sleep(duration)

# --- Visual Payloads (GDI) ---

def payload_invert_flash(hdc, t):
    brush = gdi32.CreateSolidBrush((t % 256) | ((t // 2 % 256) << 8) | ((t // 2 % 256) << 16))
    gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, 0, 0, sw, sh, PATINVERT)
    gdi32.DeleteObject(brush)
    time.sleep(0.015)

def payload_glitch_stretch(hdc, t):
    hcdc = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, sw, sh)
    gdi32.SelectObject(hcdc, hbm)
    gdi32.BitBlt(hcdc, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)
    
    for _ in range(5):
        x = random.randint(0, sw - 100)
        y = random.randint(0, sh - 100)
        gdi32.StretchBlt(hdc, x + random.randint(-10, 10), y + random.randint(-10, 10), 
                        100, 100, hcdc, x, y, 50, 50, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hcdc)
    time.sleep(0.05)

def payload_alpha_rotate(hdc, t):
    hcdc = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, sw, sh)
    gdi32.SelectObject(hcdc, hbm)
    gdi32.BitBlt(hcdc, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)

    gdi32.SetGraphicsMode(hdc, GM_ADVANCED)
    angle = 0.02 
    xform = XFORM(math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle), 0, 0)
    gdi32.SetWorldTransform(hdc, ctypes.byref(xform))

    blf = BLENDFUNCTION(AC_SRC_OVER, 0, 160, 0) # Alpha transparency
    msimg32.AlphaBlend(hdc, 0, 0, sw, sh, hcdc, 0, 0, sw, sh, blf)

    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hcdc)
    time.sleep(0.02)

# --- Controller ---

def main():
    # Warnings
    if user32.MessageBoxW(0, "Execute Safe GDL Python Tribute?\nNo files will be harmed.", "Safety First", 4 | 48) != 6:
        return

    init_dpi()
    
    # Start Audio thread
    threading.Thread(target=audio_thread_manager, daemon=True).start()

    # Get Desktop Context
    hdc = user32.GetDC(0)
    
    payloads = [
        (payload_invert_flash, 10),
        (payload_glitch_stretch, 10),
        (payload_alpha_rotate, 10)
    ]

    print("Sequence started. Press Ctrl+C in terminal to stop.")
    try:
        for func, duration in payloads:
            start_time = time.time()
            t = 0
            while time.time() - start_time < duration:
                func(hdc, t)
                t += 1
            # Refresh screen
            user32.InvalidateRect(0, 0, 0)
            time.sleep(0.5)
            
        # Final stage (Harmless message boxes)
        for _ in range(5):
            threading.Thread(target=lambda: user32.MessageBoxW(0, "Sequence Complete", "GDL Only", 0x40)).start()
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        pass
    finally:
        user32.ReleaseDC(0, hdc)
        user32.InvalidateRect(0, 0, 0) 
        print("Sequence finished. Screen refreshed.")

if __name__ == "__main__":
    main()