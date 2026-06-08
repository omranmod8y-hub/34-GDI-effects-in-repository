import ctypes
from ctypes import wintypes
import math
import random
import time
import threading

# Windows constants
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SRCCOPY = 0x00CC0020
SRCINVERT = 0x00660046
SRCPAINT = 0x00EE0086
PATINVERT = 0x5A0049
NOTSRCCOPY = 0x00330008
CAPTUREBLT = 0x40000000

# Load Windows libraries
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

def get_desktop_dc():
    return user32.GetDC(0)

def release_dc(hdc):
    user32.ReleaseDC(0, hdc)

def get_screen_size():
    return user32.GetSystemMetrics(SM_CXSCREEN), user32.GetSystemMetrics(SM_CYSCREEN)

def ran_tunnel():
    """Random stretching effect"""
    sw, sh = get_screen_size()
    while True:
        hdc = get_desktop_dc()
        if hdc:
            w = random.randint(0, sw)
            h = random.randint(0, sh)
            gdi32.StretchBlt(hdc, 0, 0, w, h, hdc, 0, 0, sw, sh, SRCCOPY)
            release_dc(hdc)
        time.sleep(0.1)

def cube_color_half():
    """Random colored rectangle patching"""
    sw, sh = get_screen_size()
    while True:
        hdc = get_desktop_dc()
        if hdc:
            brush = gdi32.CreateSolidBrush(
                (random.randint(0, 128) << 16) | 
                (random.randint(0, 128) << 8) | 
                random.randint(0, 128)
            )
            gdi32.SelectObject(hdc, brush)
            gdi32.PatBlt(hdc, 0, 0, random.randint(0, sw), random.randint(0, sh), PATINVERT)
            gdi32.DeleteObject(brush)
            release_dc(hdc)
        time.sleep(0.01)

def weird_invert():
    """Screen invert effect"""
    sw, sh = get_screen_size()
    while True:
        hdc = get_desktop_dc()
        if hdc:
            gdi32.BitBlt(hdc, 1, 1, sw, sh, hdc, 0, 0, SRCINVERT)
            gdi32.BitBlt(hdc, -1, -1, sw, sh, hdc, 0, 0, SRCINVERT)
            release_dc(hdc)
        time.sleep(0.01)

def light():
    """Lighten screen effect"""
    sw, sh = get_screen_size()
    while True:
        hdc = get_desktop_dc()
        if hdc:
            gdi32.BitBlt(hdc, 1, 0, sw, sh, hdc, 0, 0, SRCPAINT)
            gdi32.BitBlt(hdc, -1, 0, sw, sh, hdc, 0, 0, SRCPAINT)
            gdi32.BitBlt(hdc, 0, 1, sw, sh, hdc, 0, 0, SRCPAINT)
            gdi32.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, SRCPAINT)
            release_dc(hdc)
        time.sleep(0.01)

def light_dif():
    """Mixed light/dark effect"""
    sw, sh = get_screen_size()
    while True:
        hdc = get_desktop_dc()
        if hdc:
            gdi32.BitBlt(hdc, 1, 0, sw, sh, hdc, 0, 0, SRCPAINT)
            gdi32.BitBlt(hdc, -1, 0, sw, sh, hdc, 0, 0, SRCPAINT)
            gdi32.BitBlt(hdc, 0, 1, sw, sh, hdc, 0, 0, 0x008800C6)  # SRCAND
            gdi32.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, 0x008800C6)
            release_dc(hdc)
        time.sleep(0.01)

