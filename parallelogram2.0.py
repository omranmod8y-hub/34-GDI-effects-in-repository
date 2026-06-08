import ctypes
from ctypes import wintypes
import random
import time
import sys
import math
import threading

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
kernel32 = ctypes.windll.kernel32

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class ByteBeatPlayer:
    def __init__(self):
        self.playing = False
        self.thread = None
        self.time_var = 0
        self.stop_flag = False
        
    def bytebeat1(self, t):
        """Classic bytebeat: (t * (t >> 8)) & 0xFF"""
        return (t * (t >> 8)) & 0xFF
    
    def bytebeat2(self, t):
        """Chiptune style: t & (t >> 8)"""
        return (t & (t >> 8)) & 0xFF
    
    def bytebeat3(self, t):
        """Bass rhythm: (t * ((t >> 5) & 0xF)) & 0xFF"""
        return (t * ((t >> 5) & 0xF)) & 0xFF
    
    def bytebeat4(self, t):
        """Arpeggio: ((t >> 2) | (t >> 5)) & 0xFF"""
        return ((t >> 2) | (t >> 5)) & 0xFF
    
    def bytebeat5(self, t):
        """Complex melody: ((t * (t >> 8) & 0xFF) | (t >> 4)) & 0xFF"""
        return ((t * (t >> 8) & 0xFF) | (t >> 4)) & 0xFF
    
    def bytebeat6(self, t):
        """Wobble bass: (t * ((t >> 8) & 0x7F)) & 0xFF"""
        return (t * ((t >> 8) & 0x7F)) & 0xFF
    
    def bytebeat7(self, t):
        """Synth wave: ((t >> 4) * 0x30 + ((t >> 8) * 0x20)) & 0xFF"""
        return ((t >> 4) * 0x30 + ((t >> 8) * 0x20)) & 0xFF
    
    def bytebeat8(self, t):
        """Pulse wave: (t >> 3) & ((t >> 4) | (t >> 7)) & 0xFF"""
        return (t >> 3) & ((t >> 4) | (t >> 7)) & 0xFF
    
    def play_bytebeat_simple(self, duration_seconds, beat_func):
        """Play bytebeat using Windows Beep (simple but effective)"""
        self.stop_flag = False
        sample_rate = 8000  # 8kHz beep rate
        num_samples = int(duration_seconds * sample_rate)
        
        for i in range(num_samples):
            if self.stop_flag:
                break
            
            t = i + self.time_var
            value = beat_func(t)
            
            # Convert bytebeat value (0-255) to frequency (37-8000 Hz)
            # Map 0-255 to 100-4000 Hz range for audible tones
            freq = 100 + (value * 15)
            
            # Duration of each beep in milliseconds
            beep_duration = max(1, int(1000 / sample_rate))
            
            # Play beep if value is above threshold (creates rhythm)
            if value > 64:  # Threshold for triggering sound
                kernel32.Beep(int(freq), beep_duration)
            else:
                time.sleep(beep_duration / 1000.0)
            
            # Small delay between samples
            time.sleep(0.0001)
        
        self.time_var += num_samples
    
    def play_bytebeat_thread(self, duration, beat_func):
        """Play bytebeat in a separate thread"""
        self.stop_flag = False
        thread = threading.Thread(target=self.play_bytebeat_simple, 
                                 args=(duration, beat_func))
        thread.start()
        return thread
    
    def stop(self):
        """Stop playback"""
        self.stop_flag = True

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
    
    left = 0
    top = 0
    right = w
    bottom = h
    
    points = (POINT * 3)()
    
    points[0].x = (left + 50) + (t % 100)
    points[0].y = (top - 50) + (t % 50)
    
    points[1].x = (right + 50) - (t % 100)
    points[1].y = (top + 50) + (t % 50)
    
    points[2].x = (left - 50) + (t % 50)
    points[2].y = (bottom - 50) - (t % 50)
    
    src_left = left - 20
    src_top = top - 20
    src_width = (right - left) + 40
    src_height = (bottom - top) + 40
    
    gdi32.PlgBlt(hdc, points, hdc, src_left, src_top, src_width, src_height, None, 0, 0)
    
    return t + 5

