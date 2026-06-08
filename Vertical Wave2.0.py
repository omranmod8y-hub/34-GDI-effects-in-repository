import ctypes
from ctypes import wintypes
import math
import random
import time
import sys
import threading

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
winmm = ctypes.windll.winmm

# Sound constants
SND_ASYNC = 0x0001
SND_NODEFAULT = 0x0002

class ByteBeat:
    def __init__(self):
        self.sample_rate = 44100
        self.duration = 0.4
        self.volume = 4000
        self.running = False
        
    # NEW BYTEBEAT ALGORITHMS
    
    def beat_dreamy(self, t):
        """Dreamy chime melody"""
        return int(((t >> 3) & 0xFF) * ((t >> 6) & 0x1F) * 0.5) & 0xFF
    
    def beat_techno(self, t):
        """Techno bass pattern"""
        return int((t * 5) & (t >> 7) | (t * 3) & (t >> 6)) & 0xFF
    
    def beat_sine_wobble(self, t):
        """Smooth sine-like wobble"""
        return int((((t >> 2) * (t >> 4) & 0xFF) * math.sin(t / 100) * 2)) & 0xFF
    
    def beat_chiptune(self, t):
        """Classic 8-bit game music"""
        return int(((t >> 4) & 0x0F) * ((t >> 6) & 0x07) * 8) & 0xFF
    
    def beat_drum_loop(self, t):
        """Percussive rhythm"""
        return int(((t & 0xFF) * ((t >> 8) & 0xFF)) >> 8) & 0xFF
    
    def beat_acid(self, t):
        """Acid house squelch"""
        return int((t & 0xFF) * (t >> 6 | t >> 4) & 0xFF) & 0xFF
    
    def beat_ambient(self, t):
        """Atmospheric drone"""
        return int((t >> 4) ^ (t >> 6) & (t >> 5) | (t >> 3)) & 0xFF
    
    def beat_arp(self, t):
        """Fast arpeggio"""
        t2 = t >> 2
        return int((t2 & 0xFF) * (t2 >> 5) & 0xFF) & 0xFF
    
    def beat_noise(self, t):
        """White noise sweep"""
        return int((t & 0xFF) * random.randint(0, 255) / 255) & 0xFF
    
    def beat_bounce(self, t):
        """Bouncing ball effect"""
        return int(abs(math.sin(t / 500) * 255) * ((t >> 4) & 0x0F)) & 0xFF
    
    def beat_phaser(self, t):
        """Phaser sweep"""
        phase = int((t >> 5) & 0xFF)
        return int((phase * 2) ^ (phase >> 3) & phase) & 0xFF
    
    def beat_heartbeat(self, t):
        """Heartbeat thump"""
        beat = int(math.sin(t / 2000) ** 2 * 255)
        return int(beat * ((t >> 3) & 0x0F)) & 0xFF
    
    def beat_spiral(self, t):
        """Spiral descending tone"""
        return int((t & 0xFF) * (t >> 7 | t >> 4) & 0xFF) & 0xFF
    
    def beat_crystal(self, t):
        """Crystal clear arpeggios"""
        return int(((t >> 1) & 0xFF) ^ ((t >> 4) & 0xFF) & ((t >> 2) & 0xFF)) & 0xFF
    
    def beat_robot(self, t):
        """Robot voice effect"""
        return int((t & 0xFF) * ((t >> 8) & 0x0F) | ((t >> 4) & 0xF0)) & 0xFF
    
    def beat_wind(self, t):
        """Wind blowing effect"""
        return int(math.sin(t / 100) * ((t >> 5) & 0xFF)) & 0xFF
    
    def beat_pulse_train(self, t):
        """Pulse train rhythm"""
        return int((t & 0x8000) >> 15 * 255) & 0xFF
    
    def beat_fm_synth(self, t):
        """FM synthesis emulation"""
        mod = math.sin(t / 200) * 50
        carrier = math.sin(t / 50 + mod) * 127
        return int(carrier + 128) & 0xFF
    
    def beat_bitcrush(self, t):
        """Bit crushed melody"""
        step = 16
        crushed = (t >> 4) & ~(step - 1)
        return int((crushed & 0xFF) * ((t >> 6) & 0x03)) & 0xFF
    
    def beat_water(self, t):
        """Water droplet sounds"""
        drip = int(math.sin(t / 300) ** 4 * 255)
        return int(drip * ((t >> 5) & 0x07)) & 0xFF
    
    def generate_wave(self, beat_func, frame=0):
        """Generate wave file content"""
        samples = int(self.sample_rate * self.duration)
        data = bytearray()
        
        t_offset = frame * 800
        
        for i in range(samples):
            t = i + t_offset
            value = beat_func(t)
            value = (value - 128) * self.volume // 128
            value = max(-32768, min(32767, value))
            data.extend([value & 0xFF, (value >> 8) & 0xFF])
        
        # WAV header
        header = bytearray()
        header.extend(b'RIFF')
        header.extend((36 + len(data)).to_bytes(4, 'little'))
        header.extend(b'WAVEfmt ')
        header.extend((16).to_bytes(4, 'little'))
        header.extend((1).to_bytes(2, 'little'))
        header.extend((1).to_bytes(2, 'little'))
        header.extend(self.sample_rate.to_bytes(4, 'little'))
        header.extend((self.sample_rate * 2).to_bytes(4, 'little'))
        header.extend((2).to_bytes(2, 'little'))
        header.extend((16).to_bytes(2, 'little'))
        header.extend(b'data')
        header.extend(len(data).to_bytes(4, 'little'))
        
        return header + data
    
    def play_beat(self, effect_index, frame=0, variation=0):
        """Play a bytebeat sound"""
        try:
            import tempfile
            import os
            
            # NEW SOUND MAP - each effect gets unique sound
            beat_map = [
                self.beat_chiptune,   # Standard Wave - 8-bit game music
                self.beat_techno,     # Animated Wave - Techno bass
                self.beat_acid,       # Fast Wave - Acid squelch
                self.beat_dreamy,     # Slow Wave - Dreamy chimes
                self.beat_drum_loop,  # Strong Wave - Percussive
                self.beat_crystal,    # Double Wave - Crystal clear
                self.beat_spiral,     # Reverse Wave - Spiral tones
                self.beat_heartbeat,  # Pulsing Wave - Heartbeat
                self.beat_ambient,    # Extra 1 - Ambient drone
                self.beat_robot,      # Extra 2 - Robot voice
                self.beat_water,      # Extra 3 - Water drops
                self.beat_fm_synth,   # Extra 4 - FM synth
            ]
            
            beat_func = beat_map[effect_index % len(beat_map)]
            wav_data = self.generate_wave(beat_func, frame + variation)
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file.write(wav_data)
            temp_file.close()
            
            winmm.PlaySoundW(temp_file.name, 0, SND_ASYNC | SND_NODEFAULT)
            
            def delete_file():
                time.sleep(0.5)
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            
            threading.Thread(target=delete_file, daemon=True).start()
        except Exception as e:
            pass

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

