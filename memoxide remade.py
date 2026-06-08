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
CUSTOM_ROP = 0x999999

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
    return ((t * (t ^ t % 9) | t >> 3) >> 1) if (t & 4096) else 255

def sfx_formula_2(t):
    t_32 = t & 0xFFFFFFFF
    part1 = (t_32 >> 17) & 1
    part2 = (2 ^ 2 & (t_32 >> 14)) // 3 if part1 else (3 & (t_32 >> 13)) + 1
    return (t_32 * (1 + (5 & (t_32 >> 10))) * (3 + part2)) >> (3 & (t_32 >> 9))

def sfx_formula_3(t):
    return sfx_formula_2(t) & sfx_formula_1(t)

def sfx_formula_4(t):
    choice = 16 if (t & 32768) else 24
    return (t >> 2) * (t & choice | t >> (t >> 8 & 24)) | t >> 3

def sfx_formula_5(t):
    choice = 6 if (t & 16384) else 5
    shift = 3 if (t & 4096) else 4
    return t * choice * (4 - (1 & t >> 8)) >> (3 & t >> 8) | t >> shift

def sfx_formula_6_fallback(t):
    return (t * (5 if (t >> 13 & 1) else 6) & t >> 8) | t >> 4

def sfx_formula_7(t):
    choice = 7 if (t & 16384) else 5
    return t * choice * (3 + (3 & t >> 14)) >> (3 & t >> 9) | (t | t * 3) >> 5

def sfx_formula_8(t):
    t_32 = t & 0xFFFFFFFF
    mult = 8 if (t_32 & 4096) else 4 if (t_32 & 2048) else 2 if (t_32 & 1024) else 1
    return (t_32 * mult) << (t_32 >> 16)

def sfx_formula_9(t):
    return (t & (t + t // 256)) - t * (t >> 15) & 64

def sfx_formula_10_fallback(t):
    return (t >> 7 | t | t >> 6) * 10 + 4

def sfx_formula_11(t):
    t_32 = t & 0xFFFFFFFF
    return t_32 * ((t_32 >> 5 | t_32) >> (t_32 >> 15))


# --- GDI Thread Definitions ---

def ran_tunnel_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.StretchBlt(hdc, 0, 0, random.randint(10, sw), random.randint(10, sh), hdc, 0, 0, sw, sh, SRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.1)

def cube_color_half_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)))
        gdi32.SelectObject(hdc, brush)
        gdi32.PatBlt(hdc, 0, 0, random.randint(0, sw), random.randint(0, sh), PATINVERT)
        gdi32.DeleteObject(brush)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def weird_invert_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 1, 1, sw, sh, hdc, 0, 0, SRCINVERT)
        gdi32.BitBlt(hdc, -1, -1, sw, sh, hdc, 0, 0, SRCINVERT)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def light_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 1, 0, sw, sh, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, -1, 0, sw, sh, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, 0, 1, sw, sh, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, SRCPAINT)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def light_dif_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 1, 0, sw, sh, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, -1, 0, sw, sh, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, 0, 1, sw, sh, hdc, 0, 0, SRCAND)
        gdi32.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, SRCAND)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def text_out_thread(stop_event):
    lp_text = "Memoxide"
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.SetBkColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.SetTextColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.TextOutA(hdc, random.randint(0, sw), random.randint(0, sh), lp_text.encode('ansi'), len(lp_text))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.02)

