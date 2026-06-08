import ctypes
from ctypes import wintypes
import math
import random
import time
import sys

# Windows constants
SRCCOPY = 0x00CC0020
PATINVERT = 0x5A0049
SRCINVERT = 0x00660046
SRCPAINT = 0x00EE0086
NOTSRCCOPY = 0x00330008
SM_CXSCREEN = 0
SM_CYSCREEN = 1
MB_YESNO = 0x00000004
MB_ICONEXCLAMATION = 0x00000030
MB_ICONWARNING = 0x00000030
MB_SYSTEMMODAL = 0x00001000
IDYES = 6

# Load Windows libraries
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

def create_compatible_dc(hdc):
    return gdi32.CreateCompatibleDC(hdc)

def create_compatible_bitmap(hdc, width, height):
    return gdi32.CreateCompatibleBitmap(hdc, width, height)

# ============ REAL DESKTOP GDI EFFECTS ============

def effect_wave_shake(hdc, width, height, frame):
    """Wave distortion effect - shifts rows horizontally"""
    angle = frame / 10.0
    for y in range(height):
        offset = int(math.sin(angle + y / 30) * 40)
        gdi32.BitBlt(hdc, offset, y, width, 1, hdc, 0, y, SRCCOPY)
    return frame + 1

def effect_vertical_wave(hdc, width, height, frame):
    """Vertical wave distortion - shifts columns vertically"""
    angle = frame / 10.0
    for x in range(width):
        offset = int(math.sin(angle + x / 30) * 40)
        gdi32.BitBlt(hdc, x, offset, 1, height, hdc, x, 0, SRCCOPY)
    return frame + 1

def effect_glitch(hdc, width, height, frame):
    """Glitch effect - random row shifts"""
    for _ in range(50):
        y = random.randint(0, height - 20)
        h = random.randint(10, 60)
        shift = random.randint(-80, 80)
        gdi32.BitBlt(hdc, shift, y, width, h, hdc, 0, y, SRCCOPY)
    return frame + 1

def effect_invert(hdc, width, height, frame):
    """Screen invert effect"""
    gdi32.PatBlt(hdc, 0, 0, width, height, PATINVERT)
    return frame + 1

def effect_shake(hdc, width, height, frame):
    """Screen shake effect"""
    hdc_mem = create_compatible_dc(hdc)
    hbm = create_compatible_bitmap(hdc, width, height)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc, 0, 0, SRCCOPY)
    ox, oy = random.randint(-15, 15), random.randint(-15, 15)
    gdi32.BitBlt(hdc, ox, oy, width, height, hdc_mem, 0, 0, SRCCOPY)
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def effect_zoom(hdc, width, height, frame):
    """Zoom in/out effect"""
    zoom = abs(math.sin(frame / 30)) * 0.7 + 0.3
    nw, nh = int(width * zoom), int(height * zoom)
    x, y = (width - nw) // 2, (height - nh) // 2
    if nw > 0 and nh > 0:
        gdi32.StretchBlt(hdc, x, y, nw, nh, hdc, 0, 0, width, height, SRCCOPY)
    return frame + 1

