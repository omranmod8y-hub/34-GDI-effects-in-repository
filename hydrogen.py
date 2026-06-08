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

# GDI Constants
SRCCOPY = 0x00CC0020
SRCPAINT = 0x00EE0086
SRCAND = 0x008800C6
SRCINVERT = 0x00660046
NOTSRCCOPY = 0x00330008
PATINVERT = 0x005A0049
DSTINVERT = 0x00550009
BLACKNESS = 0x00000042
WHITENESS = 0x00FF0062

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

# Get screen metrics
sw = user32.GetSystemMetrics(0)
sh = user32.GetSystemMetrics(1)

# Set DPI Awareness
def init_dpi():
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Helper to generate the Windows COLORREF integer
def RGB(r, g, b):
    return (r & 0xFF) | ((g & 0xFF) << 8) | ((b & 0xFF) << 16)


# --- Background Audio (Bytebeat Progression) ---

def audio_seq_1(t): return (t >> 6 | t | t >> (t >> 16)) * 10
def audio_seq_2(t): return (t * (t >> 5 | t >> 8)) >> (t >> 16 & 7)
def audio_seq_3(t): return (t & t >> 12) * (t >> 4 | t >> 8)
def audio_seq_4(t): return (t >> 7 | t | t >> 6) * 10 + 4
def audio_seq_5(t): return t * (t >> 8 * (t >> 15 | t >> 8) & (20 | 5 ^ (t >> 19) >> t | t >> 3))
def audio_seq_6(t): return (t * (5 if (t >> 13 & 1) else 6) & t >> 8) | t >> 4
def audio_seq_7(t): return (t * (t & 16384 and 7 or 5) * (3 + (3 & t >> 14)) >> (3 & t >> 9) | (t | t * 3) >> 5)
def audio_seq_8(t): return t * ((t & 1024 and (t & 2048 and (t & 4096 and 8 or 4) or 2) or 1) << (t >> 16))
def audio_seq_9(t): return (t & (t + t // 256)) - t * (t >> 15) & 64
def audio_seq_10(t): return t * ((t >> 5 | t) >> (t >> 15))

audio_sequences = [
    audio_seq_1, audio_seq_2, audio_seq_3, audio_seq_4, audio_seq_5,
    audio_seq_6, audio_seq_7, audio_seq_8, audio_seq_9, audio_seq_10
]

def play_audio_sequence(index, duration_sec):
    sample_rate = 8000
    num_samples = sample_rate * duration_sec
    audio_data = bytearray(num_samples)
    formula = audio_sequences[index % len(audio_sequences)]
    
    for t in range(num_samples):
        try:
            audio_data[t] = int(formula(t)) & 0xFF
        except Exception:
            audio_data[t] = 0
            
    header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + num_samples, b'WAVE', b'fmt ',
        16, 1, 1, sample_rate, sample_rate, 1, 8, b'data', num_samples
    )
    
    # Non-blocking async audio buffer playback
    winsound.PlaySound(header + audio_data, winsound.SND_MEMORY | winsound.SND_ASYNC)


# --- 10 GDI Payloads ---

def payload_1(hdc): # Screen melt drift
    x = random.randint(0, sw)
    gdi32.BitBlt(hdc, x, random.randint(1, 10), random.randint(50, 200), sh, hdc, x, 0, SRCCOPY)

def payload_2(hdc): # Horizontal lines drift
    y = random.randint(0, sh)
    gdi32.BitBlt(hdc, random.randint(1, 10), y, sw, random.randint(5, 50), hdc, 0, y, SRCCOPY)

def payload_3(hdc): # Screen color flash blocks
    x, y = random.randint(0, sw - 150), random.randint(0, sh - 150)
    w, h = random.randint(50, 300), random.randint(50, 300)
    brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SelectObject(hdc, brush)
    gdi32.PatBlt(hdc, x, y, w, h, PATINVERT)
    gdi32.DeleteObject(brush)

def payload_4(hdc): # Block copy inversion
    x, y = random.randint(0, sw - 100), random.randint(0, sh - 100)
    gdi32.BitBlt(hdc, x, y, 100, 100, hdc, x + random.randint(-10, 10), y + random.randint(-10, 10), SRCINVERT)

def payload_5(hdc): # Shift up-down mirror
    gdi32.BitBlt(hdc, 0, -2, sw, sh, hdc, 0, 0, SRCCOPY)
    gdi32.BitBlt(hdc, 0, sh - 2, sw, sh, hdc, 0, 0, NOTSRCCOPY)

def payload_6(hdc): # Shift left-right mirror
    gdi32.BitBlt(hdc, -2, 0, sw, sh, hdc, 0, 0, SRCCOPY)
    gdi32.BitBlt(hdc, sw - 2, 0, sw, sh, hdc, 0, 0, NOTSRCCOPY)

def payload_7(hdc): # Sines distortion
    angle = time.time() * 5
    for i in range(0, sh, 15):
        offset = int(math.sin(angle + i) * 10)
        gdi32.BitBlt(hdc, offset, i, sw, 15, hdc, 0, i, SRCCOPY)

def payload_8(hdc): # Random block stretch zoom
    x, y = random.randint(0, sw - 200), random.randint(0, sh - 200)
    gdi32.StretchBlt(hdc, x - 10, y - 10, 220, 220, hdc, x, y, 200, 200, SRCCOPY)

def payload_9(hdc): # Text scattering
    lp_text = "Hydrogen"
    gdi32.SetBkColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SetTextColor(hdc, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    user32.TextOutA(hdc, random.randint(0, sw), random.randint(0, sh), lp_text.encode('ansi'), len(lp_text))

def payload_10(hdc): # Draw error warning icons
    user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), user32.LoadIconW(0, ctypes.c_wchar_p(32515)))


