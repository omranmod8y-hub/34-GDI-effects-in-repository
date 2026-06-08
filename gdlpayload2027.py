import ctypes
from ctypes import wintypes
import math
import random
import time
import threading
import sys

# Windows constants
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020
PATINVERT = 0x5A0049
SRCINVERT = 0x00660046
NOTSRCCOPY = 0x00330008
MB_YESNO = 0x00000004
MB_ICONWARNING = 0x00000030
MB_SYSTEMMODAL = 0x00001000
IDYES = 6
VK_ESCAPE = 0x1B

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
winmm = ctypes.windll.winmm

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

# ============ BYTEBEAT SOUNDS ============

def play_bytebeat(beat_num, duration=8):
    """Play bytebeat sound"""
    def play():
        try:
            sample_rate = 16000
            samples = int(sample_rate * duration)
            audio = bytearray()
            
            for t in range(samples):
                if beat_num == 1:
                    val = ((t >> 4) * t & (t >> 3 ^ t >> 4) + (t >> 5 | t >> 2)) & 0xFF
                elif beat_num == 2:
                    val = (t * (42 & t >> 10)) & 0xFF
                elif beat_num == 3:
                    val = ((t & 4096 and (t * (t ^ t % 9) | t >> 3) >> 1 or 255)) & 0xFF
                elif beat_num == 4:
                    val = ((t >> 6 | t | t >> (t >> 16)) * 10 + ((t >> 11) & 7)) & 0xFF
                elif beat_num == 5:
                    val = (t * (t >> 5 | t >> 8) | t >> 80 ^ t) & 0xFF
                elif beat_num == 6:
                    val = ((t >> 1) * (15 & (0x234568a0 >> ((t >> 8) & 28)))) & 0xFF
                elif beat_num == 7:
                    val = ((t >> 4) * (t & 0xFF) >> 8) & 0xFF
                else:
                    val = (t * (t ^ t + (t >> 15 | 1))) & 0xFF
                
                audio.append(val)
            
            import tempfile
            import wave
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_name = temp_file.name
            
            with wave.open(temp_name, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(1)
                wav.setframerate(sample_rate)
                wav.writeframes(bytes(audio))
            
            winmm.PlaySoundW(temp_name, 0, 1)  # SND_ASYNC
            time.sleep(duration)
        except:
            pass
    
    threading.Thread(target=play, daemon=True).start()

# ============ GDI PAYLOADS (REAL DESKTOP) ============

def payload_wave(hdc, w, h, frame):
    """Wave distortion"""
    angle = frame / 10.0
    for y in range(h):
        offset = int(math.sin(angle + y / 30) * 40)
        gdi32.BitBlt(hdc, offset, y, w, 1, hdc, 0, y, SRCCOPY)
    return frame + 1

def payload_glitch(hdc, w, h, frame):
    """Glitch effect"""
    for _ in range(30):
        y = random.randint(0, h - 50)
        height = random.randint(20, 80)
        shift = random.randint(-80, 80)
        gdi32.BitBlt(hdc, shift, y, w, height, hdc, 0, y, SRCCOPY)
    return frame + 1

def payload_invert(hdc, w, h, frame):
    """Screen invert"""
    gdi32.PatBlt(hdc, 0, 0, w, h, PATINVERT)
    return frame + 1

def payload_shake(hdc, w, h, frame):
    """Screen shake"""
    ox = random.randint(-10, 10)
    oy = random.randint(-10, 10)
    gdi32.BitBlt(hdc, ox, oy, w, h, hdc, 0, 0, SRCCOPY)
    return frame + 1

def payload_zoom(hdc, w, h, frame):
    """Zoom effect"""
    zoom = abs(math.sin(frame / 30)) * 0.6 + 0.4
    nw, nh = int(w * zoom), int(h * zoom)
    x, y = (w - nw) // 2, (h - nh) // 2
    if nw > 0 and nh > 0:
        gdi32.StretchBlt(hdc, x, y, nw, nh, hdc, 0, 0, w, h, SRCCOPY)
    return frame + 1

def payload_rainbow(hdc, w, h, frame):
    """Rainbow effect"""
    for y in range(h):
        hue = (frame / 50.0 + y / float(h)) % 1.0
        if hue < 1.0/6.0:
            r, g, b = 255, int(255 * hue * 6), 0
        elif hue < 2.0/6.0:
            r, g, b = int(255 * (2.0/3.0 - hue * 6)), 255, 0
        elif hue < 3.0/6.0:
            r, g, b = 0, 255, int(255 * (hue * 6 - 2))
        elif hue < 4.0/6.0:
            r, g, b = 0, int(255 * (4.0/3.0 - hue * 6)), 255
        elif hue < 5.0/6.0:
            r, g, b = int(255 * (hue * 6 - 4)), 0, 255
        else:
            r, g, b = 255, 0, int(255 * (2 - hue * 6))
        color = (b << 16) | (g << 8) | r
        brush = gdi32.CreateSolidBrush(color)
        rect = wintypes.RECT(0, y, w, y + 1)
        user32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
    return frame + 1

def payload_pixelate(hdc, w, h, frame):
    """Pixelate effect"""
    size = max(4, 8 + int(math.sin(frame / 20) * 4))
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    for y in range(0, h, size):
        for x in range(0, w, size):
            color = gdi32.GetPixel(hdc_mem, x, y)
            if color != -1:
                for dy in range(min(size, h - y)):
                    for dx in range(min(size, w - x)):
                        gdi32.SetPixel(hdc, x + dx, y + dy, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def payload_negative(hdc, w, h, frame):
    """Negative effect"""
    gdi32.BitBlt(hdc, 0, 0, w, h, hdc, 0, 0, NOTSRCCOPY)
    return frame + 1

# ============ MAIN ============

def main():
    print("=" * 70)
    print("REAL DESKTOP GDI PAYLOADS + BYTEBEAT")
    print("=" * 70)
    print("⚠️ THIS WILL AFFECT YOUR ACTUAL SCREEN! ⚠️")
    print("Press ESC to stop at any time")
    print("=" * 70)
    
    result = user32.MessageBoxW(0, 
        "⚠️ REAL DESKTOP GDI ⚠️\n\n"
        "This WILL affect your ACTUAL screen!\n"
        "Press ESC to stop.\n\n"
        "Continue?",
        "Desktop GDI", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled")
        return
    
    result = user32.MessageBoxW(0,
        "⚠️ LAST WARNING ⚠️\n\n"
        "Your screen WILL be affected!\n"
        "Sounds WILL play!\n\n"
        "ARE YOU ABSOLUTELY SURE?",
        "FINAL WARNING", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled")
        return
    
    w, h = get_screen_size()
    print(f"Screen: {w}x{h}")
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    hdc = user32.GetDC(0)
    if not hdc:
        print("Failed!")
        return
    
    # Backup screen
    hdc_backup = gdi32.CreateCompatibleDC(hdc)
    hbm_backup = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_backup, hbm_backup)
    gdi32.BitBlt(hdc_backup, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    payloads = [
        ("🌊 Wave", payload_wave, 1, 6),
        ("⚡ Glitch", payload_glitch, 2, 5),
        ("🔄 Invert", payload_invert, 3, 4),
        ("📱 Shake", payload_shake, 4, 5),
        ("🔍 Zoom", payload_zoom, 5, 6),
        ("🌈 Rainbow", payload_rainbow, 6, 8),
        ("📷 Pixelate", payload_pixelate, 7, 6),
        ("🎨 Negative", payload_negative, 8, 4),
    ]
    
    frame = 0
    
    print("\n" + "=" * 50)
    print("🚀 GDI PAYLOADS STARTED!")
    print("Press ESC to stop")
    print("=" * 50)
    
    try:
        for i, (name, payload, sound_num, duration) in enumerate(payloads):
            print(f"[{i+1}/{len(payloads)}] {name} ({duration}s)")
            
            # Start sound
            play_bytebeat(sound_num, duration)
            
            start_time = time.time()
            
            while time.time() - start_time < duration:
                if user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
                    print("\nESC pressed!")
                    raise KeyboardInterrupt
                
                frame = payload(hdc, w, h, frame)
                time.sleep(0.033)
            
            # Restore between effects
            gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
            time.sleep(0.3)
        
        print("\n✅ All payloads completed!")
        
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        print("\nRestoring screen...")
        gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
        user32.InvalidateRect(0, None, 0)
        
        gdi32.DeleteObject(hbm_backup)
        gdi32.DeleteDC(hdc_backup)
        user32.ReleaseDC(0, hdc)
        
        print("Screen restored!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")