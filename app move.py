import ctypes
import math
import time
import random
import threading

# Windows API Setup
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Struct for window coordinates
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), 
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

def is_real_window(hwnd):
    """Filters out hidden background processes and system components."""
    if not user32.IsWindowVisible(hwnd):
        return False
    
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return False
    
    # Ignore the Taskbar and Desktop
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    title = buf.value
    forbidden = ["Program Manager", "Start", "Taskbar"]
    if any(f in title for f in forbidden):
        return False
        
    return True

def move_windows_effect():
    """Moves all visible windows in a circular floating motion."""
    # List to store window handles and their original centers
    window_data = []

    def enum_handler(hwnd, lParam):
        if is_real_window(hwnd):
            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            center_x = rect.left
            center_y = rect.top
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            window_data.append([hwnd, center_x, center_y, width, height])
        return True

    # Find all windows
    enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(enum_proc(enum_handler), 0)

    print(f"Floating {len(window_data)} windows. Press Ctrl+C to stop.")

    angle = 0
    try:
        while True:
            angle += 0.1
            # Calculate shift based on a circle
            offset_x = int(math.sin(angle) * 15)
            offset_y = int(math.cos(angle) * 15)

            for data in window_data:
                hwnd, orig_x, orig_y, w, h = data
                # Check if window still exists
                if user32.IsWindow(hwnd):
                    user32.MoveWindow(hwnd, orig_x + offset_x, orig_y + offset_y, w, h, True)
            
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nStopping and returning windows to original positions...")
        for data in window_data:
            hwnd, orig_x, orig_y, w, h = data
            if user32.IsWindow(hwnd):
                user32.MoveWindow(hwnd, orig_x, orig_y, w, h, True)

if __name__ == "__main__":
    # Ensure DPI awareness for accurate coordinates
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()

    move_windows_effect()