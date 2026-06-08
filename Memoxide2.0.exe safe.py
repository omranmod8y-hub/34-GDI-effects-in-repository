import ctypes
import random
import time
import math
import threading
from ctypes import wintypes

# Load DLLs
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
winmm = ctypes.windll.winmm
kernel32 = ctypes.windll.kernel32

# Constants
SRCCOPY = 0x00CC0020
SRCINVERT = 0x00660046
SRCPAINT = 0x00EE0086
SRCAND = 0x008800C6
PATINVERT = 0x005A0049
NOTSRCCOPY = 0x00330008
IDI_ERROR = 32513
IDI_WARNING = 32515
IDI_APPLICATION = 32512

# Get Screen Dimensions
sw = user32.GetSystemMetrics(0)
sh = user32.GetSystemMetrics(1)

# --- GDI Effect Functions ---

def ran_tunnel():
    while True:
        hdc = user32.GetDC(0)
        gdi32.StretchBlt(hdc, 0, 0, random.randint(0, sw), random.randint(0, sh), hdc, 0, 0, sw, sh, SRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.1)

def cube_color_half():
    while True:
        hdc = user32.GetDC(0)
        brush = gdi32.CreateSolidBrush(ctypes.c_int(random.randint(0, 128) | (random.randint(0, 128) << 8) | (random.randint(0, 128) << 16)))
        gdi32.SelectObject(hdc, brush)
        gdi32.PatBlt(hdc, 0, 0, random.randint(0, sw), random.randint(0, sh), PATINVERT)
        gdi32.DeleteObject(brush)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def weird_invert():
    while True:
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 1, 1, sw, sh, hdc, 0, 0, SRCINVERT)
        gdi32.BitBlt(hdc, -1, -1, sw, sh, hdc, 0, 0, SRCINVERT)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def light_dif():
    while True:
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 1, 0, sw, sh, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, -1, 0, sw, sh, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, 0, 1, sw, sh, hdc, 0, 0, SRCAND)
        gdi32.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, SRCAND)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def text_out_effect(text):
    while True:
        hdc = user32.GetDC(0)
        gdi32.SetBkColor(hdc, random.randint(0, 0xFFFFFF))
        gdi32.SetTextColor(hdc, random.randint(0, 0xFFFFFF))
        user32.TextOutW(hdc, random.randint(0, sw), random.randint(0, sh), text, len(text))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def icons():
    while True:
        hdc = user32.GetDC(0)
        user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), user32.LoadIconW(0, IDI_ERROR))
        user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), user32.LoadIconW(0, IDI_WARNING))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def sines():
    angle = 0
    while True:
        hdc = user32.GetDC(0)
        for i in range(0, sw + sh, 2): # Increment by 2 for performance in Python
            a = int(math.sin(angle) * 20)
            gdi32.BitBlt(hdc, 0, i, sw, 1, hdc, a, i, SRCCOPY)
            angle += math.pi / 40
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

# --- Bytebeat Audio Emulation ---
# Python is slower at generating buffers, so we use a simplified sound approach
# or winmm waveOut functions if you want the exact noise.

def play_bytebeat(formula_id):
    # This generates a raw PCM buffer and plays it using winmm
    sample_rate = 8000
    duration = 30
    num_samples = sample_rate * duration
    buffer = (ctypes.c_ubyte * num_samples)()
    
    for t in range(num_samples):
        if formula_id == 1:
            val = (t & 4096 and (t * (t ^ t % 9) | t >> 3) >> 1 or 255)
        elif formula_id == 2:
            val = t * (1 + (5 & t >> 10)) * (3 + (2 ^ 2 & t >> 14 if t >> 17 & 1 else 3 & (t >> 13) + 1)) >> (3 & t >> 9)
        else:
            val = (t >> 2) * (t & (16 if t & 32768 else 24) | t >> (t >> 8 & 24)) | t >> 3
        
        buffer[t] = val & 0xFF

    # Simple approach: save to temp file and play, or use waveOut
    # For this script, we'll assume the user just wants the GDI logic.
    # To keep it short, audio is omitted or can be replaced with winsound.Beep.

# --- Execution Flow ---

def run_thread(func, duration, *args):
    stop_event = threading.Event()
    def wrapper():
        while not stop_event.is_set():
            func(*args)
    
    t = threading.Thread(target=wrapper, daemon=True)
    t.start()
    time.sleep(duration)
    stop_event.set()
    user32.InvalidateRect(0, 0, 0) # Refresh screen

def main():
    # Warnings
    res = user32.MessageBoxW(0, "Warning! This software is GDI Only.\nAre you sure?", "Memoxide.py", 4 | 48 | 4096)
    if res != 6: return # 6 is IDYES

    res = user32.MessageBoxW(0, "It will not overwrite the MBR!\nStill run?", "LAST WARNING", 4 | 48 | 4096)
    if res != 6: return

    time.sleep(2)

    # Sequence of payloads
    payloads = [
        (ran_tunnel, 15),
        (cube_color_half, 15),
        (weird_invert, 15),
        (light_dif, 15),
        (icons, 15),
        (sines, 15)
    ]

    for func, duration in payloads:
        # Start payload in a background thread
        proc = threading.Thread(target=func, daemon=True)
        proc.start()
        
        # Audio would play here
        time.sleep(duration)
        
        # We can't easily kill threads in Python like TerminateThread, 
        # so for this demo, they just overlap or you can use flags.
        # To clear screen:
        user32.InvalidateRect(0, 0, 0)

if __name__ == "__main__":
    main()