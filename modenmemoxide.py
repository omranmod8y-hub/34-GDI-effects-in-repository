import ctypes
import threading
import random
import math
import time
import sys
from ctypes import wintypes

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SRCCOPY = 0x00CC0020
SRCINVERT = 0x00660046
SRCPAINT = 0x00EE0086
SRCAND = 0x008800C6
NOTSRCCOPY = 0x00330008
PATINVERT = 0x005A0049
DSTINVERT = 0x00550009
NOTSRCERASE = 0x001100A6

MB_YESNO = 0x04
MB_ICONEXCLAMATION = 0x30
MB_SYSTEMMODAL = 0x1000
IDYES = 6
IDNO = 7

# ---------------------------------------------------------------------------
# Win32 DLL bindings
# ---------------------------------------------------------------------------
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

# Set DPI awareness
try:
    shcore = ctypes.windll.shcore
    shcore.SetProcessDpiAwareness(1)
except:
    try:
        user32.SetProcessDPIAware()
    except:
        pass

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def RGB(r, g, b):
    return (r & 0xFF) | ((g & 0xFF) << 8) | ((b & 0xFF) << 16)

def get_screen_size():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def get_hdc():
    return user32.GetDC(0)

def release_hdc(hdc):
    user32.ReleaseDC(0, hdc)

def redraw_window():
    user32.InvalidateRect(0, None, True)

# ---------------------------------------------------------------------------
# Audio generation
# ---------------------------------------------------------------------------
def play_audio(generator_func, duration=30):
    """Play generated audio using winsound"""
    try:
        import winsound
        import numpy as np
        
        sample_rate = 8000
        samples = int(sample_rate * duration)
        
        # Generate audio data
        data = generator_func(samples, sample_rate)
        
        # Convert to bytes
        import struct
        audio_bytes = b''
        for sample in data:
            audio_bytes += struct.pack('B', int(sample))
        
        # Play using winsound (Windows only)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            # Write simple WAV header
            f.write(b'RIFF')
            f.write(struct.pack('<I', 0))
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write(struct.pack('<I', 16))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<I', sample_rate))
            f.write(struct.pack('<I', sample_rate))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<H', 8))
            f.write(b'data')
            f.write(struct.pack('<I', len(audio_bytes)))
            f.write(audio_bytes)
            f.flush()
            
            # Play
            winsound.PlaySound(f.name, winsound.SND_FILENAME | winsound.SND_ASYNC)
            time.sleep(duration)
    except:
        pass

def audio_seq1(samples, rate):
    data = []
    for t in range(samples):
        val = (t & 4096 and ((t * (t ^ (t % 9)) | (t >> 3)) >> 1) or 255)
        data.append(val & 0xFF)
    return data

