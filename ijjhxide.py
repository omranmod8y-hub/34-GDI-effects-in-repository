import ctypes
from ctypes import wintypes
import math
import random
import time
import threading
import sys

# ============ CONSTANTS ============
SRCCOPY = 0x00CC0020
PATINVERT = 0x5A0049
SRCINVERT = 0x00660046
SRCPAINT = 0x00EE0086
NOTSRCCOPY = 0x00330008
SM_CXSCREEN = 0
SM_CYSCREEN = 1
MB_YESNO = 0x00000004
MB_ICONWARNING = 0x00000030
MB_TOPMOST = 0x00040000
IDYES = 6

PAYLOAD_TIME = 8  # seconds per payload

# Load Windows libraries
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class RGBQUAD(ctypes.Structure):
    _fields_ = [("rgbBlue", ctypes.c_ubyte), ("rgbGreen", ctypes.c_ubyte),
                ("rgbRed", ctypes.c_ubyte), ("rgbReserved", ctypes.c_ubyte)]

# ============ XORSHIFT32 RNG ============
xs = int(time.time() * 1000)

def xorshift32():
    global xs
    xs ^= (xs << 13) & 0xFFFFFFFF
    xs ^= (xs >> 17) & 0xFFFFFFFF
    xs ^= (xs << 5) & 0xFFFFFFFF
    return xs

def random_range(min_val, max_val):
    return min_val + (xorshift32() % (max_val - min_val + 1))

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

# ============ BYTEBEAT AUDIO ============
try:
    import pyaudio
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False
    print("PyAudio not installed - Install with: pip install pyaudio")

def audio_sequence1(sample_rate, duration):
    """Bytebeat audio 1"""
    samples = int(sample_rate * duration)
    audio = bytearray()
    for t in range(samples):
        val = (((t >> 4) * t & (t >> 3 ^ t >> 4) + (t >> 5 | t >> 2)) | (t * (t >> 3 | t >> 6) >> (t >> 5 | t >> 7))) & 0xFF
        audio.append(val)
    return bytes(audio)

def audio_sequence2(sample_rate, duration):
    samples = int(sample_rate * duration)
    audio = bytearray()
    for t in range(samples):
        val = (t * (t >> 5 | t >> 8) | t >> 80 ^ t) & 0xFF
        audio.append(val)
    return bytes(audio)

def audio_sequence3(sample_rate, duration):
    samples = int(sample_rate * duration)
    audio = bytearray()
    for t in range(samples):
        val = ((t >> 6 | t | t >> (t >> 16)) * 10 + ((t >> 11) & 7)) & 0xFF
        audio.append(val)
    return bytes(audio)

def audio_sequence4(sample_rate, duration):
    samples = int(sample_rate * duration)
    audio = bytearray()
    for t in range(samples):
        val = ((t >> 1) * (15 & (0x234568a0 >> ((t >> 8) & 28))) | ((t >> 1) >> (t >> 15)) ^ (t >> 4)) & 0xFF
        audio.append(val)
    return bytes(audio)

def audio_sequence5(sample_rate, duration):
    samples = int(sample_rate * duration)
    audio = bytearray()
    for t in range(samples):
        val = (t * (42 & t >> 10)) & 0xFF
        audio.append(val)
    return bytes(audio)

def audio_sequence6(sample_rate, duration):
    samples = int(sample_rate * duration)
    audio = bytearray()
    for t in range(samples):
        val = ((t & 4096 and (t * (t ^ t % 9) | t >> 3) >> 1 or 255)) & 0xFF
        audio.append(val)
    return bytes(audio)

def audio_sequence7(sample_rate, duration):
    samples = int(sample_rate * duration)
    audio = bytearray()
    for t in range(samples):
        val = (t * (t >> 5 | t >> 8) | t >> 80 ^ t) & 0xFF
        audio.append(val)
    return bytes(audio)

def audio_sequence8(sample_rate, duration):
    samples = int(sample_rate * duration)
    audio = bytearray()
    for t in range(samples):
        val = ((t >> 4) * (t & 0xFF) >> 8) & 0xFF
        audio.append(val)
    return bytes(audio)

def audio_sequence9(sample_rate, duration):
    samples = int(sample_rate * duration)
    audio = bytearray()
    for t in range(samples):
        val = (((t >> 8) & 0xFF) * ((t >> 4) & 0xF) ^ (t >> 10)) & 0xFF
        audio.append(val)
    return bytes(audio)

def audio_sequence10(sample_rate, duration):
    samples = int(sample_rate * duration)
    audio = bytearray()
    for t in range(samples):
        val = ((t >> 7 | t | t >> 9) * (t >> 11 | t >> 14)) & 0xFF
        audio.append(val)
    return bytes(audio)

def play_audio_async(audio_func, duration, sample_rate=8000):
    """Play audio in background thread"""
    if not HAS_AUDIO:
        return
    
    def play():
        try:
            audio_data = audio_func(sample_rate, duration)
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt8, channels=1, rate=sample_rate, output=True)
            stream.write(audio_data)
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            pass
    
    thread = threading.Thread(target=play, daemon=True)
    thread.start()

