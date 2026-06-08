import win32gui
import win32api
import win32con
import math
import time
import random
import threading
import pyaudio

# --- Configuration ---
sw = win32api.GetSystemMetrics(0)
sh = win32api.GetSystemMetrics(1)
TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS
SAMPLE_RATE = 8000  

# Global state
current_payload_idx = 0
running = True

# --- Bytebeat Formulas (1-11) ---
formulas = [
    lambda t: (t * (t >> 8 | t >> 9) & 46 & t >> 8) ^ (t & t >> 13 | t >> 6), # 1
    lambda t: (t >> 6 | t | t >> (t >> 16)) * 10 + ((t >> 11) & 7),           # 2
    lambda t: (t * (t >> 5 | t >> 8)) >> (t >> 16),                          # 3
    lambda t: t * (((t >> 12) | (t >> 8)) & (63 & (t >> 4))),                # 4
    lambda t: (t >> 7 | t | t >> 6) * 10 + 4 * (t & t >> 13 | t >> 6),       # 5
    lambda t: (t * 5 & t >> 7) | (t * 3 & t >> 10),                          # 6
    lambda t: (t >> 10 ^ t >> 11) * t & ((t >> 12) | 127),                   # 7
    lambda t: (t >> 5 | t >> 4 | t >> 3) & t << 1,                           # 8
    lambda t: (t * (t >> 8 + t >> 9) & 33 & t >> 8) | (t & t >> 11),         # 9
    lambda t: t * (t >> 11 & t >> 8 & 123 & t >> 3),                         # 10
    lambda t: (t * 5 & t >> 7) | (t * 3 & t >> 10) | (t >> 4 & t >> 8)       # 11 (Rainbow Chaos)
]

# --- Audio Thread ---
def audio_engine():
    global current_payload_idx, running
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt8, channels=1, rate=SAMPLE_RATE, output=True)
    t = 0
    while running:
        try:
            formula = formulas[current_payload_idx]
            samples = bytes([formula(t + i) & 0xFF for i in range(1024)])
            stream.write(samples)
            t += 1024
        except: break
    stream.stop_stream(); stream.close(); p.terminate()

# --- Visual Payloads ---
def payload_1_spiral(hdc, t):
    cx, cy = sw // 2, sh // 2
    r = (t * 80) % (sh // 1.5)
    angle = t * 7
    x, y = int(cx + r * math.cos(angle)), int(cy + r * math.sin(angle))
    brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), 0, 255))
    win32gui.SelectObject(hdc, brush); win32gui.Ellipse(hdc, x-25, y-25, x+25, y+25); win32gui.DeleteObject(brush)

def payload_2_plasma(hdc, t):
    for x in range(0, sw, 60):
        v = math.sin(x * 0.02 + t * 2)
        h = int((v + 1) * (sh / 2.5))
        brush = win32gui.CreateSolidBrush(win32api.RGB(int(127 + 127 * v), 0, 255))
        win32gui.SelectObject(hdc, brush); win32gui.PatBlt(hdc, x, sh - h, 60, h, win32con.PATCOPY); win32gui.DeleteObject(brush)

def payload_3_bouncing(hdc, t):
    # Setup helper for bouncing
    global circles
    if 'circles' not in globals(): circles = [[random.randint(0, sw), random.randint(0, sh), random.randint(5, 12), random.randint(5, 12)] for _ in range(15)]
    for c in circles:
        c[0] += c[2]; c[1] += c[3]
        if c[0] <= 0 or c[0] >= sw: c[2] *= -1
        if c[1] <= 0 or c[1] >= sh: c[3] *= -1
        brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        win32gui.SelectObject(hdc, brush); win32gui.Ellipse(hdc, c[0]-35, c[1]-35, c[0]+35, c[1]+35); win32gui.DeleteObject(brush)

def payload_4_rotation(hdc, t):
    dx, dy = int(15 * math.sin(t*5)), int(15 * math.cos(t*5))
    win32gui.BitBlt(hdc, dx, dy, sw, sh, hdc, 0, 0, win32con.SRCCOPY)

def payload_5_text(hdc, t):
    win32gui.SetTextColor(hdc, win32api.RGB(random.randint(0,255), 255, random.randint(0,255)))
    win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
    win32gui.DrawText(hdc, "JWZYEXYOL", -1, (random.randint(0,sw), random.randint(0,sh), sw, sh), win32con.DT_LEFT)

