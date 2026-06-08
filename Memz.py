import ctypes
import random
import time
import threading
import winsound

# --- Setup Win32 API ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
shcore = ctypes.windll.shcore

# Constants
SRCCOPY = 0x00CC0020
NOTSRCCOPY = 0x00330008
SM_CXSCREEN = 0
SM_CYSCREEN = 1
IDI_ERROR = 32513
IDI_WARNING = 32515
MB_ICONERROR = 0x00000010
MB_ICONWARNING = 0x00000030

def init_dpi():
    """Ensure coordinates match high-resolution screens."""
    try:
        shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

# --- Logic Threads ---

def play_error_sound():
    """Simulates random system beeps."""
    while True:
        choice = random.choice([MB_ICONERROR, MB_ICONWARNING])
        winsound.MessageBeep(choice)
        time.sleep(random.uniform(0.1, 1.0))

def show_message_box():
    """Spawns background message boxes."""
    while True:
        time.sleep(10)
        # We spawn this in a separate sub-thread so it doesn't block the loop
        threading.Thread(target=lambda: user32.MessageBoxA(0, b"still using this computer?", b"lol", 0x30)).start()

def draw_cursor_icon():
    """Draws an error icon following the mouse cursor."""
    h_icon = user32.LoadIconA(0, IDI_ERROR)
    while True:
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        hdc = user32.GetDC(0)
        user32.DrawIcon(hdc, pt.x, pt.y, h_icon)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.05)

def shake_cursor():
    """Slightly jitters the mouse cursor."""
    while True:
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        if user32.GetCursorPos(ctypes.byref(pt)):
            move_x = random.choice([1, -1])
            move_y = random.choice([1, -1])
            user32.SetCursorPos(pt.x + move_x, pt.y + move_y)
        time.sleep(0.01)

def draw_random_icons():
    """Draws error/warning icons at random locations."""
    hdc = user32.GetDC(0)
    sw, sh = get_screen_size()
    x = random.randint(0, sw)
    y = random.randint(0, sh)
    h_icon = user32.LoadIconA(0, random.choice([IDI_ERROR, IDI_WARNING]))
    user32.DrawIcon(hdc, x, y, h_icon)
    user32.ReleaseDC(0, hdc)

def move_screen_chunks():
    """Copies chunks of the screen to other random locations."""
    hdc_desktop = user32.GetDC(0)
    sw, sh = get_screen_size()
    while True:
        cw = random.randint(50, sw // 4 + 50)
        ch = random.randint(50, sh // 4 + 50)
        sx, sy = random.randint(0, sw - cw), random.randint(0, sh - ch)
        dx, dy = random.randint(0, sw - cw), random.randint(0, sh - ch)
        
        hdc_mem = gdi32.CreateCompatibleDC(hdc_desktop)
        h_bm = gdi32.CreateCompatibleBitmap(hdc_desktop, cw, ch)
        old_bm = gdi32.SelectObject(hdc_mem, h_bm)
        
        # Copy from screen to memory, then memory to screen at new location
        gdi32.BitBlt(hdc_mem, 0, 0, cw, ch, hdc_desktop, sx, sy, SRCCOPY)
        gdi32.BitBlt(hdc_desktop, dx, dy, cw, ch, hdc_mem, 0, 0, SRCCOPY)
        
        gdi32.SelectObject(hdc_mem, old_bm)
        gdi32.DeleteObject(h_bm)
        gdi32.DeleteDC(hdc_mem)
        time.sleep(1.0)

# --- Main Entry ---

def main():
    print("This Is The MEMZ Simulation (Safe Python Version)")
    print("Press Ctrl+C to stop.")
    
    init_dpi()
    sw, sh = get_screen_size()

    # Start all background tasks as daemon threads
    threading.Thread(target=play_error_sound, daemon=True).start()
    threading.Thread(target=show_message_box, daemon=True).start()
    threading.Thread(target=draw_cursor_icon, daemon=True).start()
    threading.Thread(target=shake_cursor, daemon=True).start()
    threading.Thread(target=move_screen_chunks, daemon=True).start()

    hdc = user32.GetDC(0)
    last_toggle = time.time()
    current_rop = SRCCOPY

    try:
        while True:
            draw_random_icons()

            # Handle the tunneling / inverting logic
            now = time.time()
            elapsed = now - last_toggle

            if current_rop == SRCCOPY:
                if elapsed >= 0.99: # Toggle invert every ~1 second
                    current_rop = NOTSRCCOPY
                    last_toggle = now
            else:
                if elapsed >= 0.01: # Stay inverted for a very short pulse
                    current_rop = SRCCOPY
                    last_toggle = now

            # The Tunneling Effect (StretchBlt)
            offset = 12
            gdi32.StretchBlt(
                hdc, offset, offset, sw - 2 * offset, sh - 2 * offset,
                hdc, 0, 0, sw, sh, current_rop
            )

            time.sleep(0.5)
            
    except KeyboardInterrupt:
        user32.ReleaseDC(0, hdc)
        print("\nStopped. Refresh your desktop to clear icons.")

if __name__ == "__main__":
    main()