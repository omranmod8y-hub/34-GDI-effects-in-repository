import win32gui
import win32api
import win32con
import math
import random
import time
import threading
import tkinter as tk
from tkinter import ttk

# Global Configuration
sw = win32api.GetSystemMetrics(0)
sh = win32api.GetSystemMetrics(1)
running = False
current_effect = None

def get_hdc():
    return win32gui.GetDC(0)

class GDIEffects:
    @staticmethod
    def dark():
        hdc = get_hdc()
        while running:
            win32gui.PatBlt(hdc, 0, 0, sw, sh, win32con.BLACKNESS)
            time.sleep(0.1)

    @staticmethod
    def cursors():
        while running:
            x, y = random.randint(0, sw), random.randint(0, sh)
            win32gui.DrawIcon(get_hdc(), x, y, win32gui.LoadIcon(0, win32con.IDI_APPLICATION))
            time.sleep(0.01)

    @staticmethod
    def rgb_circle():
        hdc = get_hdc()
        while running:
            brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
            win32gui.SelectObject(hdc, brush)
            x, y = random.randint(0, sw), random.randint(0, sh)
            size = random.randint(50, 200)
            win32gui.Ellipse(hdc, x, y, x+size, y+size)
            time.sleep(0.05)

    @staticmethod
    def icon_wave():
        hdc = get_hdc()
        t = 0
        icon = win32gui.LoadIcon(0, win32con.IDI_WARNING)
        while running:
            for x in range(0, sw, 60):
                y = int(sh/2 + math.sin(t + x/100) * 200)
                win32gui.DrawIcon(hdc, x, y, icon)
            t += 0.1
            time.sleep(0.02)

    @staticmethod
    def sinewave():
        hdc = get_hdc()
        while running:
            for i in range(sh):
                offset = int(math.sin(i/20.0) * 10)
                win32gui.BitBlt(hdc, offset, i, sw, 1, hdc, 0, i, win32con.SRCCOPY)
            time.sleep(0.01)

    @staticmethod
    def shake():
        hdc = get_hdc()
        while running:
            win32gui.BitBlt(hdc, random.randint(-10, 10), random.randint(-10, 10), sw, sh, hdc, 0, 0, win32con.SRCCOPY)
            time.sleep(0.01)

    @staticmethod
    def melter():
        hdc = get_hdc()
        while running:
            x = random.randint(0, sw)
            win32gui.BitBlt(hdc, x, 1, 100, sh, hdc, x, 0, win32con.SRCCOPY)
            time.sleep(0.001)

    @staticmethod
    def trails():
        hdc = get_hdc()
        while running:
            win32gui.BitBlt(hdc, 5, 5, sw-10, sh-10, hdc, 0, 0, win32con.SRCCOPY)
            time.sleep(0.05)

    @staticmethod
    def rotate():
        hdc = get_hdc()
        while running:
            win32gui.StretchBlt(hdc, 10, 10, sw-20, sh-20, hdc, 0, 0, sw, sh, win32con.SRCCOPY)
            time.sleep(0.05)

    @staticmethod
    def invert():
        hdc = get_hdc()
        while running:
            win32gui.PatBlt(hdc, 0, 0, sw, sh, win32con.DSTINVERT)
            time.sleep(0.5)

    @staticmethod
    def rainbow():
        hdc = get_hdc()
        while running:
            brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
            win32gui.SelectObject(hdc, brush)
            win32gui.PatBlt(hdc, 0, 0, sw, sh, win32con.PATINVERT)
            time.sleep(0.1)

    @staticmethod
    def circle_square():
        hdc = get_hdc()
        while running:
            x, y = random.randint(0, sw), random.randint(0, sh)
            if random.random() > 0.5:
                win32gui.Rectangle(hdc, x, y, x+100, y+100)
            else:
                win32gui.Ellipse(hdc, x, y, x+100, y+100)
            time.sleep(0.05)

    @staticmethod
    def flip():
        hdc = get_hdc()
        while running:
            win32gui.StretchBlt(hdc, sw, 0, -sw, sh, hdc, 0, 0, sw, sh, win32con.SRCCOPY)
            time.sleep(0.5)

    @staticmethod
    def cubes():
        hdc = get_hdc()
        while running:
            x, y = random.randint(0, sw), random.randint(0, sh)
            size = random.randint(20, 100)
            win32gui.Rectangle(hdc, x, y, x+size, y+size)
            win32gui.BitBlt(hdc, x+2, y+2, size, size, hdc, x, y, win32con.SRCINVERT)
            time.sleep(0.05)

