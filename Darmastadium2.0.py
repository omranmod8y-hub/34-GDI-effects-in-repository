import ctypes
import random
import time
import threading
import sys

# --- Setup Win32 API ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
shcore = ctypes.windll.shcore
kernel32 = ctypes.windll.kernel32

# Constants
SRCCOPY = 0x00CC0020
NOTSRCCOPY = 0x00330008
SQUARE_SIZE = 100
SW_HIDE = 0

# Colors (RGB)
COLORS = [
    (255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0),
    (0, 0, 255), (75, 0, 130), (148, 0, 211), (255, 0, 255)
]

# Global State
running = True

def hide_console():
    """Hides the console window if it exists."""
    hwnd = kernel32.GetConsoleWindow()
    if hwnd:
        user32.ShowWindow(hwnd, SW_HIDE)

def init_dpi():
    """Ensure coordinates match the actual screen resolution."""
    try:
        shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()

def interpolate_color(c1, c2, progress):
    r = int(c1[0] + (c2[0] - c1[0]) * progress)
    g = int(c1[1] + (c2[1] - c1[1]) * progress)
    b = int(c1[2] + (c2[2] - c1[2]) * progress)
    return r | (g << 8) | (b << 16)

def show_message_box():
    """Replicates the ÆÆÆ message box."""
    user32.MessageBoxW(0, "ÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆ", "ÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆ", 0x10 | 0x0)

def distort_screen_func():
    """Waits 28 seconds then begins vertical strip inversion."""
    global running
    time.sleep(28)
    if not running: return
    
    hdc = user32.GetDC(0)
    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    
    while running:
        x = random.randint(0, sw)
        gdi32.BitBlt(hdc, x, 0, 10, sh, hdc, x, 0, NOTSRCCOPY)
        time.sleep(0.1)
    
    user32.ReleaseDC(0, hdc)

def main():
    global running
    hide_console() # Immediately hide the window
    init_dpi()
    
    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    hdc = user32.GetDC(0)
    
    # Square state
    x, y = 200, 200
    vx, vy = 12, 8
    color_idx = 0
    next_color_idx = 1
    progress = 0.0
    
    # Start threads
    threading.Thread(target=show_message_box, daemon=True).start()
    threading.Thread(target=distort_screen_func, daemon=True).start()
    
    try:
        while running:
            # --- Update Colors ---
            progress += 0.1
            if progress >= 1.0:
                progress = 0.0
                color_idx = (color_idx + 1) % len(COLORS)
                next_color_idx = (color_idx + 1) % len(COLORS)
            
            current_color = interpolate_color(COLORS[color_idx], COLORS[next_color_idx], progress)
            
            # --- Draw Square ---
            h_brush = gdi32.CreateSolidBrush(current_color)
            old_brush = gdi32.SelectObject(hdc, h_brush)
            gdi32.Rectangle(hdc, x, y, x + SQUARE_SIZE, y + SQUARE_SIZE)
            
            # Cleanup
            gdi32.SelectObject(hdc, old_brush)
            gdi32.DeleteObject(h_brush)
            
            # --- Movement ---
            x += vx
            y += vy
            
            if x < 0 or x + SQUARE_SIZE > sw:
                vx = -vx
            if y < 0 or y + SQUARE_SIZE > sh:
                vy = -vy
            
            time.sleep(0.01)
            
    except:
        running = False
    finally:
        user32.ReleaseDC(0, hdc)

if __name__ == "__main__":
    main()