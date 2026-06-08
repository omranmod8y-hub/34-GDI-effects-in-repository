import win32gui
import win32api
import win32con
import math
import time
import random
import threading
import pyaudio
import numpy as np

# --- Configuration ---
sw = win32api.GetSystemMetrics(0)
sh = win32api.GetSystemMetrics(1)
TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS
STREAM_RATE = 16000 

# Global state for audio sync
current_payload_idx = 0
running = True

# --- Bytebeat Formulas & Metadata ---
# (formula_lambda, is_16000hz)
formulas = [
    (lambda t: ((((t & t >> 8) - (t >> 13 & t)) & ((t & t >> 8) - (t >> 13))) ^ (t >> 8 & t)), True),
    (lambda t: (t - (t >> 4 & t >> 8) & t >> 12) - 1, False),
    (lambda t: ((t >> 8 & t >> 4) >> (t >> 16 & t >> 8)) * t, True),
    (lambda t: (t & (t >> 7 | t >> 8 | t >> 16) ^ t) * t, True),
    (lambda t: (t * t // (1 + (t >> 9 & t >> 8))) & 128, False),
    (lambda t: t >> 5 | (t >> 2) * (t >> 5), True),
    (lambda t: 100 * ((t << 2 | t >> 5 | t ^ 63) & (t << 10 | t >> 11)), True),
    (lambda t: t // 8 >> (t >> 9) * t // ((t >> 14 & 3) + 4), True),
    (lambda t: 10 * (t & 5 * t | t >> 6 | (-6 * t // 7 if t & 32768 else (-9 * (t & 100) if t & 65536 else -9 * (t & 100)) // 11)), True),
    (lambda t: 10 * (t >> 7 | 3 * t | t >> (t >> 15)) + (t >> 8 & 5), True)
]

# --- Audio Thread ---
def audio_engine():
    global current_payload_idx, running
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt8, channels=1, rate=STREAM_RATE, output=True)
    
    t = 0
    chunk_size = 1024
    
    try:
        while running:
            formula_func, is_16k = formulas[current_payload_idx]
            buf = bytearray(chunk_size)
            for i in range(chunk_size):
                actual_t = t if is_16k else t // 2
                buf[i] = formula_func(int(actual_t)) & 0xFF
                t += 1
            stream.write(bytes(buf))
            if t > 0xFFFFFFFF: t = 0 
    except:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# --- Visual Payloads ---
def show_warning():
    title = "Jwzyexyol Warning"
    message = "Visual effects and loud Bytebeat audio will start.\n\nDo you want to continue?"
    # MB_YESNO creates the Yes/No buttons
    res = win32api.MessageBox(0, message, title, win32con.MB_YESNO | win32con.MB_ICONWARNING)
    if res != win32con.IDYES:
        exit()

# [Visual data/functions]
stars = [[random.randint(-sw, sw), random.randint(-sh, sh), random.randint(1, 1000)] for _ in range(100)]
circles = [[random.randint(0, sw), random.randint(0, sh), random.randint(5, 12), random.randint(5, 12)] for _ in range(15)]

def get_hdc(): return win32gui.GetDC(0)

def payload_1_spiral(hdc, t):
    cx, cy = sw // 2, sh // 2
    r = (int(t * 150)) % (sh // 1.5)
    angle = t * 10
    x, y = int(cx + r * math.cos(angle)), int(cy + r * math.sin(angle))
    brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), 0, 255))
    win32gui.SelectObject(hdc, brush); win32gui.Ellipse(hdc, x-30, y-30, x+30, y+30); win32gui.DeleteObject(brush)

def payload_2_plasma(hdc, t):
    for x in range(0, sw, 50):
        v = math.sin(x * 0.01 + t * 3)
        h = int((v + 1) * (sh / 2))
        brush = win32gui.CreateSolidBrush(win32api.RGB(0, int(127 + 127 * v), 255))
        win32gui.SelectObject(hdc, brush); win32gui.PatBlt(hdc, x, sh - h, 50, h, win32con.PATCOPY); win32gui.DeleteObject(brush)

def payload_3_bouncing(hdc, t):
    for c in circles:
        c[0] += c[2]; c[1] += c[3]
        if c[0] <= 0 or c[0] >= sw: c[2] *= -1
        if c[1] <= 0 or c[1] >= sh: c[3] *= -1
        brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), 0, random.randint(0,255)))
        win32gui.SelectObject(hdc, brush); win32gui.Ellipse(hdc, c[0]-40, c[1]-40, c[0]+40, c[1]+40); win32gui.DeleteObject(brush)

