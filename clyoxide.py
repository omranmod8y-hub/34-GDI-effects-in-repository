import win32gui, win32con, win32api, win32ui
import random, time, math, ctypes, sys
import numpy as np
import sounddevice as sd

# Screen size
sw = win32api.GetSystemMetrics(0)
sh = win32api.GetSystemMetrics(1)

# --- Bytebeat player ---
def play_bytebeat(formula, duration=3, samplerate=8000):
    length = duration * samplerate
    t = np.arange(length, dtype=np.int32)
    samples = formula(t) & 255
    audio = (samples.astype(np.float32) - 128) / 128.0
    sd.play(audio, samplerate)
    sd.wait()

# Example sounds
def sound1(): play_bytebeat(lambda t: t*(t>>5|t>>8), duration=3)
def sound2(): play_bytebeat(lambda t: (t>>6|t>>8|t>>12)*10, duration=3)
def sound3(): play_bytebeat(lambda t: (t*t>>11)&t, duration=3)

# --- Payloads ---
def bubble():
    hdc = win32gui.GetDC(0)
    for _ in range(50):
        x, y = random.randint(0, sw), random.randint(0, sh)
        r = random.randint(10, 80)
        win32gui.Ellipse(hdc, x-r, y-r, x+r, y+r)
        time.sleep(0.02)
    win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)

def water():
    hdc = win32gui.GetDC(0)
    for _ in range(30):
        win32gui.StretchBlt(hdc, 0, 0, sw, sh,
                            hdc, random.randint(-10,10), random.randint(-10,10),
                            sw, sh, win32con.SRCCOPY)
        time.sleep(0.05)
    win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)

def pulse():
    hdc = win32gui.GetDC(0)
    for i in range(20):
        factor = 1 + 0.05*math.sin(i)
        win32gui.StretchBlt(hdc, 0, 0, int(sw*factor), int(sh*factor),
                            hdc, 0, 0, sw, sh, win32con.SRCCOPY)
        time.sleep(0.05)
    win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)

def tunnel():
    hdc = win32gui.GetDC(0)
    for i in range(40):
        r = int(min(sw, sh)/2 * (i/40))
        win32gui.Ellipse(hdc, sw//2-r, sh//2-r, sw//2+r, sh//2+r)
        time.sleep(0.02)
    win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)

def spiral():
    hdc = win32gui.GetDC(0)
    for i in range(200):
        angle = i * 0.1
        x = int(sw/2 + math.cos(angle)*i)
        y = int(sh/2 + math.sin(angle)*i)
        win32gui.SetPixel(hdc, x, y, win32api.RGB(255,255,255))
        time.sleep(0.01)
    win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)

def shake_fast():
    hdc = win32gui.GetDC(0)
    for _ in range(20):
        dx, dy = random.randint(-20,20), random.randint(-20,20)
        win32gui.BitBlt(hdc, dx, dy, sw, sh, hdc, 0, 0, win32con.SRCCOPY)
        time.sleep(0.05)
    win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)

def negative():
    hdc = win32gui.GetDC(0)
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, win32con.NOTSRCCOPY)
    time.sleep(0.5)
    win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)

def glitch_fast():
    hdc = win32gui.GetDC(0)
    for _ in range(30):
        sx, sy = random.randint(0, sw//2), random.randint(0, sh//2)
        dx, dy = random.randint(0, sw), random.randint(0, sh)
        win32gui.BitBlt(hdc, dx, dy, sx, sy, hdc, 0, 0, win32con.SRCCOPY)
        time.sleep(0.02)
    win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)

def scanlines():
    hdc = win32gui.GetDC(0)
    for y in range(0, sh, 4):
        win32gui.MoveToEx(hdc, 0, y)
        win32gui.LineTo(hdc, sw, y)
    time.sleep(0.5)
    win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)

def pixelate_fast():
    hdc = win32gui.GetDC(0)
    for _ in range(20):
        block = random.randint(10, 50)
        win32gui.StretchBlt(hdc, 0, 0, sw//block, sh//block,
                            hdc, 0, 0, sw, sh, win32con.SRCCOPY)
        win32gui.StretchBlt(hdc, 0, 0, sw, sh,
                            hdc, 0, 0, sw//block, sh//block, win32con.SRCCOPY)
        time.sleep(0.05)
    win32gui.ReleaseDC(win32gui.GetDesktopWindow(), hdc)

# --- Main ---
if __name__ == "__main__":
    MB_YESNO = 0x00000004
    MB_ICONEXCLAMATION = 0x00000030
    MB_SYSTEMMODAL = 0x00001000

    result = ctypes.windll.user32.MessageBoxW(
        None,
        "Warning! This program uses GDI screen effects and bytebeat audio.\nDo you want to continue?",
        "clyoxide.py (Safe Demo)",
        MB_YESNO | MB_ICONEXCLAMATION | MB_SYSTEMMODAL
    )

    if result == 7:  # IDNO
        sys.exit(0)

    # Run visuals + sounds
    bubble(); sound1()
    water(); sound2()
    pulse(); sound3()
    tunnel(); sound1()
    spiral(); sound2()
    shake_fast(); sound3()
    negative(); sound1()
    glitch_fast(); sound2()
    scanlines(); sound3()
    pixelate_fast(); sound1()
