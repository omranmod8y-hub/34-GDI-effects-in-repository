import win32gui
import win32con
import win32api
import random
import time

def glitch_25_seconds():
    # 1. Setup
    hdc = win32gui.GetDC(0)
    sw = win32api.GetSystemMetrics(0)
    sh = win32api.GetSystemMetrics(1)
    
    duration = 25  # Set duration to 25 seconds
    start_time = time.time()
    
    print(f"Glitch loop started. Running for {duration} seconds...")
    print("Move mouse to (0,0) (top-left) to stop early.")

    try:
        # 2. The Loop
        while time.time() - start_time < duration:
            # --- EMERGENCY STOP ---
            cursor_pos = win32api.GetCursorPos()
            if cursor_pos[0] == 0 and cursor_pos[1] == 0:
                print("Emergency stop triggered.")
                break

            # --- GLITCH LOGIC ---
            # Pick random coordinates and size
            x = random.randint(0, sw)
            y = random.randint(0, sh)
            w = random.randint(100, 500)
            h = random.randint(100, 500)
            
            # Draw a portion of the screen slightly shifted
            win32gui.BitBlt(
                hdc, 
                x + random.randint(-20, 20), 
                y + random.randint(-20, 20), 
                w, h, 
                hdc, 
                x, y, 
                win32con.SRCCOPY
            )
            
            # Speed of the glitch (25ms delay makes it smooth but glitchy)
            time.sleep(0.025)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    
    finally:
        # 3. Cleanup (The 'Safe' part)
        # Refresh the screen to remove all visual artifacts
        win32gui.InvalidateRect(0, None, True)
        win32gui.ReleaseDC(0, hdc)
        print("25 seconds completed. Screen cleaned.")

if __name__ == "__main__":
    glitch_25_seconds()