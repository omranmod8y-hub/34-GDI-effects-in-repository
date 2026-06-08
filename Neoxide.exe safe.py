import ctypes
from ctypes import wintypes
import math
import random
import time

# Windows constants
SRCCOPY = 0x00CC0020
PATINVERT = 0x5A0049
SM_CXSCREEN = 0
SM_CYSCREEN = 1
MB_YESNO = 0x00000004
MB_ICONWARNING = 0x00000030
IDYES = 6

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

def main():
    # Warning message box
    result = user32.MessageBoxW(0, 
        "⚠️ REAL DESKTOP EFFECT ⚠️\n\n"
        "This WILL affect your actual screen!\n"
        "Press Ctrl+C in terminal to stop.\n\n"
        "Continue?",
        "Desktop GDI Effect", MB_YESNO | MB_ICONWARNING)
    
    if result != IDYES:
        print("Cancelled")
        return
    
    # Get screen size
    w, h = get_screen_size()
    print(f"Screen: {w}x{h}")
    print("Press Ctrl+C to stop")
    
    # Get desktop DC (affects REAL screen)
    hdc = user32.GetDC(0)
    
    # Create memory DC for backup
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    
    # Backup original screen
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    angle = 0
    frame = 0
    
    effects = [
        ("WAVE", 1),
        ("GLITCH", 2),
        ("INVERT", 3),
        ("SHAKE", 4),
        ("TUNNEL", 5),
        ("SWIRL", 6),
    ]
    
    try:
        for effect_name, effect_type in effects:
            print(f"Running: {effect_name}")
            start_time = time.time()
            
            while time.time() - start_time < 8:
                
                if effect_type == 1:  # WAVE
                    for y in range(h):
                        offset = int(math.sin(angle + y / 30) * 50)
                        gdi32.BitBlt(hdc, offset, y, w, 1, hdc_mem, 0, y, SRCCOPY)
                    angle += 0.1
                    
                elif effect_type == 2:  # GLITCH
                    for _ in range(30):
                        y = random.randint(0, h - 50)
                        height_chunk = random.randint(20, 80)
                        shift = random.randint(-100, 100)
                        gdi32.BitBlt(hdc, shift, y, w, height_chunk, hdc_mem, 0, y, SRCCOPY)
                    
                elif effect_type == 3:  # INVERT
                    gdi32.BitBlt(hdc, 0, 0, w, h, hdc, 0, 0, PATINVERT)
                    
                elif effect_type == 4:  # SHAKE
                    ox = random.randint(-10, 10)
                    oy = random.randint(-10, 10)
                    gdi32.BitBlt(hdc, ox, oy, w, h, hdc_mem, 0, 0, SRCCOPY)
                    
                elif effect_type == 5:  # TUNNEL
                    cx, cy = w // 2, h // 2
                    for y in range(h):
                        for x in range(w):
                            dx = x - cx
                            dy = y - cy
                            dist = math.sqrt(dx*dx + dy*dy)
                            ang = math.atan2(dy, dx)
                            u = int((ang + frame/20) / (2*math.pi) * w) % w
                            v = int(dist * 3) % h
                            color = gdi32.GetPixel(hdc_mem, u, v)
                            if color != -1:
                                gdi32.SetPixel(hdc, x, y, color)
                    
                elif effect_type == 6:  # SWIRL
                    cx, cy = w // 2, h // 2
                    for y in range(h):
                        for x in range(w):
                            dx = x - cx
                            dy = y - cy
                            dist = math.sqrt(dx*dx + dy*dy)
                            ang = math.atan2(dy, dx) + dist * 0.03 - frame/20
                            u = int(cx + math.cos(ang) * dist) % w
                            v = int(cy + math.sin(ang) * dist) % h
                            color = gdi32.GetPixel(hdc_mem, u, v)
                            if color != -1:
                                gdi32.SetPixel(hdc, x, y, color)
                
                frame += 1
                time.sleep(0.033)
                
                # Restore backup for next effect
                gdi32.BitBlt(hdc, 0, 0, w, h, hdc_mem, 0, 0, SRCCOPY)
            
            # Refresh between effects
            user32.InvalidateRect(0, None, 0)
            time.sleep(0.5)
        
        # Final restore
        gdi32.BitBlt(hdc, 0, 0, w, h, hdc_mem, 0, 0, SRCCOPY)
        user32.InvalidateRect(0, None, 0)
        print("\nAll effects completed!")
        user32.MessageBoxW(0, "Desktop effects complete!\nScreen restored.", "Done", 0x00000040)
        
    except KeyboardInterrupt:
        print("\nStopping...")
        gdi32.BitBlt(hdc, 0, 0, w, h, hdc_mem, 0, 0, SRCCOPY)
        user32.InvalidateRect(0, None, 0)
    
    # Cleanup
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(0, hdc)

if __name__ == "__main__":
    main()