def payload_4_rotation(hdc, t):
    dx, dy = int(20 * math.sin(t*10)), int(20 * math.cos(t*10))
    win32gui.BitBlt(hdc, dx, dy, sw, sh, hdc, 0, 0, win32con.SRCINVERT)

def payload_5_text(hdc, t):
    win32gui.SetTextColor(hdc, win32api.RGB(255, random.randint(0,255), 0))
    win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
    win32gui.DrawText(hdc, "JWZYEXYOL", -1, (random.randint(0,sw), random.randint(0,sh), sw, sh), win32con.DT_LEFT)

def payload_6_kaleidoscope(hdc, t):
    win32gui.StretchBlt(hdc, 0, 0, sw//2, sh//2, hdc, sw, sh, -sw//2, -sh//2, win32con.SRCPAINT)

def draw_fractal_tree(hdc, x, y, angle, depth):
    if depth == 0: return
    x2 = x + int(math.cos(angle) * depth * 15); y2 = y + int(math.sin(angle) * depth * 15)
    win32gui.MoveToEx(hdc, x, y); win32gui.LineTo(hdc, x2, y2)
    draw_fractal_tree(hdc, x2, y2, angle - 0.4, depth - 1); draw_fractal_tree(hdc, x2, y2, angle + 0.4, depth - 1)

def payload_7_fractal(hdc, t):
    pen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(0, 255, 0))
    win32gui.SelectObject(hdc, pen); draw_fractal_tree(hdc, sw//2, sh, -math.pi/2 + math.sin(t*2), 9); win32gui.DeleteObject(pen)

def payload_8_rects(hdc, t):
    for _ in range(5):
        brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), 0, 0))
        win32gui.SelectObject(hdc, brush); x, y = random.randint(0, sw), random.randint(0, sh)
        win32gui.Rectangle(hdc, x, y, x+150, y+150); win32gui.DeleteObject(brush)

def payload_9_starfield(hdc, t):
    for s in stars:
        s[2] -= 30
        if s[2] <= 0: s[2] = 1000
        x, y = int(sw/2 + (s[0] / s[2]) * 300), int(sh/2 + (s[1] / s[2]) * 300)
        win32gui.SetPixel(hdc, x, y, win32api.RGB(255, 255, 255))

def payload_10_lines(hdc, t):
    pen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(255, 255, 0))
    win32gui.SelectObject(hdc, pen)
    for i in range(0, sw, 80):
        offset = int(math.sin(t*3 + i) * 100)
        win32gui.MoveToEx(hdc, i + offset, 0); win32gui.LineTo(hdc, sw - i - offset, sh)
    win32gui.DeleteObject(pen)

# --- Main ---
def main():
    global current_payload_idx, running
    show_warning()
    
    a_thread = threading.Thread(target=audio_engine, daemon=True)
    a_thread.start()
    
    visual_payloads = [
        payload_1_spiral, payload_2_plasma, payload_3_bouncing,
        payload_4_rotation, payload_5_text, payload_6_kaleidoscope,
        payload_7_fractal, payload_8_rects, payload_9_starfield, payload_10_lines
    ]
    
    start_time = time.perf_counter()
    payload_timer = time.perf_counter()
    
    try:
        while running:
            frame_start = time.perf_counter()
            hdc = get_hdc()
            t = time.perf_counter() - start_time
            
            if time.perf_counter() - payload_timer > 8:
                current_payload_idx = (current_payload_idx + 1) % len(visual_payloads)
                payload_timer = time.perf_counter()
                win32gui.InvalidateRect(0, None, True)

            visual_payloads[current_payload_idx](hdc, t)
            win32gui.ReleaseDC(0, hdc)
            
            if win32api.GetCursorPos() == (0, 0):
                running = False
                break
                
            elapsed = time.perf_counter() - frame_start
            if FRAME_TIME > elapsed:
                time.sleep(FRAME_TIME - elapsed)
    finally:
        running = False
        time.sleep(0.5)
        win32gui.InvalidateRect(0, None, True)

if __name__ == "__main__":
    main()