# --- 16 Visual Shaders ---

def shader_1(hdc): gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, DSTINVERT)
def shader_2(hdc): gdi32.BitBlt(hdc, 1, 1, sw, sh, hdc, -1, -1, SRCPAINT)
def shader_3(hdc): gdi32.BitBlt(hdc, -1, -1, sw, sh, hdc, 1, 1, SRCAND)
def shader_4(hdc): # Quick screen pixel invert blocks
    gdi32.PatBlt(hdc, random.randint(0, sw), random.randint(0, sh), random.randint(50, 400), random.randint(50, 400), PATINVERT)
def shader_5(hdc): gdi32.BitBlt(hdc, random.randint(-5, 5), random.randint(-5, 5), sw, sh, hdc, 0, 0, SRCCOPY)
def shader_6(hdc): gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, SRCINVERT)
def shader_7(hdc): # Horizontal lines flash
    gdi32.PatBlt(hdc, 0, random.randint(0, sh), sw, random.randint(10, 100), DSTINVERT)
def shader_8(hdc): # Screen expand/contract
    gdi32.StretchBlt(hdc, 5, 5, sw - 10, sh - 10, hdc, 0, 0, sw, sh, SRCCOPY)
def shader_9(hdc): # Diagonal drift lines
    gdi32.BitBlt(hdc, 2, 2, sw, sh, hdc, 0, 0, SRCCOPY)
def shader_10(hdc): # Alternate diagonal drift
    gdi32.BitBlt(hdc, -2, 2, sw, sh, hdc, 0, 0, SRCPAINT)
def shader_11(hdc): # Color merge brush flash
    brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    gdi32.SelectObject(hdc, brush)
    gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, MERGECOPY)
    gdi32.DeleteObject(brush)
def shader_12(hdc): gdi32.BitBlt(hdc, 2, 0, sw, sh, hdc, -2, 0, SRCPAINT)
def shader_13(hdc): gdi32.BitBlt(hdc, 0, 2, sw, sh, hdc, 0, -2, SRCAND)
def shader_14(hdc): # Fullscreen invert flash
    gdi32.PatBlt(hdc, 0, 0, sw, sh, DSTINVERT)
def shader_15(hdc): # Interlaced scanline shift
    for i in range(0, sh, 4):
        gdi32.BitBlt(hdc, random.randint(-2, 2), i, sw, 2, hdc, 0, i, SRCCOPY)