# --- GUI Application ---

class GDIMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Python GDI Menu")
        self.root.geometry("400x600")
        self.root.attributes("-topmost", True)
        
        style = ttk.Style()
        style.theme_use('clam')

        lbl = tk.Label(root, text="GDI Effects Controller", font=("Arial", 14, "bold"))
        lbl.pack(pady=10)

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(fill="both", expand=True, padx=10)

        effects = [
            ("Dark", GDIEffects.dark), ("Cursors", GDIEffects.cursors),
            ("RGBCircle", GDIEffects.rgb_circle), ("IconWave", GDIEffects.icon_wave),
            ("Sinewave", GDIEffects.sinewave), ("Shake", GDIEffects.shake),
            ("Melter", GDIEffects.melter), ("Trails", GDIEffects.trails),
            ("Rotate", GDIEffects.rotate), ("Rainbow", GDIEffects.rainbow),
            ("Invert", GDIEffects.invert), ("Flip", GDIEffects.flip),
            ("CircleSquare", GDIEffects.circle_square), ("Cubes", GDIEffects.cubes),
            ("Bright", lambda: self.fast_blit(win32con.SRCPAINT)),
            ("ExtremeRotation", lambda: self.repeat_stretch()),
            ("Colors", lambda: self.color_cycle()),
            ("Melter2", lambda: self.melter_variant(2)),
            ("Melter3", lambda: self.melter_variant(5)),
            ("Dark2", lambda: self.fast_blit(win32con.SRCAND))
        ]

        for name, func in effects:
            btn = ttk.Button(self.btn_frame, text=name, command=lambda f=func: self.start_effect(f))
            btn.pack(fill="x", pady=2)

        stop_btn = tk.Button(root, text="STOP ALL EFFECTS", bg="red", fg="white", font=("Arial", 12, "bold"), command=self.stop_all)
        stop_btn.pack(fill="x", pady=20)

    def start_effect(self, effect_func):
        global running
        self.stop_all()
        running = True
        thread = threading.Thread(target=effect_func, daemon=True)
        thread.start()

    def stop_all(self):
        global running
        running = False
        win32gui.InvalidateRect(0, None, True) # Refresh screen

    # Variant logic for buttons that need parameters
    def fast_blit(self, mode):
        hdc = get_hdc()
        while running:
            win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, mode)
            time.sleep(0.1)

    def color_cycle(self):
        hdc = get_hdc()
        while running:
            brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
            win32gui.SelectObject(hdc, brush)
            win32gui.PatBlt(hdc, 0, 0, sw, sh, win32con.PATCOPY)
            time.sleep(0.2)

    def melter_variant(self, speed):
        hdc = get_hdc()
        while running:
            win32gui.BitBlt(hdc, 0, speed, sw, sh, hdc, 0, 0, win32con.SRCCOPY)
            time.sleep(0.01)

    def repeat_stretch(self):
        hdc = get_hdc()
        while running:
            win32gui.StretchBlt(hdc, -10, -10, sw+20, sh+20, hdc, 0, 0, sw, sh, win32con.SRCCOPY)
            time.sleep(0.01)

if __name__ == "__main__":
    root = tk.Tk()
    app = GDIMenu(root)
    root.mainloop()