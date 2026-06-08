import win32gui
import win32api
import win32con
import random
import math
import time
import threading
import ctypes

# Get Screen Dimensions
sw = win32api.GetSystemMetrics(0)
sh = win32api.GetSystemMetrics(1)

def redraw_screen():
    """Forces the screen to clear/refresh."""
    win32gui.InvalidateRect(0, None, True)

# --- GDI EFFECT FUNCTIONS ---

def ran_tunnel():
    hdc = win32gui.GetDC(0)
    while True:
        win32gui.StretchBlt(hdc, 0, 0, random.randint(0, sw), random.randint(0, sh), hdc, 0, 0, sw, sh, win32con.SRCCOPY)
        time.sleep(0.1)

def cube_color_half():
    while True:
        hdc = win32gui.GetDC(0)
        brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)))
        win32gui.SelectObject(hdc, brush)
        win32gui.PatBlt(hdc, 0, 0, random.randint(0, sw), random.randint(0, sh), win32con.PATINVERT)
        win32gui.DeleteObject(brush)
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.01)

def weird_invert():
    hdc = win32gui.GetDC(0)
    while True:
        win32gui.BitBlt(hdc, 1, 1, sw, sh, hdc, 0, 0, win32con.SRCINVERT)
        win32gui.BitBlt(hdc, -1, -1, sw, sh, hdc, 0, 0, win32con.SRCINVERT)
        time.sleep(0.01)

def light():
    hdc = win32gui.GetDC(0)
    while True:
        win32gui.BitBlt(hdc, 1, 0, sw, sh, hdc, 0, 0, win32con.SRCPAINT)
        win32gui.BitBlt(hdc, -1, 0, sw, sh, hdc, 0, 0, win32con.SRCPAINT)
        win32gui.BitBlt(hdc, 0, 1, sw, sh, hdc, 0, 0, win32con.SRCPAINT)
        win32gui.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, win32con.SRCPAINT)
        time.sleep(0.01)

def text_out():
    text = "Memoxide"
    while True:
        hdc = win32gui.GetDC(0)
        win32gui.SetBkColor(hdc, win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        win32gui.SetTextColor(hdc, win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        win32gui.TextOut(hdc, random.randint(0, sw), random.randint(0, sh), text)
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.05)

def move_screen_invert():
    hdc = win32gui.GetDC(0)
    while True:
        win32gui.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, win32con.SRCCOPY)
        win32gui.BitBlt(hdc, 0, sh - 1, sw, sh, hdc, 0, 0, win32con.NOTSRCCOPY)
        win32gui.BitBlt(hdc, -1, 0, sw, sh, hdc, 0, 0, win32con.SRCCOPY)
        win32gui.BitBlt(hdc, sw - 1, 0, sw, sh, hdc, 0, 0, win32con.NOTSRCCOPY)
        time.sleep(0.01)

def sines_effect():
    angle = 0
    while True:
        hdc = win32gui.GetDC(0)
        brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)))
        win32gui.SelectObject(hdc, brush)
        for i in range(0, sw + sh, 4): # Step of 4 for better performance in Python
            a = int(math.sin(angle) * 20)
            win32gui.BitBlt(hdc, 0, i, sw, 1, hdc, a, i, win32con.SRCCOPY)
            win32gui.BitBlt(hdc, 0, i, sw, 1, hdc, a, i, win32con.PATINVERT)
            angle += math.pi / 40
        win32gui.DeleteObject(brush)
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.01)

def draw_icons():
    while True:
        hdc = win32gui.GetDC(0)
        # Load standard system icons
        error_icon = win32gui.LoadIcon(0, win32con.IDI_ERROR)
        warn_icon = win32gui.LoadIcon(0, win32con.IDI_WARNING)
        
        win32gui.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), error_icon)
        win32gui.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), warn_icon)
        
        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.1)

# --- EXECUTION LOGIC ---

def run_effect(effect_func, duration):
    """Runs a function in a thread, waits, then stops it indirectly."""
    stop_event = threading.Event()
    
    def wrapper():
        while not stop_event.is_set():
            effect_func()
            
    # For simplicity in this demo, we use a slightly more direct approach:
    t = threading.Thread(target=effect_func, daemon=True)
    t.start()
    time.sleep(duration)
    # Python threads can't be 'terminated' forcefully like Win32 threads easily
    # so we just let the sequence move on or clear the screen.
    redraw_screen()

def main():
    # Warning Messages
    resp = ctypes.windll.user32.MessageBoxW(0, "Warning! This software is GDI Only.\nAre you sure you want to run it?", "Python Memoxide (Safe)", 0x00000004 | 0x00000030 | 0x00001000)
    if resp != 6: # 6 is 'Yes'
        return

    resp2 = ctypes.windll.user32.MessageBoxW(0, "It will not damage your computer.\nStill run it?", "LAST WARNING", 0x00000004 | 0x00000030 | 0x00001000)
    if resp2 != 6:
        return

    time.sleep(2)

    # Sequence of effects
    effects = [
        (ran_tunnel, 10),
        (cube_color_half, 10),
        (weird_invert, 10),
        (light, 10),
        (text_out, 10),
        (move_screen_invert, 10),
        (draw_icons, 10),
        (sines_effect, 15)
    ]

    for func, duration in effects:
        print(f"Running {func.__name__}...")
        # Since these loops are 'while True', we launch as daemon and sleep
        t = threading.Thread(target=func, daemon=True)
        t.start()
        time.sleep(duration)
        redraw_screen()
        time.sleep(0.1)

    redraw_screen()
    ctypes.windll.user32.MessageBoxW(0, "GDI Sequence Finished.", "Done", 0x40)

if __name__ == "__main__":
    main()