def shader_16(hdc): # Final overlay visual noise
    gdi32.BitBlt(hdc, random.randint(-4, 4), random.randint(-4, 4), sw, sh, hdc, random.randint(-4, 4), random.randint(-4, 4), SRCINVERT)


# --- Visual Execution Controllers ---

def run_payload(payload_func, duration_sec):
    start_time = time.time()
    while time.time() - start_time < duration_sec:
        hdc = user32.GetDC(0)
        payload_func(hdc)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01) # CPU usage safety yield

def run_shader(shader_func, duration_sec):
    start_time = time.time()
    while time.time() - start_time < duration_sec:
        hdc = user32.GetDC(0)
        shader_func(hdc)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)


# --- Final Stage Glitch Threads ---

def windows_corruption_loop(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        # Shift random blocks around
        gdi32.BitBlt(hdc, random.randint(-5, 5), random.randint(-5, 5), sw, sh, hdc, 0, 0, SRCINVERT)
        # Draw warnings on top
        user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), user32.LoadIconW(0, ctypes.c_wchar_p(32513)))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.05)

def message_box_loop(stop_event):
    # Safe non-blocking visual simulation of pop-up warning dialogues
    while not stop_event.is_set():
        threading.Thread(
            target=lambda: user32.MessageBoxW(0, "System Glitch Emulation", "Hydrogen.exe", 0x00000030 | 0x00040000), 
            daemon=True
        ).start()
        time.sleep(1.0)


# --- Main Application Controller ---

def main():
    init_dpi()
    
    # 1. Warning Dialogs
    msg_result = user32.MessageBoxW(
        0, 
        "What you have just executed is a malware mockup.\nYour display will flicker. No data will be harmed.\nContinue?", 
        "Hydrogen.exe", 
        0x00000004 | 0x00000100 | 0x00001000
    )
    if msg_result != 6: # IDYES
        sys.exit(0)

    msg_result = user32.MessageBoxW(
        0, 
        "THIS IS THE LAST WARNING!\nThe execution contains flash properties. Close the terminal to force exit.\nStill continue?", 
        "Hydrogen.exe - LAST WARNING", 
        0x00000004 | 0x00000100 | 0x00001000
    )
    if msg_result != 6: # IDYES
        sys.exit(0)

    payload_time_seconds = 10 # 10 seconds per stage
    
    # Background sound synthesizer thread manager
    def audio_orchestrator():
        for i in range(10):
            play_audio_sequence(i, payload_time_seconds)
            time.sleep(payload_time_seconds)
            
    audio_thread = threading.Thread(target=audio_orchestrator, daemon=True)
    audio_thread.start()

    # 2. Run 10 GDI Payloads
    payloads = [
        payload_1, payload_2, payload_3, payload_4, payload_5,
        payload_6, payload_7, payload_8, payload_9, payload_10
    ]
    for i, p_func in enumerate(payloads):
        print(f"[INFO] Executing Payload {i+1}/10...")
        run_payload(p_func, payload_time_seconds)
        user32.InvalidateRect(0, None, True)

    # 3. Run 16 Shaders
    shaders = [
        shader_1, shader_2, shader_3, shader_4, shader_5, shader_6, shader_7, shader_8,
        shader_9, shader_10, shader_11, shader_12, shader_13, shader_14, shader_15, shader_16
    ]
    for i, s_func in enumerate(shaders):
        print(f"[INFO] Executing Shader {i+1}/16...")
        run_shader(s_func, payload_time_seconds)
        user32.InvalidateRect(0, None, True)

    # 4. Spawns final corruption and dialog loops for 20 seconds
    print("[INFO] Starting final stage...")
    stop_event = threading.Event()
    
    t_corrupt = threading.Thread(target=windows_corruption_loop, args=(stop_event,), daemon=True)
    t_msgbox = threading.Thread(target=message_box_loop, args=(stop_event,), daemon=True)
    
    t_corrupt.start()
    t_msgbox.start()
    
    time.sleep(20.0)
    
    stop_event.set()
    winsound.PlaySound(None, 0)
    user32.InvalidateRect(0, None, True)
    print("[INFO] Demo finished safely. Display outputs refreshed.")

if __name__ == "__main__":
    import sys
    main()