import ctypes
import random
import time
import math
import threading

# --- Windows API Constants ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
shcore = ctypes.windll.shcore

SRCCOPY = 0x00CC0020
PATINVERT = 0x005A0049
DSTINVERT = 0x00550009
NOTSRCERASE = 0x001100A6
MB_YESNO = 0x04
IDYES = 6
MB_ICONWARNING = 0x30
MB_TOPMOST = 0x40000

# Global screen variables
HDC = user32.GetDC(0)
SW = user32.GetSystemMetrics(0)
SH = user32.GetSystemMetrics(1)
PAYLOAD_TIME = 5  # Seconds per payload

def init_dpi():
    """Equivalent to InitDPI in C++"""
    try:
        shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()

# --- Placeholder Payloads (Simulating 1-10) ---
def payload_shaker(t):
    end = time.time() + t
    while time.time() < end:
        gdi32.BitBlt(HDC, random.randint(-10, 10), random.randint(-10, 10), SW, SH, HDC, 0, 0, SRCCOPY)
        time.sleep(0.01)

def payload_invert(t):
    end = time.time() + t
    while time.time() < end:
        gdi32.BitBlt(HDC, 0, 0, SW, SH, HDC, 0, 0, DSTINVERT)
        time.sleep(0.1)

def payload_melt(t):
    end = time.time() + t
    while time.time() < end:
        x = random.randint(0, SW)
        gdi32.BitBlt(HDC, x, 10, 100, SH, HDC, x, 0, SRCCOPY)
        time.sleep(0.001)

# --- Placeholder Shaders (Simulating 1-16) ---
def shader_trippy(t):
    end = time.time() + t
    while time.time() < end:
        # Complex mathematical GDI movement
        gdi32.StretchBlt(HDC, 10, 10, SW-20, SH-20, HDC, 0, 0, SW, SH, SRCCOPY)
        gdi32.BitBlt(HDC, 0, 0, SW, SH, HDC, 0, 0, 0x999999) # Random pattern
        time.sleep(0.05)

# --- Background Threads ---
def message_box_payload():
    """Simulates the background message box thread"""
    for _ in range(5):
        time.sleep(3)
        # Using a non-blocking thread for a warning
        threading.Thread(target=lambda: user32.MessageBoxW(0, "Still here?", "easdrogen", 0x30)).start()

def windows_corruption_payload():
    """SIMULATED: In a real malware this would be dangerous. Here, it just flickers."""
    print("[Safe] Background 'Corruption' Thread Started")
    end = time.time() + 20
    while time.time() < end:
        gdi32.PatBlt(HDC, random.randint(0, SW), random.randint(0, SH), 100, 100, PATINVERT)
        time.sleep(0.5)

# --- Main Logic ---
def main():
    init_dpi()

    # Warning 1
    res = user32.MessageBoxW(None, "What you have just executed is a malware.\nYou might lose all of your data if you continue!\nStill execute it?", "easdrogen.exe", MB_YESNO | MB_TOPMOST | MB_ICONWARNING)
    if res != IDYES: return

    # Warning 2
    res = user32.MessageBoxW(None, "THIS IS THE LAST WARNING!\nTHE CREATOR WILL NOT BE RESPONSIBLE FOR DESTRUCTION!\nSTILL CONTINUE?", "easdrogen.exe - LAST WARNING", MB_YESNO | MB_TOPMOST | MB_ICONWARNING)
    if res != IDYES: return

    # Start background threads (Audio simulation skipped for system safety)
    threading.Thread(target=message_box_payload, daemon=True).start()
    
    # Execute Payloads 1-10
    print("Running GDI Payloads...")
    payloads = [payload_shaker, payload_invert, payload_melt] # Add more here
    for p in payloads:
        p(PAYLOAD_TIME)

    # Execute Shaders 1-16
    print("Running Shader Payloads...")
    shaders = [shader_trippy] # Add more here
    for s in shaders:
        s(PAYLOAD_TIME)

    # Final Phase
    threading.Thread(target=windows_corruption_payload, daemon=True).start()
    
    print("Payload complete. Waiting 20s for cleanup...")
    time.sleep(20)
    
    # Cleanup
    user32.ReleaseDC(0, HDC)
    user32.InvalidateRect(0, None, True)
    print("System Restored.")

if __name__ == "__main__":
    main()