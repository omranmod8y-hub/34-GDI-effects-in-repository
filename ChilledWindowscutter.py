import win32gui
import win32api
import win32con
import random
import time

# --- CONFIGURATION ---
DURATION = 30  # How many seconds the effect runs
EFFECT_SPEED = 0.01 # Delay between glitches (lower = faster)

def chilled_windows():
    # Get Handles
    hwnd = win32gui.GetDesktopWindow()
    hdc = win32gui.GetWindowDC(hwnd)
    
    # Get Screen Dimensions
    sw = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    sh = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    print("!!! CHILLED WINDOWS STARTED !!!")
    print(f"Running for {DURATION} seconds...")
    print("To stop early: Click this window and press Ctrl+C, or wait for the timer.")

    start_time = time.time()

    try:
        while time.time() - start_time < DURATION:
            # Pick a random effect to run
            choice = random.randint(0, 5)

            if choice == 0:
                # EFFECT: Screen Melt (Shifting a random column down)
                x = random.randint(0, sw)
                y = random.randint(0, 10)
                win32gui.BitBlt(hdc, x, y, 100, sh, hdc, x, 0, win32con.SRCCOPY)

            elif choice == 1:
                # EFFECT: Horizontal Flip (The one from your previous image)
                win32gui.StretchBlt(hdc, sw, 0, -sw, sh, hdc, 0, 0, sw, sh, win32con.SRCCOPY)

            elif choice == 2:
                # EFFECT: Invert Colors
                win32gui.PatBlt(hdc, 0, 0, sw, sh, win32con.DSTINVERT)

            elif choice == 3:
                # EFFECT: Random Icons
                ix = random.randint(0, sw)
                iy = random.randint(0, sh)
                icon = win32gui.LoadIcon(0, win32con.IDI_ERROR)
                win32gui.DrawIcon(hdc, ix, iy, icon)

            elif choice == 4:
                # EFFECT: Small jitter/shake
                win32gui.BitBlt(hdc, random.randint(-10, 10), random.randint(-10, 10), sw, sh, hdc, 0, 0, win32con.SRCCOPY)
            
            time.sleep(EFFECT_SPEED)

    except KeyboardInterrupt:
        pass

    # CLEANUP
    win32gui.ReleaseDC(hwnd, hdc)
    # Force a screen refresh to clear the glitches
    win32gui.InvalidateRect(0, None, True)
    print("\n[Finished] Screen cleared.")

if __name__ == "__main__":
    chilled_windows()