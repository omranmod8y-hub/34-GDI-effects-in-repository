import ctypes
from ctypes import wintypes
import math
import random
import time
import threading

# Windows constants
SRCCOPY = 0x00CC0020
PATINVERT = 0x5A0049
MB_YESNO = 0x00000004
MB_ICONWARNING = 0x00000030
MB_SYSTEMMODAL = 0x00001000
IDYES = 6

# Load Windows libraries
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
winmm = ctypes.windll.winmm  # For Sound

# ============ BYTEBEAT AUDIO ENGINE ============

class BytebeatPlayer:
    def __init__(self, sample_rate=8000):
        self.sample_rate = sample_rate
        self.is_playing = False
        
    def play(self, formula_type=0):
        self.is_playing = True
        self.thread = threading.Thread(target=self._audio_thread, args=(formula_type,))
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.is_playing = False

    def _audio_thread(self, formula_type):
        # WAVEFORMATEX structure: 1 channel, 8000Hz, 8-bit
        wfx = bytes([1, 0, 1, 0, 64, 31, 0, 0, 64, 31, 0, 0, 1, 0, 8, 0, 0, 0])
        h_waveout = wintypes.HANDLE()
        
        # Open Wave Device
        winmm.waveOutOpen(ctypes.byref(h_waveout), -1, wfx, 0, 0, 0)
        
        t = 0
        buffer_size = 8000  # 1 second of audio per chunk
        
        while self.is_playing:
            audio_data = bytearray(buffer_size)
            for i in range(buffer_size):
                # BYTEBEAT FORMULAS
                if formula_type == 0: # Glitch Techno
                    val = (t * (t >> 8 | t >> 9) & 46 & t >> 8) ^ (t & t >> 13 | t >> 6)
                elif formula_type == 1: # Chaotic Sine
                    val = (t >> 6 | t | t >> (t >> 16)) * 10 + ((t >> 11) & 7)
                else: # Dark Industrial
                    val = (t * (t >> 5 | t >> 8)) >> (t >> 16)
                
                audio_data[i] = val & 0xFF
                t += 1

            # Prepare header
            header = ctypes.create_string_buffer(bytes(audio_data))
            wave_hdr = bytearray(ctypes.sizeof(ctypes.c_void_p) * 4 + 16) 
            # Simplified header handling for background playback
            winmm.waveOutWrite(h_waveout, header, len(header))
            
            # Control buffer speed (prevents massive memory buildup)
            time.sleep(0.9) 

# ============ GDI EFFECTS (Simplified for Demo) ============

def get_screen_size():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def effect_glitch(hdc, width, height, frame):
    for _ in range(30):
        y = random.randint(0, height - 20)
        h = random.randint(10, 60)
        shift = random.randint(-50, 50)
        gdi32.BitBlt(hdc, shift, y, width, h, hdc, 0, y, SRCCOPY)
    return frame + 1

def effect_invert(hdc, width, height, frame):
    gdi32.PatBlt(hdc, 0, 0, width, height, PATINVERT)
    return frame + 1

# ============ MAIN EXECUTION ============

def main():
    result = user32.MessageBoxW(0, 
        "⚠️ WARNING ⚠️\n\nThis script will apply GDI effects AND play Bytebeat audio.\nContinue?",
        "GDI + BYTEBEAT", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES: return

    width, height = get_screen_size()
    hdc = user32.GetDC(0)
    
    # Start Sound
    player = BytebeatPlayer()
    player.play(formula_type=random.randint(0, 2))
    
    print("Effects and Sound Running... Press Ctrl+C to stop.")
    
    effects = [
        ("Glitch Mode", effect_glitch, 10),
        ("Invert Mode", effect_invert, 5)
    ]
    
    frame = 0
    try:
        for name, effect_func, duration in effects:
            print(f"Current Effect: {name}")
            start_time = time.time()
            # Change audio formula for every new effect
            player.stop()
            time.sleep(0.1)
            player.play(formula_type=random.randint(0, 2))
            
            while time.time() - start_time < duration:
                frame = effect_func(hdc, width, height, frame)
                time.sleep(0.03) # ~30 FPS
            
            user32.InvalidateRect(0, None, 0) # Refresh screen
            
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        player.stop()
        user32.ReleaseDC(0, hdc)
        user32.InvalidateRect(0, None, 0)
        print("Cleanup complete.")

if __name__ == "__main__":
    main()