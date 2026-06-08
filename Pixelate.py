import ctypes
from ctypes import wintypes
import math
import random
import time
import sys

# Windows constants
SRCCOPY = 0x00CC0020
SM_CXSCREEN = 0
SM_CYSCREEN = 1
MB_YESNO = 0x00000004
MB_ICONWARNING = 0x00000030
MB_SYSTEMMODAL = 0x00001000
IDYES = 6

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

def pixelate_effect(hdc, w, h, frame, pixel_size):
    """
    Pixelate effect - makes screen blocky
    pixel_size: size of each pixel block (4 to 32)
    """
    # Create memory DC for backup
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    
    # Capture current screen
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    # Apply pixelation
    for y in range(0, h, pixel_size):
        for x in range(0, w, pixel_size):
            # Get the color of the top-left pixel in the block
            color = gdi32.GetPixel(hdc_mem, x, y)
            if color != -1:  # CLR_INVALID check
                # Fill the entire block with that color
                for dy in range(min(pixel_size, h - y)):
                    for dx in range(min(pixel_size, w - x)):
                        gdi32.SetPixel(hdc, x + dx, y + dy, color)
    
    # Cleanup
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return pixel_size

def animated_pixelate(hdc, w, h, frame):
    """Animated pixelation - size changes over time"""
    # Pixel size oscillates between 4 and 32
    pixel_size = int(abs(math.sin(frame / 20)) * 14) + 4
    return pixelate_effect(hdc, w, h, frame, pixel_size)

def growing_pixelate(hdc, w, h, frame):
    """Pixelation that grows and shrinks"""
    # Size goes from 2 to 40 and back
    t = frame / 30
    pixel_size = int(abs(math.sin(t)) * 20) + 4
    return pixelate_effect(hdc, w, h, frame, pixel_size)

def random_pixelate(hdc, w, h, frame):
    """Random pixelation size"""
    pixel_size = random.randint(4, 32)
    return pixelate_effect(hdc, w, h, frame, pixel_size)

def progressive_pixelate(hdc, w, h, frame):
    """Progressive pixelation - gets blockier over time"""
    # Size increases from 4 to 40 over time
    pixel_size = min(40, 4 + int(frame / 10))
    return pixelate_effect(hdc, w, h, frame, pixel_size)

def reverse_pixelate(hdc, w, h, frame):
    """Reverse pixelation - starts blocky, gets clearer"""
    # Size decreases from 40 to 4 over time
    pixel_size = max(4, 40 - int(frame / 10))
    return pixelate_effect(hdc, w, h, frame, pixel_size)

def mosaic_pixelate(hdc, w, h, frame):
    """Mosaic effect - different pixel sizes in different areas"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    # Center area has smaller pixels, edges have larger
    cx, cy = w // 2, h // 2
    
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            # Calculate distance from center
            dx = abs(x - cx)
            dy = abs(y - cy)
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Pixel size based on distance
            pixel_size = max(4, min(24, int(dist / 20) + 4))
            
            color = gdi32.GetPixel(hdc_mem, x, y)
            if color != -1:
                for dy in range(min(pixel_size, h - y)):
                    for dx in range(min(pixel_size, w - x)):
                        gdi32.SetPixel(hdc, x + dx, y + dy, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

# ============ MAIN ============

def main():
    print("=" * 70)
    print("PIXELATE EFFECT - REAL DESKTOP")
    print("=" * 70)
    print("⚠️ THIS WILL PIXELATE YOUR ACTUAL SCREEN! ⚠️")
    print("Press Ctrl+C in terminal to stop")
    print("=" * 70)
    
    # First warning
    result = user32.MessageBoxW(0, 
        "⚠️ PIXELATE EFFECT ⚠️\n\n"
        "This will PIXELATE your ACTUAL DESKTOP screen!\n"
        "Your screen will become blocky.\n\n"
        "Press Ctrl+C in terminal to stop anytime.\n\n"
        "Continue?",
        "Pixelate - REAL DESKTOP", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled by user")
        return
    
    # Second warning
    result = user32.MessageBoxW(0,
        "⚠️ LAST WARNING ⚠️\n\n"
        "Your screen will become PIXELATED!\n"
        "This is a REAL desktop effect.\n\n"
        "ARE YOU ABSOLUTELY SURE?",
        "FINAL WARNING", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled at last warning")
        return
    
    # Get screen size
    w, h = get_screen_size()
    print(f"Screen: {w}x{h}")
    print("Starting pixelate effects in 3 seconds...")
    time.sleep(3)
    
    # Get desktop DC
    hdc = user32.GetDC(0)
    if not hdc:
        print("Failed to get desktop DC!")
        return
    
    # Backup original screen
    hdc_backup = gdi32.CreateCompatibleDC(hdc)
    hbm_backup = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_backup, hbm_backup)
    gdi32.BitBlt(hdc_backup, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    effects = [
        ("📷 Animated Pixelate (size changes)", animated_pixelate, 8),
        ("📈 Growing Pixelate (gets blockier)", growing_pixelate, 8),
        ("🎲 Random Pixelate", random_pixelate, 6),
        ("📊 Progressive Pixelate", progressive_pixelate, 8),
        ("📉 Reverse Pixelate (clears up)", reverse_pixelate, 8),
        ("🖼️ Mosaic Effect", mosaic_pixelate, 8),
    ]
    
    frame = 0
    
    print("\n" + "=" * 50)
    print("STARTING PIXELATE EFFECTS ON REAL DESKTOP")
    print("Your screen will become pixelated!")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        for i, (name, effect, duration) in enumerate(effects):
            print(f"[{i+1}/{len(effects)}] {name} ({duration}s)")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                frame = effect(hdc, w, h, frame)
                time.sleep(0.033)  # ~30 FPS
                
                # Check for ESC key
                if user32.GetAsyncKeyState(0x1B) & 0x8000:
                    print("\nESC pressed - stopping!")
                    break
            
            # Restore between effects
            gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
            time.sleep(0.3)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")
    finally:
        # Restore original screen
        print("\nRestoring screen...")
        gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
        user32.InvalidateRect(0, None, 0)
        time.sleep(0.5)
        
        # Cleanup
        gdi32.DeleteObject(hbm_backup)
        gdi32.DeleteDC(hdc_backup)
        user32.ReleaseDC(0, hdc)
        
        print("Screen restored to normal!")
        user32.MessageBoxW(0, "Pixelate Effect Complete!\n\nScreen restored to normal.", 
                          "Complete", 0x00000040)

if __name__ == "__main__":
    main()