import ctypes
from ctypes import wintypes
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

# Load Windows libraries
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

def get_screen_rect():
    """Get the actual screen bounds (supports multi-monitor)"""
    return RECT(
        user32.GetSystemMetrics(SM_CXSCREEN),
        user32.GetSystemMetrics(SM_CYSCREEN),
        user32.GetSystemMetrics(SM_CXSCREEN),
        user32.GetSystemMetrics(SM_CYSCREEN)
    )

def plgblt_effect(hdc, w, h, t):
    """PlgBlt parallelogram transformation effect - REAL DESKTOP"""
    
    # Calculate screen bounds with offsets (like original C#)
    left = 0
    top = 0
    right = w
    bottom = h
    
    # Create 3 points for parallelogram transformation
    # This creates a warped/tilted parallelogram effect
    points = (POINT * 3)()
    
    # First point: top-left area (shifted right and up)
    points[0].x = (left + 50) + (t % 100)  # Animated X offset
    points[0].y = (top - 50) + (t % 50)    # Animated Y offset
    
    # Second point: top-right area (shifted right and down)
    points[1].x = (right + 50) - (t % 100)  # Animated X offset
    points[1].y = (top + 50) + (t % 50)     # Animated Y offset
    
    # Third point: bottom-left area (shifted left)
    points[2].x = (left - 50) + (t % 50)    # Animated X offset
    points[2].y = (bottom - 50) - (t % 50)  # Animated Y offset
    
    # Source rectangle (slightly expanded)
    src_left = left - 20
    src_top = top - 20
    src_width = (right - left) + 40
    src_height = (bottom - top) + 40
    
    # Apply PlgBlt - transforms the screen into a parallelogram
    # Parameters: dest DC, dest points, src DC, src x, src y, src w, src h, mask, mask x, mask y
    gdi32.PlgBlt(
        hdc,                    # Destination DC
        points,                 # Destination parallelogram points
        hdc,                    # Source DC
        src_left,               # Source X
        src_top,                # Source Y
        src_width,              # Source Width
        src_height,             # Source Height
        None,                   # Mask bitmap (None)
        0,                      # Mask X
        0                       # Mask Y
    )
    
    return t + 5  # Increment for animation

def plgblt_rotate_effect(hdc, w, h, t):
    """Rotating parallelogram effect"""
    left = 0
    top = 0
    right = w
    bottom = h
    
    points = (POINT * 3)()
    
    # Animated offsets using sine waves
    import math
    angle = t / 30.0
    
    # Create a rotating/distorting parallelogram
    points[0].x = int(left + 50 + math.sin(angle) * 80)
    points[0].y = int(top - 50 + math.cos(angle * 0.7) * 40)
    
    points[1].x = int(right + 50 - math.sin(angle + 2) * 80)
    points[1].y = int(top + 50 + math.sin(angle) * 40)
    
    points[2].x = int(left - 50 + math.cos(angle) * 40)
    points[2].y = int(bottom - 50 - math.cos(angle * 0.5) * 60)
    
    src_left = left - 20
    src_top = top - 20
    src_width = (right - left) + 40
    src_height = (bottom - top) + 40
    
    gdi32.PlgBlt(hdc, points, hdc, src_left, src_top, src_width, src_height, None, 0, 0)
    
    return t + 1

def plgblt_stretch_effect(hdc, w, h, t):
    """Stretching parallelogram effect"""
    left = 0
    top = 0
    right = w
    bottom = h
    
    points = (POINT * 3)()
    
    # Stretch effect - points move outward/inward
    stretch = abs(math.sin(t / 40)) * 150
    
    points[0].x = int(left + 50 - stretch * 0.5)
    points[0].y = int(top - 50 + stretch * 0.3)
    
    points[1].x = int(right + 50 + stretch * 0.5)
    points[1].y = int(top + 50 - stretch * 0.2)
    
    points[2].x = int(left - 50 + stretch * 0.3)
    points[2].y = int(bottom - 50 + stretch * 0.4)
    
    src_left = left - 20
    src_top = top - 20
    src_width = (right - left) + 40
    src_height = (bottom - top) + 40
    
    gdi32.PlgBlt(hdc, points, hdc, src_left, src_top, src_width, src_height, None, 0, 0)
    
    return t + 1

# ============ MAIN ============

def main():
    print("=" * 70)
    print("PlgBlt PARALLELOGRAM EFFECT - REAL DESKTOP")
    print("=" * 70)
    print("⚠️ THIS WILL DISTORT YOUR ACTUAL SCREEN! ⚠️")
    print("Press Ctrl+C in terminal to stop")
    print("=" * 70)
    
    # First warning
    result = user32.MessageBoxW(0, 
        "⚠️ PlgBlt PARALLELOGRAM EFFECT ⚠️\n\n"
        "This WILL distort your ACTUAL DESKTOP screen!\n"
        "Creates a warped/tilted parallelogram effect.\n\n"
        "Press Ctrl+C in terminal to stop anytime.\n\n"
        "Continue?",
        "PlgBlt Effect - REAL DESKTOP", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled by user")
        return
    
    # Second warning
    result = user32.MessageBoxW(0,
        "⚠️ LAST WARNING ⚠️\n\n"
        "Your screen will be transformed into a parallelogram!\n"
        "This is a REAL desktop effect.\n\n"
        "ARE YOU ABSOLUTELY SURE?",
        "FINAL WARNING", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled at last warning")
        return
    
    # Get screen size
    w = user32.GetSystemMetrics(SM_CXSCREEN)
    h = user32.GetSystemMetrics(SM_CYSCREEN)
    print(f"Screen: {w}x{h}")
    print("Starting PlgBlt effects in 3 seconds...")
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
    
    # Effects list
    effects = [
        ("Moving Parallelogram", plgblt_effect, 8),
        ("Rotating Parallelogram", plgblt_rotate_effect, 10),
        ("Stretching Parallelogram", plgblt_stretch_effect, 10),
    ]
    
    t = 0
    
    print("\n" + "=" * 50)
    print("STARTING PlgBlt EFFECTS ON REAL DESKTOP")
    print("Your screen will be transformed!")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        for i, (name, effect, duration) in enumerate(effects):
            print(f"[{i+1}/{len(effects)}] {name} ({duration} seconds)")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                t = effect(hdc, w, h, t)
                time.sleep(0.033)  # ~30 FPS
                
                # Check for ESC key to stop
                if user32.GetAsyncKeyState(0x1B) & 0x8000:
                    print("\nESC pressed - stopping!")
                    break
            
            # Restore backup between effects
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
        
        print("Screen restored!")
        user32.MessageBoxW(0, "PlgBlt Effect Complete!\n\nScreen restored to normal.", 
                          "Complete", 0x00000040)

if __name__ == "__main__":
    main()