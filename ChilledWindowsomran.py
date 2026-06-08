import win32gui
import win32api
import win32con
import time

def flip_screen():
    # 1. Get the handle to the desktop window
    hwnd = win32gui.GetDesktopWindow()
    
    # 2. Get the Device Context (DC) of the desktop
    hdc = win32gui.GetWindowDC(hwnd)
    
    # 3. Get screen resolution (Width and Height)
    x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    print("Screen flipping started. Press Ctrl+C in the terminal to stop.")

    try:
        while True:
            # StretchBlt parameters:
            # (DestDC, x, y, width, height, SrcDC, sx, sy, swidth, sheight, RasterOp)
            # Using -x for width and x for the starting point mirrors the screen.
            win32gui.StretchBlt(
                hdc, x, 0, -x, y, 
                hdc, 0, 0, x, y, 
                win32con.SRCCOPY
            )
            
            # Small sleep to prevent the CPU from hitting 100% 
            # and to make it "safer" to manage.
            time.sleep(0.1) 
            
    except KeyboardInterrupt:
        # 4. Clean up: Release the DC when done
        win32gui.ReleaseDC(hwnd, hdc)
        print("\nStopped. Refresh your desktop (F5) or change wallpaper to clear glitches.")

if __name__ == "__main__":
    flip_screen()