def move_screen_invert_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, sh - 1, sw, sh, hdc, 0, 0, NOTSRCCOPY)
        gdi32.BitBlt(hdc, -1, 0, sw, sh, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, sw - 1, 0, sw, sh, hdc, 0, 0, NOTSRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def text_out2_thread(stop_event):
    lp_text = "Destruction"
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.SetBkColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.SetTextColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.TextOutA(hdc, random.randint(0, sw), random.randint(0, sh), lp_text.encode('ansi'), len(lp_text))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def colors_half_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)))
        gdi32.SelectObject(hdc, brush)
        gdi32.PatBlt(hdc, 0, 0, sw, sh, PATINVERT)
        gdi32.DeleteObject(brush)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def weird_screen_movement_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(
            hdc, 
            random.randint(0, 10), random.randint(0, 10), 
            random.randint(0, sw), random.randint(0, sh), 
            hdc, 
            random.randint(0, 10), random.randint(0, 10), 
            SRCCOPY
        )
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def cursor_text_thread(stop_event):
    lp_text = "Hello!"
    cursor_pt = POINT()
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        user32.GetCursorPos(ctypes.byref(cursor_pt))
        gdi32.SetBkColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.SetTextColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.TextOutA(hdc, cursor_pt.x, cursor_pt.y, lp_text.encode('ansi'), len(lp_text))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def icons_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), user32.LoadIconW(0, ctypes.c_wchar_p(32513)))
        user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), user32.LoadIconW(0, ctypes.c_wchar_p(32515)))
        user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), user32.LoadIconW(0, ctypes.c_wchar_p(32512)))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def negative_invert_thread(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 1, 1, sw, sh, hdc, 0, 0, CUSTOM_ROP)
        gdi32.BitBlt(hdc, -1, -1, sw, sh, hdc, 0, 0, CUSTOM_ROP)
        gdi32.BitBlt(hdc, 1, -1, sw, sh, hdc, 0, 0, CUSTOM_ROP)
        gdi32.BitBlt(hdc, -1, 1, sw, sh, hdc, 0, 0, CUSTOM_ROP)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def redrawer_thread(stop_event):
    while not stop_event.is_set():
        user32.InvalidateRect(0, None, True)
        time.sleep(1.0)

def sines_thread(stop_event):
    angle = 0.0
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)))
        gdi32.SelectObject(hdc, brush)
        
        for i in range(0, sw + sh, 12):
            offset_x = int(math.sin(angle) * 20)
            gdi32.BitBlt(hdc, 0, i, sw, 1, hdc, offset_x, i, SRCCOPY)
            gdi32.BitBlt(hdc, 0, i, sw, 1, hdc, offset_x, i, PATINVERT)
            gdi32.BitBlt(hdc, i, 0, 1, sh, hdc, i, offset_x, SRCCOPY)
            gdi32.BitBlt(hdc, i, 0, 1, sh, hdc, i, offset_x, PATINVERT)
            angle += (math.pi / 40.0)
            
        gdi32.DeleteObject(brush)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)


# --- Demo Runner Execution ---

def run_sequence():
    print("[INFO] Running Script Version 3.0")
    
    user32.MessageBoxW(
        None, 
        "Memoxide GDI Demonstration starting.\r\nThis code performs display-only effects.", 
        "Demo Start", 
        0x00000030
    )
    
    time.sleep(5)
    
    stages = [
        ("RanTunnel", [ran_tunnel_thread], sfx_formula_1, 8000, 30),
        ("CubeColorHalf", [cube_color_half_thread], sfx_formula_2, 8000, 30),
        ("WeirdInvert", [weird_invert_thread], sfx_formula_3, 8000, 30),
        ("Light", [light_thread], sfx_formula_4, 8000, 30),
        ("LightDif", [light_dif_thread], sfx_formula_5, 8000, 30),
        ("TextOut", [text_out_thread], sfx_formula_6_fallback, 8000, 30),
        ("MoveScreenInvert", [move_screen_invert_thread], sfx_formula_7, 8000, 30),
        ("TextOut2 & ColorsHalf", [text_out2_thread, colors_half_thread], sfx_formula_8, 8000, 30),
        ("WeirdMovement & Cursor & Icons", [weird_screen_movement_thread, cursor_text_thread, icons_thread], sfx_formula_9, 8000, 30),
        ("NegativeInvert & Redrawer", [negative_invert_thread, redrawer_thread], sfx_formula_10_fallback, 8000, 30),
        ("Sines Waves", [sines_thread], sfx_formula_11, 8000, 30)
    ]
    
    for name, thread_funcs, audio_func, rate, duration in stages:
        print(f"Running: {name}")
        
        stop_event = threading.Event()
        running_threads = []
        
        play_bytebeat(audio_func, sample_rate=rate, duration=duration)
        
        for func in thread_funcs:
            t = threading.Thread(target=func, args=(stop_event,))
            t.daemon = True
            t.start()
            running_threads.append(t)
            
        time.sleep(duration)
        
        winsound.PlaySound(None, 0)
        
        stop_event.set()
        for t in running_threads:
            t.join(timeout=1.0)
            
        user32.InvalidateRect(0, None, True)
        time.sleep(0.1)

    print("Sequence completed. Output screen refreshed.")

if __name__ == "__main__":
    run_sequence()