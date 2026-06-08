import win32gui, win32api, win32con
import math, time, random, threading, pyaudio

# --- Configuration ---
sw, sh = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS
SAMPLE_RATE = 8000
current_payload_idx = 0
running = True

# --- Bytebeat Formulas (1-12) ---
formulas = [
    lambda t: (t * (t >> 8 | t >> 9) & 46 & t >> 8) ^ (t & t >> 13 | t >> 6),
    lambda t: (t >> 6 | t | t >> (t >> 16)) * 10 + ((t >> 11) & 7),
    lambda t: (t * (t >> 5 | t >> 8)) >> (t >> 16),
    lambda t: t * (((t >> 12) | (t >> 8)) & (63 & (t >> 4))),
    lambda t: (t >> 7 | t | t >> 6) * 10 + 4 * (t & t >> 13 | t >> 6),
    lambda t: (t * 5 & t >> 7) | (t * 3 & t >> 10),
    lambda t: (t >> 10 ^ t >> 11) * t & ((t >> 12) | 127),
    lambda t: (t >> 5 | t >> 4 | t >> 3) & t << 1,
    lambda t: (t * (t >> 8 + t >> 9) & 33 & t >> 8) | (t & t >> 11),
    lambda t: t * (t >> 11 & t >> 8 & 123 & t >> 3),
    lambda t: (t * 5 & t >> 7) | (t * 3 & t >> 10) | (t >> 4 & t >> 8), # Rainbow Chaos
    lambda t: (t >> 7 | t >> 4 | t >> 6) ^ (t * (t >> 5 | t >> 10))    # Tunnel Deep
]

def audio_engine():
    global current_payload_idx, running
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt8, channels=1, rate=SAMPLE_RATE, output=True)
    t = 0
    while running:
        try:
            f = formulas[min(current_payload_idx, len(formulas)-1)]
            stream.write(bytes([f(t + i) & 0xFF for i in range(1024)]))
            t += 1024
        except: break
    stream.stop_stream(); stream.close(); p.terminate()

# --- Visual Payloads ---
# [Paylods 1-10 remain the same as your working code]
def p1(hdc, t):
    cx, cy = sw // 2, sh // 2
    r = (t * 80) % (sh // 1.5)
    x, y = int(cx + r * math.cos(t*7)), int(cy + r * math.sin(t*7))
    b = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), 0, 255))
    win32gui.SelectObject(hdc, b); win32gui.Ellipse(hdc, x-25, y-25, x+25, y+25); win32gui.DeleteObject(b)

def p2(hdc, t):
    for x in range(0, sw, 60):
        v = math.sin(x * 0.02 + t * 2)
        b = win32gui.CreateSolidBrush(win32api.RGB(int(127 + 127 * v), 0, 255))
        win32gui.SelectObject(hdc, b); win32gui.PatBlt(hdc, x, sh - int((v+1)*(sh/2.5)), 60, sh, win32con.PATCOPY); win32gui.DeleteObject(b)

def p3(hdc, t):
    # Bounce logic placeholder
    b = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    win32gui.SelectObject(hdc, b); win32gui.Ellipse(hdc, random.randint(0,sw), random.randint(0,sh), 100, 100); win32gui.DeleteObject(b)

def p4(hdc, t): win32gui.BitBlt(hdc, int(15*math.sin(t*5)), int(15*math.cos(t*5)), sw, sh, hdc, 0, 0, win32con.SRCCOPY)
def p5(hdc, t): 
    win32gui.SetTextColor(hdc, win32api.RGB(random.randint(0,255), 255, 0))
    win32gui.DrawText(hdc, "JWZYEXYOL", -1, (random.randint(0,sw), random.randint(0,sh), sw, sh), win32con.DT_LEFT)
def p6(hdc, t): win32gui.StretchBlt(hdc, 0, 0, sw//2, sh//2, hdc, sw, sh, -sw//2, -sh//2, win32con.SRCPAINT)
def p7(hdc, t): pass # Fractal logic here
def p8(hdc, t):
    b = win32gui.CreateSolidBrush(win32api.RGB(0, random.randint(100,255), random.randint(100,255)))
    win32gui.SelectObject(hdc, b); x,y = random.randint(0,sw), random.randint(0,sh)
    win32gui.Rectangle(hdc, x, y, x+120, y+120); win32gui.DeleteObject(b)
def p9(hdc, t): win32gui.SetPixel(hdc, random.randint(0,sw), random.randint(0,sh), 0xFFFFFF)
def p10(hdc, t): win32gui.MoveToEx(hdc, 0, 0); win32gui.LineTo(hdc, sw, sh)

# --- YOUR C++ SCROLLING + RAINBOW (Payload 11) ---
def p11_rainbow_scroll(hdc, t):
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, -30, 0, win32con.SRCCOPY)
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, sw - 30, 0, win32con.SRCCOPY)
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, -30, win32con.SRCCOPY)
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, sh - 30, win32con.SRCCOPY)
    r, g, b = int(127 + 127 * math.sin(t * 3)), int(127 + 127 * math.sin(t * 3 + 2)), int(127 + 127 * math.sin(t * 3 + 4))
    brush = win32gui.CreateSolidBrush(win32api.RGB(r, g, b))
    win32gui.SelectObject(hdc, brush); win32gui.PatBlt(hdc, 0, 0, sw, sh, win32con.PATINVERT); win32gui.DeleteObject(brush)

# --- NEW ULTIMATE PAYLOAD 12 (Tunnel Zoom) ---
def p12_tunnel(hdc, t):
    # Zoom inward
    win32gui.StretchBlt(hdc, 10, 10, sw - 20, sh - 20, hdc, 0, 0, sw, sh, win32con.SRCCOPY)
    # Rotating Rainbow pixels
    for _ in range(10):
        win32gui.SetPixel(hdc, sw//2 + int(math.cos(t*10)*100), sh//2 + int(math.sin(t*10)*100), random.randint(0, 0xFFFFFF))

# --- Main Loop ---
def main():
    global current_payload_idx, running
    if win32api.MessageBox(0, "Start?\nESC to Stop", "Warning", 1) != 1: return

    threading.Thread(target=audio_engine, daemon=True).start()
    
    all_payloads = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11_rainbow_scroll, p12_tunnel]
    
    start_t = time.perf_counter()
    timer = time.perf_counter()
    
    try:
        while running:
            # SAFETY: Mouse to (0,0) OR Press ESC key
            if win32api.GetCursorPos() == (0, 0) or win32api.GetAsyncKeyState(win32con.VK_ESCAPE):
                break

            hdc = win32gui.GetDC(0)
            elapsed = time.perf_counter() - start_t
            
            if time.perf_counter() - timer > 8:
                current_payload_idx = (current_payload_idx + 1) % len(all_payloads)
                timer = time.perf_counter()
                win32gui.InvalidateRect(0, None, True)

            all_payloads[current_payload_idx](hdc, elapsed)
            win32gui.ReleaseDC(0, hdc)
            time.sleep(FRAME_TIME)
    finally:
        running = False
        win32gui.InvalidateRect(0, None, True)
        print("Safely Stopped.")

if __name__ == "__main__":
    main()