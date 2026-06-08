import ctypes
import random
import time

SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def main():
    # No console window at all when run as .pyw
    screen_width = user32.GetSystemMetrics(SM_CXSCREEN)
    screen_height = user32.GetSystemMetrics(SM_CYSCREEN)
    
    hdc_screen = user32.GetDC(0)
    hdc_memory = gdi32.CreateCompatibleDC(hdc_screen)
    hbitmap = gdi32.CreateCompatibleBitmap(hdc_screen, screen_width, screen_height)
    gdi32.SelectObject(hdc_memory, hbitmap)
    
    # Capture screen
    gdi32.BitBlt(hdc_memory, 0, 0, screen_width, screen_height, 
                 hdc_screen, 0, 0, SRCCOPY)
    
    random.seed(int(time.time()))
    start = time.time()
    
    while time.time() - start < 5:
        x = random.randint(-15, 15)
        y = random.randint(-15, 15)
        gdi32.BitBlt(hdc_screen, x, y, screen_width, screen_height,
                    hdc_memory, 0, 0, SRCCOPY)
        time.sleep(0.01)
    
    # Cleanup
    gdi32.DeleteObject(hbitmap)
    gdi32.DeleteDC(hdc_memory)
    user32.ReleaseDC(0, hdc_screen)

if __name__ == "__main__":
    main()