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

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

def vertical_wave_fixed(hdc, w, h, frame, amplitude=40, frequency=30):
    """
    Vertical wave effect - shifts columns up/down like a wave
    amplitude: how far columns shift (default 40)
    frequency: wave frequency (default 30)
    """
    # Create memory DC for backup
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    
    # Capture current screen
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    # Apply vertical wave - shift each column based on sine wave
    angle = frame / 10.0
    for x in range(w):
        # Calculate offset for this column
        offset = int(math.sin(angle + x / frequency) * amplitude)
        # Shift the entire column up or down
        gdi32.BitBlt(hdc, x, offset, 1, h, hdc_mem, x, 0, SRCCOPY)
    
    # Cleanup
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def vertical_wave_animated(hdc, w, h, frame):
    """Vertical wave with changing amplitude"""
    amplitude = int(abs(math.sin(frame / 30)) * 60) + 10
    return vertical_wave_fixed(hdc, w, h, frame, amplitude, 30)

def vertical_wave_fast(hdc, w, h, frame):
    """Vertical wave - faster oscillation"""
    amplitude = 50
    frequency = 15
    return vertical_wave_fixed(hdc, w, h, frame, amplitude, frequency)

def vertical_wave_slow(hdc, w, h, frame):
    """Vertical wave - slower oscillation"""
    amplitude = 30
    frequency = 60
    return vertical_wave_fixed(hdc, w, h, frame, amplitude, frequency)

def vertical_wave_strong(hdc, w, h, frame):
    """Strong vertical wave - large amplitude"""
    amplitude = int(abs(math.sin(frame / 25)) * 100) + 20
    frequency = 25
    return vertical_wave_fixed(hdc, w, h, frame, amplitude, frequency)

def vertical_wave_double(hdc, w, h, frame):
    """Double wave - two frequencies combined"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    angle = frame / 8.0
    for x in range(w):
        # Combine two sine waves
        offset1 = int(math.sin(angle + x / 20) * 30)
        offset2 = int(math.sin(angle * 1.5 + x / 40) * 20)
        offset = offset1 + offset2
        gdi32.BitBlt(hdc, x, offset, 1, h, hdc_mem, x, 0, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def vertical_wave_reverse(hdc, w, h, frame):
    """Reverse vertical wave - columns move opposite direction"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    angle = frame / 10.0
    for x in range(w):
        # Negative offset for reverse wave
        offset = -int(math.sin(angle + x / 30) * 40)
        gdi32.BitBlt(hdc, x, offset, 1, h, hdc_mem, x, 0, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def vertical_wave_pulse(hdc, w, h, frame):
    """Pulsing vertical wave - amplitude pulses"""
    pulse = abs(math.sin(frame / 20))
    amplitude = int(pulse * 80) + 10
    return vertical_wave_fixed(hdc, w, h, frame, amplitude, 30)

# ============ MAIN ============

def main():
    print("=" * 70)
    print("VERTICAL WAVE EFFECT - REAL DESKTOP")
    print("=" * 70)
    print("⚠️ THIS WILL AFFECT YOUR ACTUAL SCREEN! ⚠️")
    print("Columns will shift up and down like a wave")
    print("Press Ctrl+C in terminal to stop")
    print("=" * 70)
    
    # First warning
    result = user32.MessageBoxW(0, 
        "⚠️ VERTICAL WAVE EFFECT ⚠️\n\n"
        "This will create a VERTICAL WAVE on your ACTUAL DESKTOP!\n"
        "Columns will shift up and down like a wave.\n\n"
        "Press Ctrl+C in terminal to stop anytime.\n\n"
        "Continue?",
        "Vertical Wave - REAL DESKTOP", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled by user")
        return
    
    # Second warning
    result = user32.MessageBoxW(0,
        "⚠️ LAST WARNING ⚠️\n\n"
        "Your screen will have a VERTICAL WAVE effect!\n"
        "This is a REAL desktop effect.\n\n"
        "ARE YOU ABSOLUTELY SURE?",
        "FINAL WARNING", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled at last warning")
        return
    
    # Get screen size
    w, h = get_screen_size()
    print(f"Screen: {w}x{h}")
    print("Starting vertical wave effects in 3 seconds...")
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
        ("📊 Standard Vertical Wave", vertical_wave_fixed, 8),
        ("🎚️ Animated Amplitude Wave", vertical_wave_animated, 8),
        ("⚡ Fast Wave", vertical_wave_fast, 6),
        ("🐢 Slow Wave", vertical_wave_slow, 8),
        ("💪 Strong Wave", vertical_wave_strong, 8),
        ("🔄 Double Wave", vertical_wave_double, 8),
        ("⬇️ Reverse Wave", vertical_wave_reverse, 6),
        ("💓 Pulsing Wave", vertical_wave_pulse, 8),
    ]
    
    frame = 0
    
    print("\n" + "=" * 50)
    print("STARTING VERTICAL WAVE EFFECTS ON REAL DESKTOP")
    print("Your screen columns will wave up and down!")
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
        user32.MessageBoxW(0, "Vertical Wave Effect Complete!\n\nScreen restored to normal.", 
                          "Complete", 0x00000040)

if __name__ == "__main__":
    main()