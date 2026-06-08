import sys
import time
import math
import random
import struct
import ctypes
import threading
import winsound
from ctypes import wintypes

# --- Windows GDI & User DLL Bindings ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# GDI Raster Operation Constants
SRCCOPY = 0x00CC0020
SRCPAINT = 0x00EE0086
SRCAND = 0x008800C6
SRCINVERT = 0x00660046
NOTSRCCOPY = 0x00330008
PATINVERT = 0x005A0049
DSTINVERT = 0x00550009
MERGECOPY = 0x00C000CA
BLACKNESS = 0x00000042

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

# Get primary screen dimensions
sw = user32.GetSystemMetrics(0)
sh = user32.GetSystemMetrics(1)

# Set high-DPI compatibility
def init_dpi():
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Color helper function
def RGB(r, g, b):
    return (r & 0xFF) | ((g & 0xFF) << 8) | ((b & 0xFF) << 16)


# --- Synchronous Bytebeat Audio Generator ---

def audio_seq_1(t): return (t >> 6 | t | t >> (t >> 16)) * 10
def audio_seq_2(t): return (t * (t >> 5 | t >> 8)) >> (t >> 16 & 7)
def audio_seq_3(t): return (t & t >> 12) * (t >> 4 | t >> 8)
def audio_seq_4(t): return (t >> 7 | t | t >> 6) * 10 + 4
def audio_seq_5(t): return t * (t >> 8 * (t >> 15 | t >> 8) & (20 | 5 ^ (t >> 19) >> t | t >> 3))
def audio_seq_6(t): return (t * (5 if (t >> 13 & 1) else 6) & t >> 8) | t >> 4
def audio_seq_7(t): return (t * (7 if (t & 16384) else 5) * (3 + (3 & t >> 14)) >> (3 & t >> 9) | (t | t * 3) >> 5)
def audio_seq_8(t): return t * ((t & 1024 and (t & 2048 and (t & 4096 and 8 or 4) or 2) or 1) << (t >> 16))
def audio_seq_9(t): return (t & (t + t // 256)) - t * (t >> 15) & 64
def audio_seq_10(t): return t * ((t >> 5 | t) >> (t >> 15))

audio_formulas = [
    audio_seq_1, audio_seq_2, audio_seq_3, audio_seq_4, audio_seq_5,
    audio_seq_6, audio_seq_7, audio_seq_8, audio_seq_9, audio_seq_10
]

def play_audio(index, duration):
    sample_rate = 8000
    num_samples = sample_rate * duration
    audio_data = bytearray(num_samples)
    formula = audio_formulas[index % len(audio_formulas)]
    
    for t in range(num_samples):
        try:
            audio_data[t] = int(formula(t)) & 0xFF
        except ZeroDivisionError:
            audio_data[t] = 0
            
    header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + num_samples, b'WAVE', b'fmt ',
        16, 1, 1, sample_rate, sample_rate, 1, 8, b'data', num_samples
    )
    
    # Run synchronously in a background thread to bypass Windows memory limitations
    def play_thread():
        winsound.PlaySound(header + audio_data, winsound.SND_MEMORY)

    thread = threading.Thread(target=play_thread, daemon=True)
    thread.start()


# --- 10 Safe GDI Visual Payloads ---

def payload_1(hdc): # Vertical columns slide down
    x = random.randint(0, sw)
    gdi32.BitBlt(hdc, x, random.randint(1, 10), random.randint(50, 150), sh, hdc, x, 0, SRCCOPY)

def payload_2(hdc): # Horizontal rows slide right
    y = random.randint(0, sh)
    gdi32.BitBlt(hdc, random.randint(1, 10), y, sw, random.randint(5, 30), hdc, 0, y, SRCCOPY)

def payload_3(hdc): # Screen color flash blocks
    x, y = random.randint(0, sw - 150), random.randint(0, sh - 150)
    w, h = random.randint(50, 250), random.randint(50, 250)
    brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, x, y, w, h, PATINVERT)
    gdi32.DeleteObject(brush)

def payload_4(hdc): # Screen jitter copy
    dx = random.randint(-10, 10)
    dy = random.randint(-10, 10)
    gdi32.BitBlt(hdc, dx, dy, sw, sh, hdc, 0, 0, SRCCOPY)

def payload_5(hdc): # Scatter colored blocks
    x, y = random.randint(0, sw - 50), random.randint(0, sh - 50)
    brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, x, y, random.randint(10, 50), random.randint(10, 50), PATINVERT)
    gdi32.DeleteObject(brush)

