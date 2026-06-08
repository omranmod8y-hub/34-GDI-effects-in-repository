import win32gui, win32api, win32con
import time, random, math, threading, ctypes, colorsys

# --- SETUP & DPI AWARENESS ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
user32.SetProcessDPIAware()

sw = win32api.GetSystemMetrics(0)
sh = win32api.GetSystemMetrics(1)

# --- MONOXIDE MATH HELPERS ---
class MonoxideMath:
    def __init__(self):
        self.xs = random.getrandbits(32)
        # Precompute sine table like the C++ pfSinVals[4096]
        self.sin_table = [math.sin(i / 4096.0 * math.pi * 2.0) for i in range(4096)]

    def xorshift32(self):
        self.xs ^= (self.xs << 13) & 0xFFFFFFFF
        self.xs ^= (self.xs >> 17) & 0xFFFFFFFF
        self.xs ^= (self.xs << 5) & 0xFFFFFFFF
        return self.xs

    def fast_sine(self, f):
        i = int(f / (2.0 * math.pi) * 4096.0)
        return self.sin_table[i % 4096]

    def fast_cosine(self, f):
        return self.fast_sine(f + math.pi / 2.0)

m_math = MonoxideMath()

# --- GDI PAYLOADS (Ported from C++ Shaders) ---

def cursor_spam(stop_event):
    """Port of CursorDraw()"""
    hdc = win32gui.GetDC(0)
    while not stop_event.is_set():
        try:
            ci = win32gui.GetCursorInfo()
            if ci[1]: # ci[1] is the hCursor handle
                for _ in range(m_math.xorshift32() % 5 + 1):
                    x = m_math.xorshift32() % sw
                    y = m_math.xorshift32() % sh
                    win32gui.DrawIcon(hdc, x, y, ci[1])
        except: pass
        time.sleep(0.01)
    win32gui.ReleaseDC(0, hdc)

def window_chaos(stop_event):
    """Port of EnumGlobalWnd() - Shakes and renames windows"""
    def enum_handler(hwnd, lparam):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            # Shake window
            rect = win32gui.GetWindowRect(hwnd)
            w, h = rect[2] - rect[0], rect[3] - rect[1]
            win32gui.MoveWindow(hwnd, rect[0] + random.randint(-2, 2), rect[1] + random.randint(-2, 2), w, h, True)
            # Random Unicode rename
            win32gui.SetWindowText(hwnd, "".join([chr(random.randint(0x4E00, 0x9FFF)) for _ in range(5)]))
    
    while not stop_event.is_set():
        win32gui.EnumWindows(enum_handler, None)
        time.sleep(0.5)

def shader_wavy_move(stop_event):
    """Port of GdiShader1/2 logic - Sinusoidal screen movement"""
    hdc = win32gui.GetDC(0)
    t = 0
    while not stop_event.is_set():
        div = t / 20.0
        a = int(m_math.fast_sine(div) * 10)
        b = int(m_math.fast_cosine(div) * 10)
        # Shift screen content
        win32gui.BitBlt(hdc, a, b, sw, sh, hdc, 0, 0, win32con.SRCCOPY)
        t += 1
        time.sleep(0.01)
    win32gui.ReleaseDC(0, hdc)

def shader_rainbow_wash(stop_event):
    """Port of GdiShader20/21 - HSL Rainbow rotation"""
    hdc = win32gui.GetDC(0)
    hue = 0.0
    while not stop_event.is_set():
        try:
            rgb = colorsys.hls_to_rgb(hue, 0.5, 1.0)
            color = win32api.RGB(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            
            brush = win32gui.CreateSolidBrush(color)
            old_brush = win32gui.SelectObject(hdc, brush)
            
            # PATINVERT creates the glitchy blend effect
            win32gui.PatBlt(hdc, 0, 0, sw, sh, win32con.PATINVERT)
            
            win32gui.SelectObject(hdc, old_brush)
            win32gui.DeleteObject(brush)
            hue = (hue + 0.02) % 1.0
        except: pass
        time.sleep(0.05)
    win32gui.ReleaseDC(0, hdc)

def shader_melting(stop_event):
    """Standard GDI Melting Effect"""
    hdc = win32gui.GetDC(0)
    while not stop_event.is_set():
        x = m_math.xorshift32() % sw
        win32gui.BitBlt(hdc, x, random.randint(1, 5), 100, sh, hdc, x, 0, win32con.SRCCOPY)
        time.sleep(0.01)
    win32gui.ReleaseDC(0, hdc)

# --- ENGINE ---

def clean_screen():
    """Restores the screen by forcing a redraw of all windows"""
    user32.RedrawWindow(0, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE | win32con.RDW_ALLCHILDREN)

def run_phase(payloads, duration):
    stop = threading.Event()
    threads = []
    for p in payloads:
        t = threading.Thread(target=p, args=(stop,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    stop.set()
    time.sleep(0.1)
    clean_screen()

def main():
    if win32gui.MessageBox(0, "Start Monoxide GDI Simulation?", "Hydrogen/Monoxide", win32con.MB_YESNO | win32con.MB_ICONWARNING) != win32con.IDYES:
        return

    # Simulation Sequence
    try:
        # Phase 1: Window Shaking & Cursor Spam
        run_phase([window_chaos, cursor_spam], 10)
        
        # Phase 2: Screen Movement (Wavy)
        run_phase([shader_wavy_move, cursor_spam], 10)
        
        # Phase 3: Rainbow Chaos
        run_phase([shader_rainbow_wash, window_chaos], 10)
        
        # Phase 4: Melting & Final Flash
        run_phase([shader_melting, shader_wavy_move, cursor_spam], 15)

    except KeyboardInterrupt:
        pass

    clean_screen()
    win32gui.MessageBox(0, "Simulation Finished. Your screen has been restored.", "Safe Exit", 64)

if __name__ == "__main__":
    main()