def payload_6_kaleidoscope(hdc, t):
    win32gui.StretchBlt(hdc, 0, 0, sw//2, sh//2, hdc, sw, sh, -sw//2, -sh//2, win32con.SRCPAINT)

def draw_fractal_tree(hdc, x, y, angle, depth):
    if depth == 0: return
    x2 = x + int(math.cos(angle) * depth * 12); y2 = y + int(math.sin(angle) * depth * 12)
    win32gui.MoveToEx(hdc, x, y); win32gui.LineTo(hdc, x2, y2)
    draw_fractal_tree(hdc, x2, y2, angle - 0.5, depth - 1); draw_fractal_tree(hdc, x2, y2, angle + 0.5, depth - 1)

def payload_7_fractal(hdc, t):
    pen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(255, 255, 0))
    win32gui.SelectObject(hdc, pen); draw_fractal_tree(hdc, sw//2, sh, -math.pi/2 + math.sin(t), 8); win32gui.DeleteObject(pen)

def payload_8_rects(hdc, t):
    for _ in range(4):
        brush = win32gui.CreateSolidBrush(win32api.RGB(0, random.randint(100,255), random.randint(100,255)))
        win32gui.SelectObject(hdc, brush); x, y = random.randint(0, sw), random.randint(0, sh)
        win32gui.Rectangle(hdc, x, y, x+120, y+120); win32gui.DeleteObject(brush)

def payload_9_starfield(hdc, t):
    global stars
    if 'stars' not in globals(): stars = [[random.randint(-sw, sw), random.randint(-sh, sh), random.randint(1, 1000)] for _ in range(100)]
    for s in stars:
        s[2] -= 25
        if s[2] <= 0: s[2] = 1000
        x, y = int(sw/2 + (s[0] / s[2]) * 250), int(sh/2 + (s[1] / s[2]) * 250)
        win32gui.SetPixel(hdc, x, y, win32api.RGB(255, 255, 255))

def payload_10_lines(hdc, t):
    pen = win32gui.CreatePen(win32con.PS_SOLID, 1, win32api.RGB(255, 0, 0))
    win32gui.SelectObject(hdc, pen)
    for i in range(0, sw, 100):
        offset = int(math.sin(t + i) * 50)
        win32gui.MoveToEx(hdc, i + offset, 0); win32gui.LineTo(hdc, sw - i - offset, sh)
    win32gui.DeleteObject(pen)

# --- NEW PAYLOAD 11 (Scrolling + Rainbow) ---
def payload_11_rainbow_scroll(hdc, t):
    # 1. Your C++ Scrolling Logic
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, -30, 0, win32con.SRCCOPY)
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, sw - 30, 0, win32con.SRCCOPY)
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, -30, win32con.SRCCOPY)
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, sh - 30, win32con.SRCCOPY)
    
    # 2. Rainbow Overlay Logic
    # Generate rainbow colors using sine waves
    r = int(127 + 127 * math.sin(t * 3))
    g = int(127 + 127 * math.sin(t * 3 + 2))
    b = int(127 + 127 * math.sin(t * 3 + 4))
    
    brush = win32gui.CreateSolidBrush(win32api.RGB(r, g, b))
    win32gui.SelectObject(hdc, brush)
    
    # PATINVERT combines the brush color with the existing screen pixels
    win32gui.PatBlt(hdc, 0, 0, sw, sh, win32con.PATINVERT)
    win32gui.DeleteObject(brush)

# --- Main Logic ---
def main():
    global current_payload_idx, running
    
    # Safety Prompt
    if win32api.MessageBox(0, "Start GDI Effects?\nSTOP: Move mouse to (0,0)", "Warning", win32con.MB_OKCANCEL) != win32con.IDOK:
        return

    threading.Thread(target=audio_engine, daemon=True).start()
    
    payloads = [
        payload_1_spiral, payload_2_plasma, payload_3_bouncing,
        payload_4_rotation, payload_5_text, payload_6_kaleidoscope,
        payload_7_fractal, payload_8_rects, payload_9_starfield, 
        payload_10_lines, payload_11_rainbow_scroll
    ]
    
    start_time = time.perf_counter()
    payload_timer = time.perf_counter()
    
    try:
        while running:
            loop_start = time.perf_counter()
            hdc = win32gui.GetDC(0)
            t = time.perf_counter() - start_time
            
            # Switch every 8 seconds
            if time.perf_counter() - payload_timer > 8:
                current_payload_idx = (current_payload_idx + 1) % len(payloads)
                payload_timer = time.perf_counter()
                win32gui.InvalidateRect(0, None, True)

            payloads[current_payload_idx](hdc, t)
            win32gui.ReleaseDC(0, hdc)
            
            if win32api.GetCursorPos() == (0, 0): break
            
            elapsed = time.perf_counter() - loop_start
            time.sleep(max(0, FRAME_TIME - elapsed))
    finally:
        running = False
        win32gui.InvalidateRect(0, None, True) # Clean screen

if __name__ == "__main__":
    main()