# ============ PAYLOADS (REAL DESKTOP) ============

def payload1(hdc, w, h, t):
    """PlgBlt parallelogram effect"""
    left, top = 0, 0
    right, bottom = w, h
    
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    
    points = (POINT * 3)()
    points[0].x = left + 50 + (t % 100)
    points[0].y = top - 50 + (t % 50)
    points[1].x = right + 50 - (t % 100)
    points[1].y = top + 50 + (t % 50)
    points[2].x = left - 50 + (t % 50)
    points[2].y = bottom - 50 - (t % 50)
    
    gdi32.PlgBlt(hdc, points, hdc, left - 20, top - 20, (right - left) + 40, (bottom - top) + 40, None, 0, 0)
    return t + 5

def payload2(hdc, w, h, t):
    """Wave distortion"""
    angle = t / 10.0
    for y in range(h):
        offset = int(math.sin(angle + y / 30) * 40)
        gdi32.BitBlt(hdc, offset, y, w, 1, hdc, 0, y, SRCCOPY)
    return t + 1

def payload3(hdc, w, h, t):
    """Vertical wave"""
    angle = t / 10.0
    for x in range(w):
        offset = int(math.sin(angle + x / 30) * 40)
        gdi32.BitBlt(hdc, x, offset, 1, h, hdc, x, 0, SRCCOPY)
    return t + 1

