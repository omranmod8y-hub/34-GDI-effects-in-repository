import win32gui
import win32api
import win32con
import math
import time
import random
import ctypes

# --- Configuration ---
sw = win32api.GetSystemMetrics(0)
sh = win32api.GetSystemMetrics(1)
TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS

# --- Show Message Box First ---
def show_warning():
    title = "Jwzyexyol GDI"
    message = "Warning: This script will draw visual effects on your screen.\n\nTo STOP: Move your mouse to the top-left corner (0,0).\n\nContinue?"
    # 0x31 is MB_OKCANCEL | MB_ICONWARNING
    res = win32api.MessageBox(0, message, title, win32con.MB_OKCANCEL | win32con.MB_ICONWARNING)
    if res != win32con.IDOK:
        exit()

# --- Helper Data for Payloads ---
stars = [[random.randint(-sw, sw), random.randint(-sh, sh), random.randint(1, 1000)] for _ in range(100)]
circles = [[random.randint(0, sw), random.randint(0, sh), random.randint(5, 12), random.randint(5, 12)] for _ in range(15)]

def get_hdc():
    return win32gui.GetDC(0)

# --- 10 Payloads ---

def payload_1_spiral(hdc, t):
    cx, cy = sw // 2, sh // 2
    r = (t * 80) % (sh // 1.5)
    angle = t * 7
    x, y = int(cx + r * math.cos(angle)), int(cy + r * math.sin(angle))
    brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), 0, 255))
    win32gui.SelectObject(hdc, brush)
    win32gui.Ellipse(hdc, x-25, y-25, x+25, y+25)
    win32gui.DeleteObject(brush)

def payload_2_plasma(hdc, t):
    for x in range(0, sw, 60):
        v = math.sin(x * 0.02 + t * 2)
        h = int((v + 1) * (sh / 2.5))
        brush = win32gui.CreateSolidBrush(win32api.RGB(int(127 + 127 * v), 0, 255))
        win32gui.SelectObject(hdc, brush)
        win32gui.PatBlt(hdc, x, sh - h, 60, h, win32con.PATCOPY)
        win32gui.DeleteObject(brush)

def payload_3_bouncing(hdc, t):
    for c in circles:
        c[0] += c[2]; c[1] += c[3]
        if c[0] <= 0 or c[0] >= sw: c[2] *= -1
        if c[1] <= 0 or c[1] >= sh: c[3] *= -1
        brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        win32gui.SelectObject(hdc, brush)
        win32gui.Ellipse(hdc, c[0]-35, c[1]-35, c[0]+35, c[1]+35)
        win32gui.DeleteObject(brush)

def payload_4_rotation(hdc, t):
    # Simulates a rotating displacement
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
    x2 = x + int(math.cos(angle) * depth * 12)
    y2 = y + int(math.sin(angle) * depth * 12)
    win32gui.MoveToEx(hdc, x, y)
    win32gui.LineTo(hdc, x2, y2)
    draw_fractal_tree(hdc, x2, y2, angle - 0.5, depth - 1)
    draw_fractal_tree(hdc, x2, y2, angle + 0.5, depth - 1)

def payload_7_fractal(hdc, t):
    pen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(255, 255, 0))
    win32gui.SelectObject(hdc, pen)
    draw_fractal_tree(hdc, sw//2, sh, -math.pi/2 + math.sin(t), 8)
    win32gui.DeleteObject(pen)

def payload_8_rects(hdc, t):
    for _ in range(4):
        brush = win32gui.CreateSolidBrush(win32api.RGB(0, random.randint(100,255), random.randint(100,255)))
        win32gui.SelectObject(hdc, brush)
        x, y = random.randint(0, sw), random.randint(0, sh)
        win32gui.Rectangle(hdc, x, y, x+120, y+120)
        win32gui.DeleteObject(brush)

def payload_9_starfield(hdc, t):
    for s in stars:
        s[2] -= 25
        if s[2] <= 0: s[2] = 1000
        x = int(sw/2 + (s[0] / s[2]) * 250)
        y = int(sh/2 + (s[1] / s[2]) * 250)
        win32gui.SetPixel(hdc, x, y, win32api.RGB(255, 255, 255))

def payload_10_lines(hdc, t):
    pen = win32gui.CreatePen(win32con.PS_SOLID, 1, win32api.RGB(255, 0, 0))
    win32gui.SelectObject(hdc, pen)
    for i in range(0, sw, 100):
        offset = int(math.sin(t + i) * 50)
        win32gui.MoveToEx(hdc, i + offset, 0)
        win32gui.LineTo(hdc, sw - i - offset, sh)
    win32gui.DeleteObject(pen)

# --- Main Loop ---

def main():
    show_warning()
    
    payloads = [
        payload_1_spiral, payload_2_plasma, payload_3_bouncing,
        payload_4_rotation, payload_5_text, payload_6_kaleidoscope,
        payload_7_fractal, payload_8_rects, payload_9_starfield, payload_10_lines
    ]
    
    current_idx = 0
    start_time = time.perf_counter()
    payload_timer = time.perf_counter()
    
    while True:
        frame_start = time.perf_counter()
        
        # Get Real Screen DC
        hdc = get_hdc()
        t = time.perf_counter() - start_time
        
        # Switch every 8 seconds
        if time.perf_counter() - payload_timer > 8:
            current_idx = (current_idx + 1) % len(payloads)
            payload_timer = time.perf_counter()
            # Force redraw to clear old artifacts
            win32gui.InvalidateRect(0, None, True)

        # Run GDI Effect
        payloads[current_idx](hdc, t)
        
        win32gui.ReleaseDC(0, hdc)
        
        # Safety Stop (Mouse at 0,0)
        if win32api.GetCursorPos() == (0, 0):
            win32gui.InvalidateRect(0, None, True) # Clean screen on exit
            break
            
        # FPS Logic (60 FPS)
        elapsed = time.perf_counter() - frame_start
        sleep_time = FRAME_TIME - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()