def vertical_wave_fixed(hdc, w, h, frame, amplitude=40, frequency=30):
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    angle = frame / 10.0
    for x in range(w):
        offset = int(math.sin(angle + x / frequency) * amplitude)
        gdi32.BitBlt(hdc, x, offset, 1, h, hdc_mem, x, 0, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def vertical_wave_animated(hdc, w, h, frame):
    amplitude = int(abs(math.sin(frame / 30)) * 60) + 10
    return vertical_wave_fixed(hdc, w, h, frame, amplitude, 30)

def vertical_wave_fast(hdc, w, h, frame):
    return vertical_wave_fixed(hdc, w, h, frame, 50, 15)

def vertical_wave_slow(hdc, w, h, frame):
    return vertical_wave_fixed(hdc, w, h, frame, 30, 60)

def vertical_wave_strong(hdc, w, h, frame):
    amplitude = int(abs(math.sin(frame / 25)) * 100) + 20
    return vertical_wave_fixed(hdc, w, h, frame, amplitude, 25)

def vertical_wave_double(hdc, w, h, frame):
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    angle = frame / 8.0
    for x in range(w):
        offset1 = int(math.sin(angle + x / 20) * 30)
        offset2 = int(math.sin(angle * 1.5 + x / 40) * 20)
        offset = offset1 + offset2
        gdi32.BitBlt(hdc, x, offset, 1, h, hdc_mem, x, 0, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def vertical_wave_reverse(hdc, w, h, frame):
    hdc_mem = gdi32.CreateCompatibleDC(hdc)
    hbm = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_mem, hbm)
    gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    angle = frame / 10.0
    for x in range(w):
        offset = -int(math.sin(angle + x / 30) * 40)
        gdi32.BitBlt(hdc, x, offset, 1, h, hdc_mem, x, 0, SRCCOPY)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    return frame + 1

def vertical_wave_pulse(hdc, w, h, frame):
    pulse = abs(math.sin(frame / 20))
    amplitude = int(pulse * 80) + 10
    return vertical_wave_fixed(hdc, w, h, frame, amplitude, 30)

def main():
    print("=" * 70)
    print("VERTICAL WAVE EFFECT - NEW BYTEBEAT SOUNDS")
    print("=" * 70)
    print("⚠️ THIS WILL AFFECT YOUR ACTUAL SCREEN! ⚠️")
    print("Columns will shift up and down like a wave")
    print("🎵 NEW - 12 unique bytebeat melodies!")
    print("   • Chiptune • Techno • Acid • Dreamy")
    print("   • Crystal • Spiral • Heartbeat • Water")
    print("Press Ctrl+C in terminal to stop")
    print("=" * 70)
    
    result = user32.MessageBoxW(0, 
        "⚠️ VERTICAL WAVE WITH NEW BYTEBEAT SOUNDS ⚠️\n\n"
        "This will create a VERTICAL WAVE on your ACTUAL DESKTOP!\n"
        "Columns will shift up and down like a wave.\n"
        "🎵 NEW sounds: Chiptune, Techno, Acid, Crystal, Water & more!\n\n"
        "Press Ctrl+C in terminal to stop anytime.\n\n"
        "Continue?",
        "Vertical Wave - NEW SOUNDS", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled by user")
        return
    
    result = user32.MessageBoxW(0,
        "⚠️ LAST WARNING ⚠️\n\n"
        "Your screen will have a VERTICAL WAVE effect with NEW sounds!\n"
        "This is a REAL desktop effect.\n\n"
        "ARE YOU ABSOLUTELY SURE?",
        "FINAL WARNING", MB_YESNO | MB_ICONWARNING | MB_SYSTEMMODAL)
    
    if result != IDYES:
        print("Cancelled at last warning")
        return
    
    w, h = get_screen_size()
    print(f"Screen: {w}x{h}")
    print("Starting vertical wave effects with NEW bytebeat sounds in 3 seconds...")
    time.sleep(3)
    
    hdc = user32.GetDC(0)
    if not hdc:
        print("Failed to get desktop DC!")
        return
    
    # Backup original screen
    hdc_backup = gdi32.CreateCompatibleDC(hdc)
    hbm_backup = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(hdc_backup, hbm_backup)
    gdi32.BitBlt(hdc_backup, 0, 0, w, h, hdc, 0, 0, SRCCOPY)
    
    beat = ByteBeat()
    
    effects = [
        ("📊 Standard Wave 🎵 CHIPTUNE (8-bit game music)", vertical_wave_fixed, 8, 0),
        ("🎚️ Animated Wave 🎵 TECHNO (Bass pattern)", vertical_wave_animated, 8, 1),
        ("⚡ Fast Wave 🎵 ACID (Squelch bass)", vertical_wave_fast, 6, 2),
        ("🐢 Slow Wave 🎵 DREAMY (Chime melody)", vertical_wave_slow, 8, 3),
        ("💪 Strong Wave 🎵 DRUM LOOP (Percussive)", vertical_wave_strong, 8, 4),
        ("🔄 Double Wave 🎵 CRYSTAL (Clear arpeggios)", vertical_wave_double, 8, 5),
        ("⬇️ Reverse Wave 🎵 SPIRAL (Descending tones)", vertical_wave_reverse, 6, 6),
        ("💓 Pulsing Wave 🎵 HEARTBEAT (Thump rhythm)", vertical_wave_pulse, 8, 7),
        ("🌊 Extra Wave 1 🎵 AMBIENT (Atmospheric drone)", vertical_wave_fixed, 5, 8),
        ("🌊 Extra Wave 2 🎵 ROBOT (Voice effect)", vertical_wave_animated, 5, 9),
        ("🌊 Extra Wave 3 🎵 WATER (Droplet sounds)", vertical_wave_double, 5, 10),
        ("🌊 Extra Wave 4 🎵 FM SYNTH (Frequency mod)", vertical_wave_pulse, 5, 11),
    ]
    
    frame = 0
    variation = 0
    
    print("\n" + "=" * 50)
    print("STARTING VERTICAL WAVE EFFECTS")
    print("🎵 EACH WAVE HAS A UNIQUE BYTEBEAT MELODY!")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        for i, (name, effect, duration, sound_idx) in enumerate(effects):
            print(f"[{i+1}/{len(effects)}] {name} ({duration}s)")
            
            def make_sound_effect(effect_func, sound_idx):
                def sound_effect(hdc, w, h, frame):
                    # Play sound at intervals with variations
                    if frame % 25 == 0 or frame % 27 == 13:
                        nonlocal variation
                        beat.play_beat(sound_idx, frame, variation)
                        variation += 1
                    return effect_func(hdc, w, h, frame)
                return sound_effect
            
            sound_effect = make_sound_effect(effect, sound_idx)
            start_time = time.time()
            
            while time.time() - start_time < duration:
                frame = sound_effect(hdc, w, h, frame)
                time.sleep(0.033)
                
                if user32.GetAsyncKeyState(0x1B) & 0x8000:
                    print("\nESC pressed - stopping!")
                    break
            
            gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user")
    finally:
        print("\nRestoring screen...")
        gdi32.BitBlt(hdc, 0, 0, w, h, hdc_backup, 0, 0, SRCCOPY)
        user32.InvalidateRect(0, None, 0)
        time.sleep(0.5)
        
        gdi32.DeleteObject(hbm_backup)
        gdi32.DeleteDC(hdc_backup)
        user32.ReleaseDC(0, hdc)
        
        winmm.PlaySoundW(0, 0, 0)
        
        print("Screen restored to normal!")
        user32.MessageBoxW(0, "Vertical Wave Effect Complete!\n\nScreen restored to normal.\n🎵 12 NEW bytebeat sounds played!", 
                          "Complete", 0x00000040)

if __name__ == "__main__":
    main()