def effect_pixelate(hdc, width, height, frame):
    """Pixelation effect"""
    size = max(2, 5 + int(math.sin(frame / 20) * 10))
    hdc_mem = create_compatible_dc(hdc)
    hbm = create_compatible_bitmap(hdc, width, height)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc, 0, 0, SRCCOPY)
    
    for y in range(0, height, size):
        for x in range(0, width, size):
            color = gdi32.GetPixel(hdc_mem, x, y)
            if color != -1:
                for dy in range(min(size, height - y)):
                    for dx in range(min(size, width - x)):
                        gdi32.SetPixel(hdc, x + dx, y + dy, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def effect_tunnel(hdc, width, height, frame):
    """Tunnel/radial effect"""
    hdc_mem = create_compatible_dc(hdc)
    hbm = create_compatible_bitmap(hdc, width, height)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc, 0, 0, SRCCOPY)
    
    cx, cy = width // 2, height // 2
    for y in range(height):
        for x in range(width):
            dx, dy = x - cx, y - cy
            angle = math.atan2(dy, dx)
            dist = math.sqrt(dx * dx + dy * dy)
            u = int((angle + frame / 20) / (2 * math.pi) * width) % width
            v = int(dist * 2) % height
            color = gdi32.GetPixel(hdc_mem, u, v)
            if color != -1:
                gdi32.SetPixel(hdc, x, y, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def effect_swirl(hdc, width, height, frame):
    """Swirl distortion effect"""
    hdc_mem = create_compatible_dc(hdc)
    hbm = create_compatible_bitmap(hdc, width, height)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc, 0, 0, SRCCOPY)
    
    cx, cy = width // 2, height // 2
    for y in range(height):
        for x in range(width):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            angle = math.atan2(dy, dx) + dist * 0.02 - frame / 30
            u = int(cx + math.cos(angle) * dist) % width
            v = int(cy + math.sin(angle) * dist) % height
            color = gdi32.GetPixel(hdc_mem, u, v)
            if color != -1:
                gdi32.SetPixel(hdc, x, y, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def effect_negative(hdc, width, height, frame):
    """Negative color effect"""
    hdc_mem = create_compatible_dc(hdc)
    hbm = create_compatible_bitmap(hdc, width, height)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc, 0, 0, SRCCOPY)
    
    for y in range(height):
        for x in range(width):
            color = gdi32.GetPixel(hdc_mem, x, y)
            if color != -1:
                gdi32.SetPixel(hdc, x, y, 0xFFFFFF - color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

# ============ MAIN ============

def main():
    print("=" * 70)
    print("REAL DESKTOP GDI EFFECTS - WARNING!")
    print("=" * 70)
    print("This will affect your ACTUAL DESKTOP screen!")
    print("Press Ctrl+C in terminal to stop")
    print("=" * 70)
    
    # First warning - Critical!
    result1 = user32.MessageBoxW(0, 
        "⚠️ CRITICAL WARNING ⚠️\n\n"
        "This program will affect your ACTUAL DESKTOP screen!\n"
        "Visual effects will appear on your entire display.\n\n"
        "Press Alt+F4 or Ctrl+Alt+Del if screen becomes unusable.\n\n"
        "Do you want to continue?",
        "DESKTOP GDI EFFECTS", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result1 != IDYES:
        print("Cancelled by user")
        return
    
    # Second warning - Last chance!
    result2 = user32.MessageBoxW(0,
        "⚠️ LAST WARNING ⚠️\n\n"
        "This is NOT a simulation - your screen WILL be affected!\n"
        "Effects include: wave distortion, glitch, shake, zoom, pixelate, tunnel, swirl\n\n"
        "Press Ctrl+C in terminal to stop effects.\n\n"
        "ARE YOU ABSOLUTELY SURE?",
        "FINAL WARNING", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result2 != IDYES:
        print("Cancelled at last warning")
        user32.MessageBoxW(0, "Demo cancelled. Your screen is safe.", "Cancelled", MB_ICONEXCLAMATION)
        return
    
    print("Starting DESKTOP effects in 3 seconds...")
    print("Press Ctrl+C to stop!")
    time.sleep(3)
    
    # Get screen dimensions
    width, height = get_screen_size()
    print(f"Screen size: {width}x{height}")
    
    # Get desktop DC
    hdc = user32.GetDC(0)
    if not hdc:
        print("Failed to get desktop DC!")
        return
    
    effects = [
        ("🌊 Wave Shake", effect_wave_shake, 6),
        ("📊 Vertical Wave", effect_vertical_wave, 6),
        ("⚡ Glitch", effect_glitch, 5),
        ("🔄 Invert", effect_invert, 4),
        ("📱 Screen Shake", effect_shake, 5),
        ("🔍 Zoom", effect_zoom, 6),
        ("📷 Pixelate", effect_pixelate, 6),
        ("🌀 Tunnel", effect_tunnel, 6),
        ("🎠 Swirl", effect_swirl, 6),
        ("🎨 Negative", effect_negative, 5),
    ]
    
    frame = 0
    
    try:
        for i, (name, effect, duration) in enumerate(effects):
            print(f"[{i+1}/{len(effects)}] {name} ({duration} seconds)")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                frame = effect(hdc, width, height, frame)
                time.sleep(0.033)  # ~30 FPS
                
                # Check for exit condition
                if user32.GetAsyncKeyState(0x1B) & 0x8000:  # ESC key
                    print("\nESC pressed - stopping effects!")
                    break
            
            # Refresh screen slightly between effects
            user32.InvalidateRect(0, None, 0)
            time.sleep(0.2)
            
            if user32.GetAsyncKeyState(0x1B) & 0x8000:
                break
        
        print("\n" + "=" * 70)
        print("✅ All effects completed!")
        print("=" * 70)
        
        # Refresh screen
        user32.InvalidateRect(0, None, 0)
        user32.MessageBoxW(0, "Desktop GDI Effects Complete!\n\nYour screen should be恢复正常.", "Complete", MB_ICONINFORMATION)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user (Ctrl+C)")
        user32.InvalidateRect(0, None, 0)
        user32.MessageBoxW(0, "Effects stopped by user.\nYour screen should return to normal.", "Stopped", MB_ICONWARNING)
    finally:
        if hdc:
            user32.ReleaseDC(0, hdc)
        print("\nCleanup complete!")

if __name__ == "__main__":
    main()