import ctypes
from ctypes import wintypes
import random
import time
import threading

# Windows constants
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020

# Icon IDs
IDI_APPLICATION = 32512
IDI_HAND = 32513
IDI_QUESTION = 32514
IDI_EXCLAMATION = 32515
IDI_ASTERISK = 32516
IDI_WARNING = IDI_EXCLAMATION
IDI_ERROR = IDI_HAND
IDI_INFORMATION = IDI_ASTERISK

# Load libraries
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def draw_random_icons():
    """Draw random Windows icons at random positions on screen"""
    hdc = user32.GetDC(0)
    if not hdc:
        return
    
    screen_width = user32.GetSystemMetrics(SM_CXSCREEN)
    screen_height = user32.GetSystemMetrics(SM_CYSCREEN)
    
    x = random.randint(0, screen_width - 1)
    y = random.randint(0, screen_height - 1)
    
    icon_ids = [IDI_ERROR, IDI_WARNING, IDI_INFORMATION, IDI_APPLICATION]
    icon_choice = random.randint(0, 3)
    
    h_icon = user32.LoadIconW(0, icon_ids[icon_choice])
    if h_icon:
        user32.DrawIcon(hdc, x, y, h_icon)
    
    user32.ReleaseDC(0, hdc)

def move_random_screen_chunks():
    """Continuously move random screen chunks around"""
    while True:
        hdc = user32.GetDC(0)
        
        screen_width = user32.GetSystemMetrics(SM_CXSCREEN)
        screen_height = user32.GetSystemMetrics(SM_CYSCREEN)
        
        chunk_width = screen_width // 2
        chunk_height = screen_height // 2
        
        source_x = random.randint(0, screen_width - chunk_width - 1)
        source_y = random.randint(0, screen_height - chunk_height - 1)
        
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        
        dest_x = source_x + offset_x
        dest_y = source_y + offset_y
        
        dest_x = max(0, min(dest_x, screen_width - chunk_width))
        dest_y = max(0, min(dest_y, screen_height - chunk_height))
        
        gdi32.BitBlt(hdc, dest_x, dest_y, chunk_width, chunk_height,
                    hdc, source_x, source_y, SRCCOPY)
        
        user32.ReleaseDC(0, hdc)
        time.sleep(0)

def icon_drawing_loop():
    """Loop for drawing icons at regular intervals"""
    while True:
        draw_random_icons()
        time.sleep(0.05)  # 50ms delay

def main():
    random.seed(time.time())
    
    move_thread = threading.Thread(target=move_random_screen_chunks, daemon=True)
    icon_thread = threading.Thread(target=icon_drawing_loop, daemon=True)
    
    move_thread.start()
    icon_thread.start()
    
    input("Press Enter to exit...\n")

if __name__ == "__main__":
    main()