def plgblt_rotate_effect(hdc, w, h, t):
    """Rotating parallelogram effect"""
    left = 0
    top = 0
    right = w
    bottom = h
    
    points = (POINT * 3)()
    
    angle = t / 30.0
    
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
    print("PlgBlt PARALLELOGRAM EFFECT with BYTEBEAT SOUND")
    print("=" * 70)
    print("⚠️ THIS WILL DISTORT YOUR ACTUAL SCREEN! ⚠️")
    print("Synthesized bytebeat music will play through PC speaker!")
    print("Press Ctrl+C in terminal to stop")
    print("=" * 70)
    
    # First warning
    result = user32.MessageBoxW(0, 
        "⚠️ PlgBlt PARALLELOGRAM EFFECT with BYTEBEAT ⚠️\n\n"
        "This WILL distort your ACTUAL DESKTOP screen!\n"
        "Creates a warped/tilted parallelogram effect.\n"
        "Bytebeat synthesized music will play!\n\n"
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
        "Bytebeat music will play through your speakers!\n"
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
    print("Starting PlgBlt effects with bytebeat in 3 seconds...")
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
    
    # Initialize bytebeat player
    player = ByteBeatPlayer()
    
    # Effects list with corresponding bytebeat functions
    effects = [
        ("🎵 Moving + Classic Bytebeat", plgblt_effect, 8, player.bytebeat1),
        ("🎵 Rotating + Chiptune", plgblt_rotate_effect, 10, player.bytebeat2),
        ("🎵 Stretching + Bass Rhythm", plgblt_stretch_effect, 10, player.bytebeat3),
        ("🎵 Rotating + Arpeggio", plgblt_rotate_effect, 8, player.bytebeat4),
        ("🎵 Moving + Complex Melody", plgblt_effect, 10, player.bytebeat5),
        ("🎵 Stretching + Wobble Bass", plgblt_stretch_effect, 8, player.bytebeat6),
        ("🎵 Rotating + Synth Wave", plgblt_rotate_effect, 10, player.bytebeat7),
        ("🎵 Moving + Pulse Wave", plgblt_effect, 8, player.bytebeat8),
    ]
    
    t = 0
    
    print("\n" + "=" * 50)
    print("🎵 STARTING PLGBLT WITH BYTEBEAT MUSIC 🎵")
    print("Your screen will be transformed!")
    print("Synthesized music will play!")
    print("Press Ctrl+C to stop")
    print("=" * 50 + "\n")
    
    try:
        for i, (name, effect, duration, beat_func) in enumerate(effects):
            print(f"[{i+1}/{len(effects)}] {name} ({duration} seconds)")
            
            # Start playing bytebeat in background thread
            sound_thread = player.play_bytebeat_thread(duration, beat_func)
            
            start_time = time.time()
            effect_end_time = start_time + duration
            
            while time.time() < effect_end_time:
                t = effect(hdc, w, h, t)
                time.sleep(0.033)  # ~30 FPS
                
                # Check for ESC key to stop
                if user32.GetAsyncKeyState(0x1B) & 0x8000:
                    print("\nESC pressed - stopping!")
                    player.stop()
                    break
            
            # Wait for sound to finish
            if sound_thread.is_alive():
                sound_thread.join(timeout=1)
            
            # Restore backup between effects
            gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
            time.sleep(0.5)
            
            if i < len(effects) - 1:
                print("  ➡ Next effect in 1 second...\n")
                time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")
        player.stop()
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
        user32.MessageBoxW(0, "PlgBlt Effect Complete!\n\nScreen restored to normal.\nBytebeat music stopped.", 
                          "Complete", 0x00000040)

if __name__ == "__main__":
    main()