def payload_6(hdc): # Colored lines
    pen = gdi32.CreatePen(0, random.randint(1, 5), RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SelectObject(hdc, pen)
    gdi32.MoveToEx(hdc, random.randint(0, sw), random.randint(0, sh), None)
    gdi32.LineTo(hdc, random.randint(0, sw), random.randint(0, sh))
    gdi32.DeleteObject(pen)

def payload_7(hdc): # Ellipse bounce
    brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SelectObject(hdc, brush)
    x1 = random.randint(0, sw)
    y1 = random.randint(0, sh)
    gdi32.Ellipse(hdc, x1, y1, x1 + random.randint(10, 80), y1 + random.randint(10, 80))
    gdi32.DeleteObject(brush)

def payload_8(hdc): # Block stretch zoom
    x, y = random.randint(0, sw - 150), random.randint(0, sh - 150)
    gdi32.StretchBlt(hdc, x - 5, y - 5, 160, 160, hdc, x, y, 150, 150, SRCCOPY)

def payload_9(hdc): # Draw safe warning text
    lp_text = "Safe Visual Demo"
    gdi32.SetBkColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SetTextColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.TextOutA(hdc, random.randint(0, sw), random.randint(0, sh), lp_text.encode('ansi'), len(lp_text))

def payload_10(hdc): # Spawn standard warnings icons
    user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), user32.LoadIconW(0, ctypes.c_wchar_p(32515)))


# --- 16 Safe GDI Shaders ---

def shader_1(hdc): gdi32.PatBlt(hdc, 0, 0, sw, sh, DSTINVERT)
def shader_2(hdc): gdi32.PatBlt(hdc, 0, random.randint(0, sh), sw, random.randint(1, 20), DSTINVERT)
def shader_3(hdc): # Horizontal screen sine wave
    angle = time.time() * 10
    for i in range(0, sh, 10):
        offset = int(math.sin(angle + i) * 15)
        gdi32.BitBlt(hdc, offset, i, sw, 10, hdc, 0, i, SRCCOPY)
def shader_4(hdc): # PatBlt with PATINVERT patterns
    brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, random.randint(0, sw), random.randint(0, sh), random.randint(100, 400), random.randint(100, 400), PATINVERT)
    gdi32.DeleteObject(brush)
def shader_5(hdc): # Drops columns by 5 pixels
    x = random.randint(0, sw)
    gdi32.BitBlt(hdc, x, 5, random.randint(50, 200), sh, hdc, x, 0, SRCCOPY)
def shader_6(hdc): # Color merge brush wash
    brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SelectObject(hdc, brush)
    gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, MERGECOPY)
    gdi32.DeleteObject(brush)
def shader_7(hdc): gdi32.BitBlt(hdc, random.randint(-4, 4), random.randint(-4, 4), sw, sh, hdc, 0, 0, SRCINVERT)
def shader_8(hdc): # Center crop and zoom-out
    gdi32.StretchBlt(hdc, 10, 10, sw - 20, sh - 20, hdc, 0, 0, sw, sh, SRCCOPY)
def shader_9(hdc): gdi32.BitBlt(hdc, 2, 2, sw, sh, hdc, 0, 0, SRCPAINT)
def shader_10(hdc): # Alternating interlaced offset
    for i in range(0, sh, 8):
        offset = 4 if (i % 16 == 0) else -4
        gdi32.BitBlt(hdc, offset, i, sw, 8, hdc, 0, i, SRCCOPY)
def shader_11(hdc): # Expanding center rects
    w, h = random.randint(50, 300), random.randint(50, 300)
    gdi32.PatBlt(hdc, (sw - w) // 2, (sh - h) // 2, w, h, DSTINVERT)
def shader_12(hdc): # Border rainbow flashing
    brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, 0, 0, sw, 10, PATINVERT)
    gdi32.PatBlt(hdc, 0, sh - 10, sw, 10, PATINVERT)
    gdi32.PatBlt(hdc, 0, 0, 10, sh, PATINVERT)
    gdi32.PatBlt(hdc, sw - 10, 0, 10, sh, PATINVERT)
    gdi32.DeleteObject(brush)
def shader_13(hdc): # Grid coordinate shift
    x = random.randint(0, sw - 50)
    y = random.randint(0, sh - 50)
    gdi32.BitBlt(hdc, x + random.randint(-5, 5), y + random.randint(-5, 5), 50, 50, hdc, x, y, SRCCOPY)
