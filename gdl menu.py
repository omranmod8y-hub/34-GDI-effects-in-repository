import ctypes
import math
import random
import time
import threading
import tkinter as tk
from tkinter import ttk
from ctypes import wintypes

# --- Windows API Setup ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
winmm = ctypes.windll.winmm
msimg32 = ctypes.windll.msimg32

# GDI Constants
SRCCOPY, SRCINVERT, PATINVERT, SRCPAINT, SRCAND, NOTSRCCOPY = 0x00CC0020, 0x00660046, 0x005A0049, 0x00EE0086, 0x008800C6, 0x00330008
BI_RGB, GM_ADVANCED = 0, 2
SW, SH = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# --- Global Control State ---
class State:
    active = {}
    audio_on = False
    running = True

# --- Audio Engine (Bytebeat) ---
def audio_loop():
    wfx = bytes([1, 0, 1, 0, 64, 31, 0, 0, 64, 31, 0, 0, 1, 0, 8, 0, 0, 0])
    h_waveout = wintypes.HANDLE()
    winmm.waveOutOpen(ctypes.byref(h_waveout), -1, wfx, 0, 0, 0)
    t = 0
    while State.running:
        if State.audio_on:
            buf_size = 4000
            # Formula: Mix of industrial glitches
            buf = bytearray([( (t >> 6 | t | t >> (t >> 16)) * 10 + ((t >> 11) & 7) ) & 0xFF for t in range(t, t + buf_size)])
            t += buf_size
            header = ctypes.create_string_buffer(bytes(buf))
            winmm.waveOutWrite(h_waveout, header, len(header))
            time.sleep(0.4)
        else:
            time.sleep(0.1)

# --- GDI Payload Functions ---
def gdi_engine():
    hdc = user32.GetDC(0)
    # Setup for Shaders (DIB Section)
    class BITMAPINFO(ctypes.Structure):
        _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
                    ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                    ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG),
                    ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD), ("colors", wintypes.DWORD * 1)]
    
    bmi = BITMAPINFO(40, SW, -SH, 1, 32, BI_RGB)
    ptr = ctypes.c_void_p()
    h_mem = gdi32.CreateCompatibleDC(hdc)
    h_bmp = gdi32.CreateDIBSection(hdc, ctypes.byref(bmi), 0, ctypes.byref(ptr), None, 0)
    gdi32.SelectObject(h_mem, h_bmp)
    
    pixels = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_uint32))
    frame = 0

    while State.running:
        if any(State.active.values()):
            # Capture current screen for shaders
            gdi32.BitBlt(h_mem, 0, 0, SW, SH, hdc, 0, 0, SRCCOPY)
            
            # --- APPLY ACTIVE EFFECTS ---
            if State.active.get("Tunnel"):
                gdi32.StretchBlt(hdc, 10, 10, SW - 20, SH - 20, hdc, 0, 0, SW, SH, SRCCOPY)
            
            if State.active.get("Melt"):
                x = random.randint(0, SW); gdi32.BitBlt(hdc, x, 5, 100, SH, hdc, x, 0, SRCCOPY)
            
            if State.active.get("Invert"):
                gdi32.BitBlt(hdc, 0, 0, SW, SH, hdc, 0, 0, PATINVERT)
            
            if State.active.get("Sine"):
                for i in range(0, SH, 30):
                    gdi32.BitBlt(hdc, int(math.sin(frame/10 + i/100)*30), i, SW, 30, hdc, 0, i, SRCCOPY)
            
            if State.active.get("HSL Warp"):
                for i in range(0, SW * SH, 16): # High step for performance
                    pixels[i] ^= (pixels[i] >> 2) | (frame << 16)
                gdi32.BitBlt(hdc, 0, 0, SW, SH, h_mem, 0, 0, SRCCOPY)

            if State.active.get("Arithmetic"):
                for i in range(0, SW * SH, 8):
                    c = pixels[i]; b, g, r = (c & 0xFF), (c >> 8 & 0xFF), (c >> 16 & 0xFF)
                    pixels[i] = ((b-1)&0xFF) | (((g+1)&0xFF)<<8) | (((r-2)&0xFF)<<16)
                gdi32.BitBlt(hdc, 0, 0, SW, SH, h_mem, 0, 0, SRCCOPY)

            if State.active.get("Icons"):
                user32.DrawIcon(hdc, random.randint(0, SW), random.randint(0, SH), user32.LoadIconW(0, 32513))

            frame += 1
            time.sleep(0.01)
        else:
            time.sleep(0.1)

# --- GUI Mod Menu ---
class ModMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("GDL ALL-IN-ONE")
        self.root.geometry("300x500")
        self.root.attributes("-topmost", True)
        
        ttk.Label(root, text="GDL Visuals", font=("Impact", 18)).pack(pady=5)
        
        self.effects = ["Tunnel", "Melt", "Invert", "Sine", "HSL Warp", "Arithmetic", "Icons"]
        for effect in self.effects:
            State.active[effect] = False
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(root, text=effect, variable=var, command=lambda e=effect, v=var: self.toggle(e, v))
            cb.pack(anchor="w", padx=40, pady=2)

        ttk.Separator(root, orient='horizontal').pack(fill='x', pady=10)
        
        self.audio_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(root, text="Bytebeat Audio", variable=self.audio_var, command=self.toggle_audio).pack()

        ttk.Button(root, text="Stop & Refresh Screen", command=self.stop_all).pack(pady=10, fill='x', padx=20)
        ttk.Label(root, text="Press Alt+F4 to quit menu", font=("Arial", 8)).pack()

    def toggle(self, effect, var): State.active[effect] = var.get()
    def toggle_audio(self): State.audio_on = self.audio_var.get()
    def stop_all(self):
        for e in self.effects: State.active[e] = False
        user32.InvalidateRect(0, 0, 0)

if __name__ == "__main__":
    # Initialize DPI Awareness
    try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: user32.SetProcessDPIAware()

    # Safety confirmation
    if user32.MessageBoxW(0, "Run GDL All-In-One Mod Menu?\n(Visual/Audio only - No payload)", "Warning", 4 | 48) != 6:
        exit()

    # Start Engines
    threading.Thread(target=gdi_engine, daemon=True).start()
    threading.Thread(target=audio_loop, daemon=True).start()

    # Run Menu
    root = tk.Tk()
    menu = ModMenu(root)
    root.mainloop()
    State.running = False