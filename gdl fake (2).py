import time
import math
import random
import struct
import ctypes
import threading
import winsound
from ctypes import wintypes

# --- Windows GDI & User API Bindings ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Standard GDI Constants
SRCCOPY = 0x00CC0020
SRCPAINT = 0x00EE0086
SRCAND = 0x008800C6
SRCINVERT = 0x00660046
NOTSRCCOPY = 0x00330008
PATINVERT = 0x005A0049
MERGECOPY = 0x00C000CA
CUSTOM_ROP = 0x9273ECEF

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long)
    ]

# Setup global screen dimensions
sw = user32.GetSystemMetrics(0)
sh = user32.GetSystemMetrics(1)

# Custom Python implementation of the Windows C++ RGB macro
def RGB(r, g, b):
    return (r & 0xFF) | ((g & 0xFF) << 8) | ((b & 0xFF) << 16)

# Helper: Generate and play Bytebeat WAV in a separate background thread
def play_bytebeat(formula_func, sample_rate=8000, duration=30):
    num_samples = sample_rate * duration
    audio_data = bytearray(num_samples)
    for t in range(num_samples):
        try:
            audio_data[t] = int(formula_func(t)) & 0xFF
        except ZeroDivisionError:
            audio_data[t] = 0
            
    header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + num_samples,
        b'WAVE',
        b'fmt ',
        16,   # Subchunk1Size
        1,    # AudioFormat (PCM)
        1,    # NumChannels (Mono)
        sample_rate,
        sample_rate, # ByteRate
        1,    # BlockAlign
        8,    # BitsPerSample
        b'data',
        num_samples
    )
    
    wav_bytes = header + audio_data
    
    def audio_target():
        winsound.PlaySound(wav_bytes, winsound.SND_MEMORY)

    audio_thread = threading.Thread(target=audio_target, daemon=True)
    audio_thread.start()


# --- Bytebeat Synthesizer Formulas ---

def sfx_formula_1(t):
    return 3 * (t >> 6 | t | t >> (t >> 16)) + (7 & t >> 11) * t

def sfx_formula_2(t):
    return 3 * (t >> 6 | t | t >> (t >> 16)) + (7 & t >> 11) * t

def sfx_formula_3(t):
    return (t & t >> 12) * (t >> 4 | t >> 8)

def sfx_formula_4(t):
    return (t - (t >> 4 & t >> 8) & t >> 12) - 1

def sfx_formula_5(t):
    return 9 * (t * ((t >> 9 | t >> 13) & 15) & 16)

def sfx_formula_6(t):
    return 2 * t & t >> 8 | 5 * t & t >> 7 | 9 * t & t >> 4 | 15 * t & t >> 4

def sfx_formula_7(t):
    t_32 = t & 0xFFFFFFFF
    return int((t_32 >> (t_32 >> 12) % 4) + t_32 * (1 + (1 + (t_32 >> 16) % 6) * (t_32 >> 10) * (t_32 >> 11) % 8) ^ t_32 >> 13 ^ t_32 >> 6)

def sfx_formula_8(t):
    t_32 = t & 0xFFFFFFFF
    neg_t = (-t) & 0xFFFFFFFF
    inner_val = (7 if (t_32 % 65536 < 59392) else (t_32 >> 6)) if (t_32 & 4096) else 16
    shift_val = 3 & (neg_t >> (2 if (t_32 & 2048) else 10))
    return int((t_32 * (inner_val + (1 & (t_32 >> 14)))) >> shift_val)

def sfx_formula_9(t):
    return int(t * (t >> 8 * (t >> 15 | t >> 8) & (20 | 5 ^ (t >> 19) >> t | t >> 3)))


# --- GDI Thread Definitions ---

def shader1_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        x = random.randint(0, sw - 200)
        y = random.randint(0, sh - 200)
        w = random.randint(100, 400)
        h = random.randint(100, 400)
        gdi32.PatBlt(hdc, x, y, w, h, PATINVERT)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.05)

def payload2_thread(stop_event):
    rekt = RECT()
    w_pt = (POINT * 3)()
    while not stop_event.is_set():
        desktop = user32.GetDesktopWindow()
        user32.GetWindowRect(desktop, ctypes.byref(rekt))
        hdc = user32.GetDC(0)
        
        gdi32.StretchBlt(hdc, 10, 10, sw - 20, sh - 20, hdc, 0, 0, sw, sh, CUSTOM_ROP)
        gdi32.StretchBlt(hdc, -10, -10, sw + 20, sh + 20, hdc, 0, 0, sw, sh, CUSTOM_ROP)
        
        w_pt[0].x = random.randint(0, sw)
        w_pt[0].y = random.randint(0, sh)
        w_pt[1].x = random.randint(0, sw)
        w_pt[1].y = random.randint(0, sh)
        w_pt[2].x = random.randint(0, sw)
        w_pt[2].y = random.randint(0, sh)
        
        gdi32.PlgBlt(hdc, ctypes.byref(w_pt), hdc, rekt.left, rekt.top, rekt.right - rekt.left, rekt.bottom - rekt.top, 0, 0, 0)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.05)

