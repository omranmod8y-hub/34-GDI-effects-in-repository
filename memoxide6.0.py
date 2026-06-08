import win32gui, win32api, win32con, win32ui
import time, random, math, threading, ctypes
from ctypes import wintypes

# --- SETUP ---
winmm = ctypes.WinDLL('winmm')
gdi32 = ctypes.WinDLL('gdi32')
sw = win32api.GetSystemMetrics(0)
sh = win32api.GetSystemMetrics(1)

# Audio engine structures
class WAVEFORMATEX(ctypes.Structure):
    _fields_ = [("wFormatTag", wintypes.WORD), ("nChannels", wintypes.WORD), ("nSamplesPerSec", wintypes.DWORD), 
                ("nAvgBytesPerSec", wintypes.DWORD), ("nBlockAlign", wintypes.WORD), ("wBitsPerSample", wintypes.WORD), ("cbSize", wintypes.WORD)]
class WAVEHDR(ctypes.Structure):
    _fields_ = [("lpData", ctypes.c_char_p), ("dwBufferLength", wintypes.DWORD), ("dwBytesRecorded", wintypes.DWORD), 
                ("dwUser", wintypes.DWORD), ("dwFlags", wintypes.DWORD), ("dwLoops", wintypes.DWORD), ("lpNext", ctypes.c_void_p), ("reserved", wintypes.DWORD)]

def play_sound(formula, seconds=30):
    sample_rate = 8000
    buf = bytearray(sample_rate * seconds)
    for t in range(len(buf)):
        try: buf[t] = formula(t) & 0xff
        except: buf[t] = 0
    wfx = WAVEFORMATEX(1, 1, sample_rate, sample_rate, 1, 8, 0)
    hwo = wintypes.HANDLE()
    winmm.waveOutOpen(ctypes.byref(hwo), 0xFFFF, ctypes.byref(wfx), 0, 0, 0)
    raw = ctypes.create_string_buffer(bytes(buf))
    whdr = WAVEHDR(ctypes.cast(raw, ctypes.c_char_p), len(buf), 0, 0, 0, 0, None, 0)
    winmm.waveOutPrepareHeader(hwo, ctypes.byref(whdr), ctypes.sizeof(WAVEHDR))
    winmm.waveOutWrite(hwo, ctypes.byref(whdr), ctypes.sizeof(WAVEHDR))
    return hwo

# --- GDI PAYLOADS ---

def ran_tunnel(stop):
    while not stop.is_set():
        hdc = win32gui.GetDC(0)
        win32gui.StretchBlt(hdc, 0, 0, random.randint(0, sw), random.randint(0, sh), hdc, 0, 0, sw, sh, win32con.SRCCOPY)
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.1)

def cube_color(stop):
    while not stop.is_set():
        hdc = win32gui.GetDC(0)
        brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)))
        win32gui.SelectObject(hdc, brush)
        win32gui.PatBlt(hdc, 0, 0, random.randint(0, sw), random.randint(0, sh), win32con.PATINVERT)
        win32gui.DeleteObject(brush)
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.01)

def light_effect(stop, mode="paint"):
    while not stop.is_set():
        hdc = win32gui.GetDC(0)
        m = win32con.SRCPAINT if mode == "paint" else win32con.SRCAND
        win32gui.BitBlt(hdc, 1, 0, sw, sh, hdc, 0, 0, m)
        win32gui.BitBlt(hdc, -1, 0, sw, sh, hdc, 0, 0, m)
        win32gui.BitBlt(hdc, 0, 1, sw, sh, hdc, 0, 0, m)
        win32gui.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, m)
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.01)

def text_payload(stop, msg="Memoxide"):
    while not stop.is_set():
        hdc = win32gui.GetDC(0)
        win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
        win32gui.SetTextColor(hdc, win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        # FIX: win32gui uses ExtTextOut, not TextOut
        win32gui.ExtTextOut(hdc, random.randint(0, sw), random.randint(0, sh), 0, None, msg)
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.05)

def cursor_text(stop):
    while not stop.is_set():
        hdc = win32gui.GetDC(0)
        x, y = win32api.GetCursorPos()
        win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
        win32gui.SetTextColor(hdc, win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        # FIX: win32gui uses ExtTextOut, not TextOut
        win32gui.ExtTextOut(hdc, x, y, 0, None, "Hello!")
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.01)

def icon_spam(stop):
    icons = [win32gui.LoadIcon(0, win32con.IDI_ERROR), win32gui.LoadIcon(0, win32con.IDI_WARNING), win32gui.LoadIcon(0, win32con.IDI_APPLICATION)]
    while not stop.is_set():
        hdc = win32gui.GetDC(0)
        win32gui.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), random.choice(icons))
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.05)

def move_invert(stop):
    while not stop.is_set():
        hdc = win32gui.GetDC(0)
        win32gui.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, win32con.SRCCOPY)
        win32gui.BitBlt(hdc, 0, sh - 1, sw, sh, hdc, 0, 0, win32con.NOTSRCCOPY)
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.01)

def sines(stop):
    angle = 0
    while not stop.is_set():
        hdc = win32gui.GetDC(0)
        for i in range(0, sw + sh, 15): # Increased step for performance
            a = int(math.sin(angle) * 20)
            win32gui.BitBlt(hdc, 0, i, sw, 1, hdc, a, i, win32con.SRCCOPY)
            win32gui.BitBlt(hdc, i, 0, 1, sh, hdc, i, a, win32con.SRCCOPY)
            angle += math.pi / 100
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.01)

# --- BYTEBEAT FORMULAS ---
def s1(t): return (t & 4096 and (t * (t ^ t % 9) | t >> 3) >> 1 or 255)
def s2(t): return t * (1 + (5 & t >> 10)) * (3 + (t >> 17 & 1 and (2 ^ 2 & t >> 14) // 3 or 3 & (t >> 13) + 1)) >> (3 & t >> 9)
def s4(t): return (t >> 2) * (t & (t & 32768 and 16 or 24) | t >> (t >> 8 & 24)) | t >> 3
def s7(t): return t * (t & 16384 and 7 or 5) * (3 + (3 & t >> 14)) >> (3 & t >> 9) | (t | t * 3) >> 5
def s11(t): return t * ((t >> 5 | t) >> (t >> 15))

# --- CONTROLLER ---
def run_phase(visual_funcs, audio_func, duration):
    stop = threading.Event()
    h_audio = play_sound(audio_func, duration)
    threads = []
    for f in visual_funcs:
        t = threading.Thread(target=f, args=(stop,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    stop.set()
    winmm.waveOutReset(h_audio)
    win32gui.InvalidateRect(0, None, True) # Clean the screen
    time.sleep(0.5)

def main():
    if win32gui.MessageBox(0, "Run GDI Payload Test?", "Python Memoxide", win32con.MB_YESNO | win32con.MB_ICONWARNING) != win32con.IDYES:
        return
    
    time.sleep(1)
    
    # 1. Tunnel
    run_phase([ran_tunnel], s1, 10)
    # 2. Colors
    run_phase([cube_color], s2, 10)
    # 3. Light + Move
    run_phase([light_effect, move_invert], s4, 10)
    # 4. Text + Icons
    run_phase([text_payload, icon_spam, cursor_text], s7, 10)
    # 5. Sines (Final)
    run_phase([sines], s11, 15)

    win32gui.InvalidateRect(0, None, True)
    win32gui.MessageBox(0, "Test Finished.", "Python GDI", 64)

if __name__ == "__main__":
    main()