def shader_14(hdc): gdi32.BitBlt(hdc, -5, 0, sw, sh, hdc, 0, 0, SRCCOPY)
def shader_15(hdc): # Symmetrical horizontal drift
    gdi32.BitBlt(hdc, -3, 0, sw // 2, sh, hdc, 0, 0, SRCCOPY)
    gdi32.BitBlt(hdc, sw // 2 + 3, 0, sw // 2, sh, hdc, sw // 2, 0, SRCCOPY)
def shader_16(hdc): # Multi-size screen static blocks
    gdi32.PatBlt(hdc, random.randint(0, sw), random.randint(0, sh), random.randint(10, 100), random.randint(10, 100), DSTINVERT)


# --- Visual Execution Thread Loops ---

def run_payload_stage(payload_func, duration_sec):
    start = time.time()
    while time.time() - start < duration_sec:
        # Check if Escape key (0x1B) is pressed for emergency exit
        if user32.GetAsyncKeyState(0x1B) & 0x8000:
            return False
            
        hdc = user32.GetDC(0)
        payload_func(hdc)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)
    return True

def run_shader_stage(shader_func, duration_sec):
    start = time.time()
    while time.time() - start < duration_sec:
        if user32.GetAsyncKeyState(0x1B) & 0x8000:
            return False
            
        hdc = user32.GetDC(0)
        shader_func(hdc)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)
    return True


# --- Persistent Final Phase Threads ---

def persistent_visuals_loop(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, random.randint(-2, 2), random.randint(-2, 2), sw, sh, hdc, 0, 0, SRCINVERT)
        user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), user32.LoadIconW(0, ctypes.c_wchar_p(32515)))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.04)

def persistent_dialogs_loop(stop_event):
    while not stop_event.is_set():
        # Spawn safe non-blocking informational dialog boxes
        threading.Thread(
            target=lambda: user32.MessageBoxW(0, "Demo Stage Complete", "Hydrogen Framework", 0x00000040 | 0x00040000), 
            daemon=True
        ).start()
        time.sleep(1.0)


# --- Orchestration Engine ---

def main():
    init_dpi()
    
    # Informational Prompt
    msg_result = user32.MessageBoxW(
        0, 
        "This is a benign, safe GDI visual art demonstration.\nYour screen will draw temporary visual patterns.\n\nPress ESCAPE at any point to cancel.\nContinue?", 
        "Hydrogen Framework Demo", 
        0x00000004 | 0x00000040 | 0x00001000
    )
    if msg_result != 6: # IDYES
        sys.exit(0)

    payload_time = 5 # 5 seconds per stage
    
    payloads = [
        payload_1, payload_2, payload_3, payload_4, payload_5,
        payload_6, payload_7, payload_8, payload_9, payload_10
    ]
    
    shaders = [
        shader_1, shader_2, shader_3, shader_4, shader_5, shader_6, shader_7, shader_8,
        shader_9, shader_10, shader_11, shader_12, shader_13, shader_14, shader_15, shader_16
    ]

    print("[INFO] Starting execution sequence. Press ESC to cancel...")
    cancelled = False

    # Execute 10 payloads sequentially
    for i, p_func in enumerate(payloads):
        if cancelled:
            break
        print(f" -> Executing Payload {i+1}/10...")
        play_audio(i, payload_time)
        
        success = run_payload_stage(p_func, payload_time)
        if not success:
            cancelled = True
            
        winsound.PlaySound(None, 0)
        user32.InvalidateRect(0, None, True)
        time.sleep(0.1)

    # Execute 16 shaders sequentially
    for i, s_func in enumerate(shaders):
        if cancelled:
            break
        print(f" -> Executing Shader {i+1}/16...")
        play_audio(i + 10, payload_time)
        
        success = run_shader_stage(s_func, payload_time)
        if not success:
            cancelled = True
            
        winsound.PlaySound(None, 0)
        user32.InvalidateRect(0, None, True)
        time.sleep(0.1)

    # Run the final overlap persistent phase for 20 seconds if not cancelled
    if not cancelled:
        print(" -> Entering final concurrent phase...")
        stop_event = threading.Event()
        
        t_visuals = threading.Thread(target=persistent_visuals_loop, args=(stop_event,), daemon=True)
        t_dialogs = threading.Thread(target=persistent_dialogs_loop, args=(stop_event,), daemon=True)
        
        t_visuals.start()
        t_dialogs.start()
        
        # Poll for Escape key during the final 20 seconds
        start = time.time()
        while time.time() - start < 20.0:
            if user32.GetAsyncKeyState(0x1B) & 0x8000:
                break
            time.sleep(0.1)
            
        stop_event.set()

    # Final cleanup sequence
    winsound.PlaySound(None, 0)
    user32.InvalidateRect(0, None, True)
    print("[INFO] Execution finished. Display updated and refreshed.")

if __name__ == "__main__":
    main()