def text_out():
    """Draw random text on screen"""
    sw, sh = get_screen_size()
    text = "Memoxide"
    while True:
        hdc = get_desktop_dc()
        if hdc:
            gdi32.SetBkColor(hdc, random.randint(0, 0xFFFFFF))
            gdi32.SetTextColor(hdc, random.randint(0, 0xFFFFFF))
            font = gdi32.CreateFontW(32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
            gdi32.SelectObject(hdc, font)
            gdi32.TextOutW(hdc, random.randint(0, sw), random.randint(0, sh), text, len(text))
            gdi32.DeleteObject(font)
            release_dc(hdc)
        time.sleep(0.01)

def move_screen_invert():
    """Screen shifting with invert"""
    sw, sh = get_screen_size()
    while True:
        hdc = get_desktop_dc()
        if hdc:
            gdi32.BitBlt(hdc, 0, -1, sw, sh, hdc, 0, 0, SRCCOPY)
            gdi32.BitBlt(hdc, 0, sh - 1, sw, sh, hdc, 0, 0, NOTSRCCOPY)
            gdi32.BitBlt(hdc, -1, 0, sw, sh, hdc, 0, 0, SRCCOPY)
            gdi32.BitBlt(hdc, sw - 1, 0, sw, sh, hdc, 0, 0, NOTSRCCOPY)
            release_dc(hdc)
        time.sleep(0.01)

def text_out2():
    """Draw Destruction text"""
    sw, sh = get_screen_size()
    text = "Destruction"
    while True:
        hdc = get_desktop_dc()
        if hdc:
            gdi32.SetBkColor(hdc, random.randint(0, 0xFFFFFF))
            gdi32.SetTextColor(hdc, random.randint(0, 0xFFFFFF))
            font = gdi32.CreateFontW(32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
            gdi32.SelectObject(hdc, font)
            gdi32.TextOutW(hdc, random.randint(0, sw), random.randint(0, sh), text, len(text))
            gdi32.DeleteObject(font)
            release_dc(hdc)
        time.sleep(0.004)

def colors_half():
    """Full screen color patching"""
    sw, sh = get_screen_size()
    while True:
        hdc = get_desktop_dc()
        if hdc:
            brush = gdi32.CreateSolidBrush(
                (random.randint(0, 128) << 16) | 
                (random.randint(0, 128) << 8) | 
                random.randint(0, 128)
            )
            gdi32.SelectObject(hdc, brush)
            gdi32.PatBlt(hdc, 0, 0, sw, sh, PATINVERT)
            gdi32.DeleteObject(brush)
            release_dc(hdc)
        time.sleep(0.01)

def weird_screen_movement():
    """Random screen chunk movement"""
    sw, sh = get_screen_size()
    while True:
        hdc = get_desktop_dc()
        if hdc:
            x1 = random.randint(0, 10)
            y1 = random.randint(0, 10)
            x2 = random.randint(0, 10)
            y2 = random.randint(0, 10)
            w = random.randint(0, sw)
            h = random.randint(0, sh)
            gdi32.BitBlt(hdc, x1, y1, w, h, hdc, x2, y2, SRCCOPY)
            release_dc(hdc)
        time.sleep(0.001)

def cursor_text():
    """Text follows cursor"""
    text = "Hello!"
    cursor = wintypes.POINT()
    while True:
        hdc = get_desktop_dc()
        if hdc:
            user32.GetCursorPos(ctypes.byref(cursor))
            gdi32.SetBkColor(hdc, random.randint(0, 0xFFFFFF))
            gdi32.SetTextColor(hdc, random.randint(0, 0xFFFFFF))
            font = gdi32.CreateFontW(24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
            gdi32.SelectObject(hdc, font)
            gdi32.TextOutW(hdc, cursor.x, cursor.y, text, len(text))
            gdi32.DeleteObject(font)
            release_dc(hdc)
        time.sleep(0.01)

def icons():
    """Draw random system icons"""
    sw, sh = get_screen_size()
    icon_ids = [32512, 32513, 32514, 32515]  # IDI_APPLICATION, IDI_HAND, IDI_QUESTION, IDI_EXCLAMATION
    while True:
        hdc = get_desktop_dc()
        if hdc:
            icon = user32.LoadIconW(0, icon_ids[random.randint(0, 3)])
            user32.DrawIcon(hdc, random.randint(0, sw), random.randint(0, sh), icon)
            release_dc(hdc)
        time.sleep(0.01)

def negative_invert():
    """Negative screen invert effect"""
    sw, sh = get_screen_size()
    while True:
        hdc = get_desktop_dc()
        if hdc:
            gdi32.BitBlt(hdc, 1, 1, sw, sh, hdc, 0, 0, 0x999999)
            gdi32.BitBlt(hdc, -1, -1, sw, sh, hdc, 0, 0, 0x999999)
            gdi32.BitBlt(hdc, 1, -1, sw, sh, hdc, 0, 0, 0x999999)
            gdi32.BitBlt(hdc, -1, 1, sw, sh, hdc, 0, 0, 0x999999)
            release_dc(hdc)
        time.sleep(0.01)

def redrawer():
    """Force screen redraw"""
    while True:
        user32.InvalidateRect(0, None, 0)
        time.sleep(1)

def sines():
    """Sine wave screen distortion"""
    sw, sh = get_screen_size()
    angle = 0
    while True:
        hdc = get_desktop_dc()
        if hdc:
            brush = gdi32.CreateSolidBrush(
                (random.randint(0, 128) << 16) | 
                (random.randint(0, 128) << 8) | 
                random.randint(0, 128)
            )
            gdi32.SelectObject(hdc, brush)
            i = 0
            while i < sw + sh:
                a = int(math.sin(angle) * 20)
                gdi32.BitBlt(hdc, 0, int(i), sw, 1, hdc, a, int(i), SRCCOPY)
                gdi32.BitBlt(hdc, 0, int(i), sw, 1, hdc, a, int(i), PATINVERT)
                gdi32.BitBlt(hdc, int(i), 0, 1, sh, hdc, int(i), a, SRCCOPY)
                gdi32.BitBlt(hdc, int(i), 0, 1, sh, hdc, int(i), a, PATINVERT)
                angle += math.pi / 40
                i += 0.99
            gdi32.DeleteObject(brush)
            release_dc(hdc)
        time.sleep(0.01)

def play_sound(buffer_size=240000):
    """Generate and play bytebeat sound"""
    import pyaudio
    import numpy as np
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt8, channels=1, rate=8000, output=True)
    
    t = 0
    samples = bytearray(buffer_size)
    for i in range(buffer_size):
        samples[i] = (i & 4096 and ((i * (i ^ i % 9) | i >> 3) >> 1) or 255) & 0xFF
    
    stream.write(bytes(samples))
    stream.stop_stream()
    stream.close()
    p.terminate()

def sound1(): play_sound()
def sound2(): play_sound()
def sound3(): play_sound()
def sound4(): play_sound()
def sound5(): play_sound()
def sound7(): play_sound()
def sound8(): play_sound()
def sound9(): play_sound()
def sound11(): play_sound()

def run_effect(effect_func, sound_func, duration=30):
    """Run an effect with sound for specified duration"""
    thread = threading.Thread(target=effect_func, daemon=True)
    thread.start()
    
    sound_thread = threading.Thread(target=sound_func, daemon=True)
    sound_thread.start()
    
    time.sleep(duration)
    return thread

def main():
    if user32.MessageBoxW(0, "Warning! This software is GDI Only.\r\nAre you sure you want to run it?", 
                          "Memoxide.exe (safety version)", 0x00000004 | 0x00000030 | 0x00001000) == 7:  # IDNO
        return
    
    if user32.MessageBoxW(0, "it will not overwrite the MBR or make the computer unbootable!\r\nstill want to run it?",
                          "LAST WARNING!!!", 0x00000004 | 0x00000030 | 0x00001000) == 7:
        return
    
    print("GDI Effects Starting - Press Ctrl+C to stop all effects")
    
    effects = [
        (ran_tunnel, sound1),
        (cube_color_half, sound2),
        (weird_invert, sound3),
        (light, sound4),
        (light_dif, sound5),
        (text_out, None),  # sound6 requires external file
        (move_screen_invert, sound7),
        (text_out2, sound8),
        (weird_screen_movement, sound9),
        (negative_invert, None),  # sound10 requires external file
        (sines, sound11)
    ]
    
    for i, (effect, sound) in enumerate(effects):
        print(f"Running effect {i+1}/{len(effects)} for 30 seconds...")
        thread = threading.Thread(target=effect, daemon=True)
        thread.start()
        
        if sound:
            sound_thread = threading.Thread(target=sound, daemon=True)
            sound_thread.start()
        
        time.sleep(30)
        
        # Refresh screen
        user32.InvalidateRect(0, None, 0)
        time.sleep(0.1)
    
    print("All effects completed!")

if __name__ == "__main__":
    print("=" * 60)
    print("GDI Screen Effects - This affects your actual desktop!")
    print("Press Ctrl+C at any time to stop")
    print("=" * 60)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")
        user32.InvalidateRect(0, None, 0)