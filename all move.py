import ctypes
import math
import time

# Windows API Setup
user32 = ctypes.windll.user32
shcore = ctypes.windll.shcore

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), 
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

def get_window_info(hwnd):
    """Helper to capture window position and size."""
    if not hwnd or not user32.IsWindow(hwnd):
        return None
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return {
        "hwnd": hwnd,
        "x": rect.left,
        "y": rect.top,
        "w": rect.right - rect.left,
        "h": rect.bottom - rect.top
    }

def move_all_effect():
    targets = []
    seen_hwnds = set()

    # 1. Collect Regular Application Windows
    def enum_handler(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            # Only grab windows that have a title
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                info = get_window_info(hwnd)
                if info and hwnd not in seen_hwnds:
                    targets.append(info)
                    seen_hwnds.add(hwnd)
        return True

    enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(enum_proc(enum_handler), 0)

    # 2. Collect System Components (Taskbar and Desktop)
    system_classes = [
        "Shell_TrayWnd",            # Primary Taskbar
        "Shell_SecondaryTrayWnd",   # Multi-monitor Taskbars
        "Progman",                  # Desktop Icons
    ]

    for cls in system_classes:
        hwnd = user32.FindWindowW(cls, None)
        if hwnd and hwnd not in seen_hwnds:
            info = get_window_info(hwnd)
            if info:
                targets.append(info)
                seen_hwnds.add(hwnd)

    # 3. Collect Wallpaper Layers (WorkerW)
    def enum_workerw(hwnd, lParam):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf, 256)
        if buf.value == "WorkerW":
            info = get_window_info(hwnd)
            if info and hwnd not in seen_hwnds:
                targets.append(info)
                seen_hwnds.add(hwnd)
        return True
    
    user32.EnumWindows(enum_proc(enum_workerw), 0)

    print(f"Floating {len(targets)} elements (Apps + Taskbar + Desktop).")
    print("Press Ctrl+C to stop.")

    angle = 0
    try:
        while True:
            angle += 0.1
            # Intensity of the float (20 pixel radius)
            offset_x = int(math.sin(angle) * 20)
            offset_y = int(math.cos(angle) * 20)

            for item in targets:
                if user32.IsWindow(item["hwnd"]):
                    # Using MoveWindow for smooth updates
                    user32.MoveWindow(
                        item["hwnd"], 
                        item["x"] + offset_x, 
                        item["y"] + offset_y, 
                        item["w"], 
                        item["h"], 
                        True
                    )
            
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping... Resetting everything to original positions.")
        for item in targets:
            if user32.IsWindow(item["hwnd"]):
                user32.MoveWindow(item["hwnd"], item["x"], item["y"], item["w"], item["h"], True)

if __name__ == "__main__":
    # Ensure coordinates are correct on high-DPI screens
    try:
        shcore.SetProcessDpiAwareness(1)
    except:
        user32.SetProcessDPIAware()

    move_all_effect()