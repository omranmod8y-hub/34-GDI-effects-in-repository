import ctypes
import ctypes.wintypes as wintypes
import time
import math
import random
import threading

# --- Windows API Constants ---
SRCCOPY = 0x00CC0020
NOTSRCCOPY = 0x00330008
PATINVERT = 0x005A0049
SRCPAINT = 0x00EE0086
MERGECOPY = 0x00C000CA
SM_CXSCREEN = 0
SM_CYSCREEN = 1
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04
WAVE_FORMAT_PCM = 1

# --- Load DLLs ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
winmm = ctypes.windll.winmm
kernel32 = ctypes.windll.kernel32

# --- Structures ---
class RGBQUAD(ctypes.Structure):
    _fields_ = [("rgbBlue", wintypes.BYTE),
                ("rgbGreen", wintypes.BYTE),
                ("rgbRed", wintypes.BYTE),
                ("rgbReserved", wintypes.BYTE)]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wintypes.DWORD),
                ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG),
                ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD)]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER),
                ("bmiColors", RGBQUAD * 1)]

class WAVEFORMATEX(ctypes.Structure):
    _fields_ = [("wFormatTag", wintypes.WORD),
                ("nChannels", wintypes.WORD),
                ("nSamplesPerSec", wintypes.DWORD),
                ("nAvgBytesPerSec", wintypes.DWORD),
                ("nBlockAlign", wintypes.WORD),
                ("wBitsPerSample", wintypes.WORD),
                ("cbSize", wintypes.WORD)]

class WAVEHDR(ctypes.Structure):
    _fields_ = [("lpData", ctypes.c_char_p),
                ("dwBufferLength", wintypes.DWORD),
                ("dwBytesRecorded", wintypes.DWORD),
                ("dwUser", ctypes.c_void_p),
                ("dwFlags", wintypes.DWORD),
                ("dwLoops", wintypes.DWORD),
                ("lpNext", ctypes.c_void_p),
                ("reserved", ctypes.c_void_p)]

# --- Helper Functions ---
def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

stop_event = threading.Event()

# --- Visual Payloads ---

def payload_shader1():
    w, h = get_screen_size()
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, random.randint(-10, 10), random.randint(-10, 10), w, h, hdc, 0, 0, SRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def payload_stretch():
    w, h = get_screen_size()
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.StretchBlt(hdc, 10, 10, w - 20, h - 20, hdc, 0, 0, w, h, 0x9273ecef)
        gdi32.StretchBlt(hdc, -10, -10, w + 20, h + 20, hdc, 0, 0, w, h, 0x9273ecef)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.05)

def payload_sines():
    w, h = get_screen_size()
    angle = 0
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        for i in range(0, w + h, 2):
            a = int(math.sin(angle) * 20)
            gdi32.BitBlt(hdc, 0, i, w, 1, hdc, a, i, SRCCOPY)
            gdi32.BitBlt(hdc, i, 0, 1, h, hdc, i, a, SRCCOPY)
            angle += 0.1
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def payload_invert_move():
    w, h = get_screen_size()
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 0, -30, w, h, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, h-30, w, h, hdc, 0, 0, NOTSRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def payload_last():
    w, h = get_screen_size()
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, random.randint(0, 2), random.randint(0, 2), w, h, hdc, random.randint(0, 2), random.randint(0, 2), SRCPAINT)
        # Draw some icons
        user32.DrawIcon(hdc, random.randint(0, w), random.randint(0, h), user32.LoadCursorW(0, 32512)) # IDC_ARROW
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

# --- Audio Payloads (ByteBeat) ---

def play_bytebeat(func, samplerate=8000, duration=30):
    hWaveOut = wintypes.HANDLE()
    wfx = WAVEFORMATEX(WAVE_FORMAT_PCM, 1, samplerate, samplerate, 1, 8, 0)
    
    if winmm.waveOutOpen(ctypes.byref(hWaveOut), 0xFFFFFFFF, ctypes.byref(wfx), 0, 0, 0) != 0:
        return

    buffer_size = samplerate * duration
    raw_data = bytearray(buffer_size)
    
    for t in range(buffer_size):
        raw_data[t] = func(t) & 0xFF
        
    buf = ctypes.create_string_buffer(bytes(raw_data))
    header = WAVEHDR(ctypes.cast(buf, ctypes.c_char_p), buffer_size, 0, 0, 0, 0, 0, 0)
    
    winmm.waveOutPrepareHeader(hWaveOut, ctypes.byref(header), ctypes.sizeof(WAVEHDR))
    winmm.waveOutWrite(hWaveOut, ctypes.byref(header), ctypes.sizeof(WAVEHDR))
    
    time.sleep(duration)
    
    winmm.waveOutUnprepareHeader(hWaveOut, ctypes.byref(header), ctypes.sizeof(WAVEHDR))
    winmm.waveOutClose(hWaveOut)

# --- Sound Formulas ---
def sound1(t): return (3 * (t >> 6 | t | t >> (t >> 16)) + (7 & t >> 11) * t)
def sound3(t): return (t & t >> 12) * (t >> 4 | t >> 8)
def sound7(t): return (t >> (t >> 12) % 4) + t * (1 + (1 + (t >> 16) % 6) * (t >> 10) * (t >> 11) % 8) ^ t >> 13 ^ t >> 6

# --- Main Orchestrator ---

def main():
    # Message Boxes
    ret = user32.MessageBoxW(0, "This is a GDI Only, Run?", "jwzyexgnlc.py", 0x30 | 0x4)
    if ret != 6: # IDYES
        return
    
    ret = user32.MessageBoxW(0, "Are you sure? Flashing lights warning.", "Last Warning", 0x30 | 0x4)
    if ret != 6:
        return

    # Payload 1
    stop_event.clear()
    t = threading.Thread(target=payload_shader1, daemon=True)
    t.start()
    play_bytebeat(sound1, samplerate=16000, duration=10)
    stop_event.set()
    user32.InvalidateRect(0, 0, 1)

    # Payload 2
    stop_event.clear()
    t = threading.Thread(target=payload_stretch, daemon=True)
    t.start()
    play_bytebeat(sound3, samplerate=22050, duration=10)
    stop_event.set()
    user32.InvalidateRect(0, 0, 1)

    # Payload 3
    stop_event.clear()
    t = threading.Thread(target=payload_sines, daemon=True)
    t.start()
    play_bytebeat(sound7, samplerate=8000, duration=10)
    stop_event.set()
    user32.InvalidateRect(0, 0, 1)

    # Final Payload
    stop_event.clear()
    threading.Thread(target=payload_last, daemon=True).start()
    play_bytebeat(lambda t: t * (t >> 8 * (t >> 15 | t >> 8) & (20 | 5 ^ (t >> 19) >> t | t >> 3)), duration=10)
    
    print("Done.")

if __name__ == "__main__":
    main()