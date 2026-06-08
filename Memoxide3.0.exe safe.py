import win32gui
import win32con
import win32api
import win32ui
import winsound
import threading
import random
import time
import math

# Example: RanTunnel effect
def ran_tunnel():
    hdc = win32gui.GetDC(0)
    sw = win32api.GetSystemMetrics(0)
    sh = win32api.GetSystemMetrics(1)
    while True:
        hdc = win32gui.GetDC(0)
        win32gui.StretchBlt(hdc, 0, 0, random.randint(0, sw), random.randint(0, sh),
                            hdc, 0, 0, sw, sh, win32con.SRCCOPY)
        win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)
        time.sleep(0.1)

# Example: TextOut effect
def text_out():
    hdc = win32gui.GetDC(0)
    sx = win32api.GetSystemMetrics(0)
    sy = win32api.GetSystemMetrics(1)
    text = "Memoxide"
    while True:
        hdc = win32gui.GetDC(0)
        win32gui.SetBkColor(hdc, win32api.RGB(random.randint(0,255),
                                              random.randint(0,255),
                                              random.randint(0,255)))
        win32gui.SetTextColor(hdc, win32api.RGB(random.randint(0,255),
                                                random.randint(0,255),
                                                random.randint(0,255)))
        win32gui.TextOut(hdc, random.randint(0, sx), random.randint(0, sy), text)
        win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)
        time.sleep(0.05)

# Example: Sound effect
def sound1():
    # Simple beep as placeholder
    winsound.Beep(800, 500)  # frequency, duration
    # For complex waveforms, you’d need numpy + sounddevice or waveOut APIs

# Thread runner
def run_effect(effect_func, duration=10):
    t = threading.Thread(target=effect_func)
    t.start()
    time.sleep(duration)
    # Threads in Python can’t be forcefully killed like TerminateThread in C++
    # You’d need a stop flag to exit gracefully

if __name__ == "__main__":
    # Warning dialogs can be simulated with ctypes MessageBox
    import ctypes
    MB_YESNO = 0x00000004
    MB_ICONEXCLAMATION = 0x00000030
    MB_SYSTEMMODAL = 0x00001000

    result = ctypes.windll.user32.MessageBoxW(
        None, "Warning! This software is GDI Only.\nAre you sure you want to run it?",
        "Memoxide.py (safety version)", MB_YESNO | MB_ICONEXCLAMATION | MB_SYSTEMMODAL)

    if result == 7:  # IDNO
        exit(0)

    run_effect(ran_tunnel, 5)
    sound1()
    run_effect(text_out, 5)