def audio_seq2(samples, rate):
    data = []
    for t in range(samples):
        val = t * (1 + (5 & (t >> 10))) * (3 + ((t >> 17) & 1 and ((2 ^ 2 & (t >> 14)) // 3) or (3 & ((t >> 13) + 1)))) >> (3 & (t >> 9))
        data.append(val & 0xFF)
    return data

def audio_seq3(samples, rate):
    data = []
    for t in range(samples):
        val = ((t >> 4) * t & (t >> 3 ^ t >> 4) + (t >> 5 | t >> 2)) | (t * (t >> 3 | t >> 6) >> (t >> 5 | t >> 7) ^ (t >> t) + ((t // 2) * t >> 12))
        data.append(val & 0xFF)
    return data

def audio_seq4(samples, rate):
    data = []
    for t in range(samples):
        val = ((t >> 2) * (t & (16 if (t & 32768) else 24) | (t >> ((t >> 8) & 24)))) | (t >> 3)
        data.append(val & 0xFF)
    return data

def audio_seq5(samples, rate):
    data = []
    for t in range(samples):
        val = 9 * t & t >> 4 | 5 * t & t >> 7 | 3 * t & t >> 10
        data.append(val & 0xFF)
    return data

def audio_seq6(samples, rate):
    data = []
    for t in range(samples):
        val = t * (3 + (1 ^ 5 & t >> 10)) * (5 + (3 & t >> 14)) >> (3 & t >> 8)
        data.append(val & 0xFF)
    return data

def audio_seq7(samples, rate):
    data = []
    for t in range(samples):
        val = 20 * t * t * (t >> 11) // 7
        data.append(val & 0xFF)
    return data

def audio_seq8(samples, rate):
    data = []
    for t in range(samples):
        val = t * (t ^ t + (t >> 15 | 1) ^ (t - 1280 ^ t) >> 10) * t
        data.append(val & 0xFF)
    return data

def audio_seq9(samples, rate):
    data = []
    for t in range(samples):
        val = 2 * (t >> 5 & t) - (t >> 5) + t * (t >> 14 & 14)
        data.append(val & 0xFF)
    return data

def audio_seq10(samples, rate):
    data = []
    for t in range(samples):
        val = t + (t & t >> 12) * t >> 8
        data.append(val & 0xFF)
    return data

# ---------------------------------------------------------------------------
# Payload classes
# ---------------------------------------------------------------------------
class Payload:
    def __init__(self):
        self.running = False
        self.stop_event = None
        self.thread = None
    
    def start(self):
        if not self.running:
            self.running = True
            self.stop_event = threading.Event()
            self.thread = threading.Thread(target=self._draw_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        self.running = False
        if self.stop_event:
            self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1)
    
    def _draw_loop(self):
        while self.running and not self.stop_event.is_set():
            hdc = get_hdc()
            self.draw(hdc)
            release_hdc(hdc)
            time.sleep(0.01)
    
    def draw(self, hdc):
        pass

class Payload1(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        x1, y1 = random.randint(0, sw), random.randint(0, sh)
        x2, y2 = random.randint(0, sw), random.randint(0, sh)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        if w > 0 and h > 0:
            gdi32.StretchBlt(hdc, x1, y1, w, h, hdc, 0, 0, sw, sh, SRCCOPY)

class Payload2(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        brush = gdi32.CreateSolidBrush(RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.SelectObject(hdc, brush)
        x = random.randint(0, sw)
        y = random.randint(0, sh)
        w = random.randint(10, 100)
        h = random.randint(10, 100)
        gdi32.PatBlt(hdc, x, y, w, h, PATINVERT)
        gdi32.DeleteObject(brush)

class Payload3(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        for _ in range(5):
            x = random.randint(0, sw)
            y = random.randint(0, sh)
            gdi32.PatBlt(hdc, x, y, 50, 50, PATINVERT)

class Payload4(Payload):
    def __init__(self):
        super().__init__()
        self.hue = 0
    
    def draw(self, hdc):
        sw, sh = get_screen_size()
        self.hue = (self.hue + 5) % 360
        # Simple color cycling
        r = int((math.sin(math.radians(self.hue)) + 1) * 127)
        g = int((math.sin(math.radians(self.hue + 120)) + 1) * 127)
        b = int((math.sin(math.radians(self.hue + 240)) + 1) * 127)
        brush = gdi32.CreateSolidBrush(RGB(r, g, b))
        gdi32.SelectObject(hdc, brush)
        gdi32.PatBlt(hdc, 0, 0, sw, sh, PATINVERT)
        gdi32.DeleteObject(brush)

class Payload5(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        for _ in range(10):
            x = random.randint(0, sw)
            y = random.randint(0, sh)
            gdi32.SetPixel(hdc, x, y, RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

class Payload6(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        gdi32.BitBlt(hdc, random.randint(-5, 5), random.randint(-5, 5), sw, sh, hdc, 0, 0, SRCCOPY)

class Payload7(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        for i in range(0, sh, 20):
            gdi32.BitBlt(hdc, 0, i, sw, 5, hdc, random.randint(-20, 20), i, SRCCOPY)

class Payload8(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        size = random.randint(25, 100)
        x = random.randint(0, sw - size)
        y = random.randint(0, sh - size)
        gdi32.PatBlt(hdc, x, y, size, size, PATINVERT)

class Payload9(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        gdi32.StretchBlt(hdc, 5, 5, sw - 10, sh - 10, hdc, 0, 0, sw, sh, SRCCOPY)

class Payload10(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        # Apply simple sharpening effect via multiple blits
        gdi32.BitBlt(hdc, 1, 1, sw - 1, sh - 1, hdc, 0, 0, SRCINVERT)

class Payload11(Payload):
    def __init__(self):
        super().__init__()
        self.angle = 0
    
    def draw(self, hdc):
        sw, sh = get_screen_size()
        self.angle += 0.1
        offset = int(math.sin(self.angle) * 30)
        for i in range(0, sh, 10):
            gdi32.BitBlt(hdc, offset, i, sw - abs(offset), 1, hdc, 0, i, SRCCOPY)

class Payload12(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        for _ in range(50):
            x = random.randint(0, sw)
            y = random.randint(0, sh)
            gdi32.SetPixel(hdc, x, y, RGB(255, 255, 255))

class Payload13(Payload):
    def __init__(self):
        super().__init__()
        self.hue = 0
    
    def draw(self, hdc):
        sw, sh = get_screen_size()
        self.hue = (self.hue + 2) % 360
        r = int((math.sin(math.radians(self.hue)) + 1) * 127)
        g = int((math.sin(math.radians(self.hue + 120)) + 1) * 127)
        b = int((math.sin(math.radians(self.hue + 240)) + 1) * 127)
        brush = gdi32.CreateSolidBrush(RGB(r, g, b))
        gdi32.SelectObject(hdc, brush)
        gdi32.PatBlt(hdc, 0, 0, sw, sh, PATINVERT)
        gdi32.DeleteObject(brush)

class Payload14(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, DSTINVERT)

class Payload15(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        points = [(random.randint(0, sw), random.randint(0, sh)) for _ in range(3)]
        for x, y in points:
            gdi32.PatBlt(hdc, x, y, 100, 100, PATINVERT)

class Payload16(Payload):
    def draw(self, hdc):
        sw, sh = get_screen_size()
        gdi32.StretchBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, sw, sh, NOTSRCERASE)

# ---------------------------------------------------------------------------
# Background threads
# ---------------------------------------------------------------------------
def message_box_thread():
    for i in range(5):
        time.sleep(4)
        try:
            user32.MessageBoxW(0, f"modenmemoxide - Phase {i+1}", "modenmemoxide", MB_ICONEXCLAMATION)
        except:
            pass

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main():
    # Warning dialogs
    result = user32.MessageBoxW(None,
        "This software uses GDI effects.\nAre you sure you want to run it?",
        "modenmemoxide.exe",
        MB_YESNO | MB_ICONEXCLAMATION | MB_SYSTEMMODAL)
    if result != IDYES:
        return
    
    result = user32.MessageBoxW(None,
        "This will NOT damage your system.\nStill continue?",
        "LAST WARNING!!!",
        MB_YESNO | MB_ICONEXCLAMATION | MB_SYSTEMMODAL)
    if result != IDYES:
        return
    
    print("[*] Starting modenmemoxide...")
    print("[*] Total runtime: ~5 minutes")
    
    time.sleep(5)
    
    # Create payloads
    payloads = [
        Payload1(), Payload2(), Payload3(), Payload4(), Payload5(),
        Payload6(), Payload7(), Payload8(), Payload9(), Payload10(),
        Payload11(), Payload12(), Payload13(), Payload14(), Payload15(), Payload16()
    ]
    
    # Audio sequences
    audio_sequences = [
        audio_seq1, audio_seq2, audio_seq3, audio_seq4, audio_seq5,
        audio_seq6, audio_seq7, audio_seq8, audio_seq9, audio_seq10
    ]
    
    # Phase 1
    print("[*] Phase 1/10")
    payloads[0].start()
    payloads[1].start()
    play_audio(audio_seq1, 30)
    payloads[0].stop()
    payloads[1].stop()
    redraw_window()
    time.sleep(0.5)
    
    # Phase 2
    print("[*] Phase 2/10")
    payloads[2].start()
    play_audio(audio_seq2, 30)
    payloads[2].stop()
    redraw_window()
    time.sleep(0.5)
    
    # Phase 3
    print("[*] Phase 3/10")
    payloads[3].start()
    payloads[4].start()
    play_audio(audio_seq3, 30)
    payloads[3].stop()
    payloads[4].stop()
    redraw_window()
    time.sleep(0.5)
    
    # Phase 4
    print("[*] Phase 4/10")
    payloads[5].start()
    payloads[6].start()
    play_audio(audio_seq4, 30)
    payloads[5].stop()
    payloads[6].stop()
    redraw_window()
    time.sleep(0.5)
    
    # Phase 5
    print("[*] Phase 5/10")
    payloads[7].start()
    play_audio(audio_seq5, 30)
    payloads[7].stop()
    redraw_window()
    time.sleep(0.5)
    
    # Phase 6
    print("[*] Phase 6/10")
    payloads[8].start()
    payloads[9].start()
    play_audio(audio_seq6, 30)
    payloads[8].stop()
    payloads[9].stop()
    redraw_window()
    time.sleep(0.5)
    
    # Phase 7
    print("[*] Phase 7/10")
    payloads[10].start()
    payloads[11].start()
    play_audio(audio_seq7, 30)
    payloads[10].stop()
    payloads[11].stop()
    redraw_window()
    time.sleep(0.5)
    
    # Phase 8
    print("[*] Phase 8/10")
    payloads[12].start()
    play_audio(audio_seq8, 30)
    payloads[12].stop()
    redraw_window()
    time.sleep(0.5)
    
    # Phase 9
    print("[*] Phase 9/10")
    payloads[13].start()
    payloads[14].start()
    play_audio(audio_seq9, 30)
    payloads[13].stop()
    payloads[14].stop()
    redraw_window()
    time.sleep(0.5)
    
    # Phase 10 - All payloads
    print("[*] Phase 10/10 - Final")
    for p in payloads:
        p.start()
    
    threading.Thread(target=message_box_thread, daemon=True).start()
    play_audio(audio_seq10, 30)
    
    for p in payloads:
        p.stop()
    
    # Final cleanup
    redraw_window()
    print("\n" + "="*50)
    print("modenmemoxide execution complete.")
    print("System restored.")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user")
        redraw_window()
    except Exception as e:
        print(f"[*] Error: {e}")
        redraw_window()