def payload4(hdc, w, h, t):
    """Glitch effect"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    for _ in range(40):
        y = random_range(0, h - 30)
        height = random_range(10, 80)
        shift = random_range(-100, 100)
        gdi32.BitBlt(hdc, shift, y, w, height, hdc_mem, 0, y, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def payload5(hdc, w, h, t):
    """Screen invert"""
    gdi32.PatBlt(hdc, 0, 0, w, h, PATINVERT)
    return t + 1

def payload6(hdc, w, h, t):
    """Screen shake"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    ox = random_range(-12, 12)
    oy = random_range(-12, 12)
    gdi32.BitBlt(hdc, ox, oy, w, h, hdc_mem, 0, 0, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def payload7(hdc, w, h, t):
    """Zoom effect"""
    zoom = abs(math.sin(t / 30)) * 0.6 + 0.4
    nw, nh = int(w * zoom), int(h * zoom)
    x, y = (w - nw) // 2, (h - nh) // 2
    if nw > 0 and nh > 0:
        gdi32.StretchBlt(hdc, x, y, nw, nh, hdc, 0, 0, w, h, SRCCOPY)
    return t + 1

def payload8(hdc, w, h, t):
    """Pixelate effect"""
    size = max(4, 8 + int(math.sin(t / 20) * 4))
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
    return t + 1

def payload9(hdc, w, h, t):
    """Tunnel effect"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    cx, cy = w // 2, h // 2
    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            u = int((angle + t/20) / (2*math.pi) * w) % w
            v = int(dist * 3) % h
            color = gdi32.GetPixel(hdc_mem, u, v)
            if color != -1:
                gdi32.SetPixel(hdc, x, y, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

def payload10(hdc, w, h, t):
    """Swirl effect"""
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    cx, cy = w // 2, h // 2
    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx) + dist * 0.03 - t/25
            u = int(cx + math.cos(angle) * dist) % w
            v = int(cy + math.sin(angle) * dist) % h
            color = gdi32.GetPixel(hdc_mem, u, v)
            if color != -1:
                gdi32.SetPixel(hdc, x, y, color)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return t + 1

# ============ SHADERS ============

def shader1(hdc, w, h, t):
    """Color invert shader"""
    gdi32.BitBlt(hdc, 0, 0, w, h, hdc, 0, 0, NOTSRCCOPY)
    return t + 1

def shader2(hdc, w, h, t):
    """Rainbow overlay"""
    color = (int(abs(math.sin(t/20))*255) << 16) | (int(abs(math.sin(t/20+2))*255) << 8) | int(abs(math.sin(t/20+4))*255)
    brush = gdi32.CreateSolidBrush(color)
    rect = RECT(0, 0, w, h)
    gdi32.FillRect(hdc, ctypes.byref(rect), brush)
    gdi32.DeleteObject(brush)
    return t + 1

def shader3(hdc, w, h, t):
    """Scanlines"""
    for y in range(0, h, 4):
        brush = gdi32.CreateSolidBrush(0x000000)
        rect = RECT(0, y, w, y + 2)
        gdi32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
    return t + 1

def shader4(hdc, w, h, t):
    """Negative effect"""
    gdi32.BitBlt(hdc, 0, 0, w, h, hdc, 0, 0, PATINVERT)
    return t + 1

def shader5(hdc, w, h, t):
    """Random color blocks"""
    for _ in range(30):
        x = random_range(0, w - 100)
        y = random_range(0, h - 80)
        bw = random_range(50, 200)
        bh = random_range(50, 150)
        color = (random_range(0, 255) << 16) | (random_range(0, 255) << 8) | random_range(0, 255)
        brush = gdi32.CreateSolidBrush(color)
        rect = RECT(x, y, x + bw, y + bh)
        gdi32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
    return t + 1

# ============ EXECUTE FUNCTIONS ============

def execute_payload(payload_func, duration, hdc, w, h):
    """Execute a payload for specified duration"""
    t = 0
    start = time.time()
    while time.time() - start < duration:
        t = payload_func(hdc, w, h, t)
        time.sleep(0.033)
    return t

def execute_shader(shader_func, duration, hdc, w, h):
    """Execute a shader for specified duration"""
    t = 0
    start = time.time()
    while time.time() - start < duration:
        t = shader_func(hdc, w, h, t)
        time.sleep(0.033)
    return t

# ============ MAIN ============

def main():
    print("=" * 70)
    print("HYDROGEN GDI EFFECTS - REAL DESKTOP")
    print("=" * 70)
    print("⚠️ THIS WILL AFFECT YOUR ACTUAL SCREEN! ⚠️")
    print("10 payloads + 5 shaders with bytebeat audio")
    print("Press Ctrl+C in terminal to stop")
    print("=" * 70)
    
    # Warning dialogs
    result = user32.MessageBoxW(0, 
        "⚠️ HYDROGEN GDI EFFECTS ⚠️\n\n"
        "This will affect your ACTUAL DESKTOP screen!\n"
        "10 visual payloads with bytebeat audio.\n\n"
        "Press Ctrl+C to stop anytime.\n\n"
        "Continue?",
        "Hydrogen.exe", MB_YESNO | MB_ICONWARNING | MB_TOPMOST)
    
    if result != IDYES:
        print("Cancelled")
        return
    
    result = user32.MessageBoxW(0,
        "⚠️ LAST WARNING ⚠️\n\n"
        "This is REAL desktop GDI malware simulation!\n"
        "Your screen WILL be distorted!\n\n"
        "ARE YOU ABSOLUTELY SURE?",
        "Hydrogen.exe - LAST WARNING", MB_YESNO | MB_ICONWARNING | MB_TOPMOST)
    
    if result != IDYES:
        print("Cancelled")
        return
    
    # Get screen size
    w, h = get_screen_size()
    print(f"Screen: {w}x{h}")
    print("Starting in 3 seconds...")
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
    
    # Payloads with audio
    payloads = [
        (payload1, "PlgBlt Parallelogram", audio_sequence1),
        (payload2, "Wave Distortion", audio_sequence2),
        (payload3, "Vertical Wave", audio_sequence3),
        (payload4, "Glitch Effect", audio_sequence4),
        (payload5, "Screen Invert", audio_sequence5),
        (payload6, "Screen Shake", audio_sequence6),
        (payload7, "Zoom Effect", audio_sequence7),
        (payload8, "Pixelate Effect", audio_sequence8),
        (payload9, "Tunnel Effect", audio_sequence9),
        (payload10, "Swirl Effect", audio_sequence10),
    ]
    
    # Shaders
    shaders = [
        (shader1, "Color Invert Shader"),
        (shader2, "Rainbow Overlay"),
        (shader3, "Scanlines"),
        (shader4, "Negative Effect"),
        (shader5, "Random Color Blocks"),
    ]
    
    print("\n" + "=" * 50)
    print("STARTING PAYLOADS")
    print("=" * 50)
    
    try:
        # Execute payloads
        for i, (payload, name, audio_func) in enumerate(payloads):
            print(f"[{i+1}/{len(payloads)}] {name} ({PAYLOAD_TIME}s)")
            
            # Play audio
            if HAS_AUDIO:
                play_audio_async(audio_func, PAYLOAD_TIME)
            
            # Run payload
            execute_payload(payload, PAYLOAD_TIME, hdc, w, h)
            
            # Restore between payloads
            gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
            time.sleep(0.5)
        
        print("\n" + "=" * 50)
        print("STARTING SHADERS")
        print("=" * 50)
        
        # Execute shaders
        for i, (shader, name) in enumerate(shaders):
            print(f"[{i+1}/{len(shaders)}] {name} ({PAYLOAD_TIME}s)")
            execute_shader(shader, PAYLOAD_TIME, hdc, w, h)
            
            # Restore between shaders
            gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
            time.sleep(0.5)
        
        print("\n✅ All payloads and shaders completed!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")
    finally:
        # Restore screen
        print("\nRestoring screen...")
        gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
        user32.InvalidateRect(0, None, 0)
        time.sleep(0.5)
        
        # Cleanup
        gdi32.DeleteObject(hbm_backup)
        gdi32.DeleteDC(hdc_backup)
        user32.ReleaseDC(0, hdc)
        
        print("Screen restored!")
        user32.MessageBoxW(0, "Hydrogen GDI Effects Complete!\n\nScreen restored to normal.", 
                          "Complete", 0x00000040)

if __name__ == "__main__":
    main()