def sines1_thread(stop_event):
    angle = 0.0
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        for i in range(0, sw + sh, 12):
            offset = int(math.sin(angle) * 360)
            gdi32.BitBlt(hdc, 0, i, sw, 1, hdc, offset, i, SRCCOPY)
            gdi32.BitBlt(hdc, i, 0, 1, sh, hdc, i, offset, SRCCOPY)
            angle += (math.pi / 3.0)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.02)

def shader3_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.SelectObject(hdc, brush)
        gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, PATINVERT)
        gdi32.DeleteObject(brush)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.2)

def payload7_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 0, -30, sw, sh, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, sh - 30, sw, sh, hdc, 0, 0, NOTSRCCOPY)
        gdi32.BitBlt(hdc, -30, 0, sw, sh, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, sw - 30, 0, sw, sh, hdc, 0, 0, NOTSRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def profect_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, -30, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, sw - 30, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, -30, SRCCOPY)
        gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, sh - 30, SRCCOPY)
        
        brush1 = gdi32.CreateSolidBrush(RGB(255, 255, 255))
        gdi32.SelectObject(hdc, brush1)
        gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, MERGECOPY)
        gdi32.DeleteObject(brush1)
        
        brush2 = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.SelectObject(hdc, brush2)
        gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, PATINVERT)
        gdi32.DeleteObject(brush2)
        
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def last_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, random.randint(0, 1), random.randint(0, 1), sw, sh, hdc, random.randint(0, 1), random.randint(0, 1), SRCPAINT)
        icon = user32.LoadIconW(0, ctypes.c_wchar_p(32515)) # 32515 = IDI_WARNING
        user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), icon)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def last2_thread(stop_event):
    text1 = "jwzyexgnlc.exe"
    text2 = "R.I.P PC"
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        user32.SetBkMode(hdc, 0)
        user32.SetTextColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        user32.TextOutA(hdc, random.randint(0, sw), random.randint(0, sh), text1.encode('ansi'), len(text1))
        user32.TextOutA(hdc, random.randint(0, sw), random.randint(0, sh), text2.encode('ansi'), len(text2))
        
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)


# --- Master Sequencing Loop ---

def run_sequence():
    # Standard warning prompt before commencing
    user32.MessageBoxW(
        None, 
        "This program is a harmless graphical demo.\r\nIt runs temporarily and will not change your files.", 
        "Hydrogen Master Demo", 
        0x00000030
    )
    
    stages = [
        # (Stage Name, Target Thread(s), Sound Formula, Sample Rate, Stage Duration)
        ("Shader 1 Sequence", [shader1_thread], sfx_formula_1, 16000, 30),
        ("Payload 2 Sequence", [payload2_thread], sfx_formula_2, 22050, 30),
        ("Sines wave distortion", [sines1_thread], sfx_formula_3, 22050, 30),
        ("Inversion block sequence", [shader3_thread], sfx_formula_4, 22050, 30),
        ("Multi-direction shifts", [payload7_thread], sfx_formula_5, 22050, 30),
        ("White wash & color flash", [profect_thread], sfx_formula_6, 11025, 30),
        ("Screen drift & warning draw", [last_thread], sfx_formula_7, 8000, 30),
        ("Scattering string arrays", [last2_thread], sfx_formula_8, 8000, 30),
        ("Unified Master Glitch Phase", [last_thread, last2_thread], sfx_formula_9, 8000, 30)
    ]
    
    for name, thread_funcs, audio_func, rate, duration in stages:
        print(f"[STAGE] Starting: {name}")
        
        stop_event = threading.Event()
        running_threads = []
        
        # Play synthesized audio
        play_bytebeat(audio_func, sample_rate=rate, duration=duration)
        
        # Spin up GDI threads
        for func in thread_funcs:
            t = threading.Thread(target=func, args=(stop_event,))
            t.daemon = True
            t.start()
            running_threads.append(t)
            
        time.sleep(duration)
        
        # Stop stage audio immediately
        winsound.PlaySound(None, 0)
        
        # Signal thread loop limits to exit
        stop_event.set()
        for t in running_threads:
            t.join(timeout=1.0)
            
        # Clear residual draw artifacts
        user32.InvalidateRect(0, None, True)
        time.sleep(0.1)

    print("[FINISHED] Sequence complete. Screen restored.")

if __name__ == "__main__":
    run_sequence()