import sys
import time
import math
import ctypes
import tkinter as tk
from ctypes import wintypes

# --- Windows GDI & User DLL Bindings ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

SRCCOPY = 0x00CC0020
PATINVERT = 0x005A0049
BLACKNESS = 0x00000042

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long)
    ]

# Setup global screen dimensions
sw = user32.GetSystemMetrics(0)
sh = user32.GetSystemMetrics(1)

# Chronological timeline intervals from the C# source code
flip_times = [
    126, 129, 133, 136, 140, 143, 147, 150, 155, 158, 162, 165, 169, 172, 176, 179,
    184, 187, 191, 194, 198, 201, 205, 208, 213, 216, 220, 223, 227, 230, 234, 237,
    242, 245, 249, 252, 256, 259, 263, 266, 271, 274, 278, 281, 285, 286, 288, 292,
    295, 297, 300, 303, 307, 310, 314, 317, 321, 324, 329, 332, 336, 339, 343, 346,
    350, 353, 355, 358, 361, 365, 368, 372, 375, 379, 382, 387, 390, 394, 397, 401,
    404, 408, 411, 416, 419, 423, 426, 430, 433, 437
]

flip_times2 = [
    440, 443, 449, 454, 456, 460, 468, 476, 481, 486, 497, 501, 504, 506, 512, 514,
    518, 522, 527, 531, 533, 536, 540, 548, 552, 557, 561, 563, 569, 572, 576, 580,
    582, 585
]

flip_times1 = [
    454, 476, 497, 512, 531, 548, 569, 585
]

# --- Helper function for Affine Rotation Matrix (PlgBlt) ---
def get_parallelogram(scale_x, angle_deg):
    theta = math.radians(angle_deg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    cx, cy = sw / 2.0, sh / 2.0
    
    def transform(px, py):
        x_scaled = px * scale_x
        rx = x_scaled * cos_t - py * sin_t
        ry = x_scaled * sin_t + py * cos_t
        return int(cx + rx), int(cy + ry)
    
    # Calculate transformed upper-left, upper-right, and lower-left corner coordinates
    x0, y0 = transform(-sw / 2.0, -sh / 2.0)
    x1, y1 = transform(sw / 2.0, -sh / 2.0)
    x2, y2 = transform(-sw / 2.0, sh / 2.0)
    
    pts = (POINT * 3)()
    pts[0].x, pts[0].y = x0, y0
    pts[1].x, pts[1].y = x1, y1
    pts[2].x, pts[2].y = x2, y2
    return pts


# --- Screen Capture ---
try:
    # Command shell to minimize all windows
    user32.ShowWindow(user32.GetShellWindow(), 6)
    ctypes.windll.shell32.ShellExecuteW(None, "open", "shell:::{3080F90D-D7AD-11D9-BD98-0000947B0257}", None, None, 5)
except Exception:
    pass

time.sleep(0.3)

# Capture current Desktop state into an offscreen GDI compatible memory context
desktop_dc = user32.GetDC(0)
mem_dc = gdi32.CreateCompatibleDC(desktop_dc)
hbitmap = gdi32.CreateCompatibleBitmap(desktop_dc, sw, sh)
gdi32.SelectObject(mem_dc, hbitmap)
gdi32.BitBlt(mem_dc, 0, 0, sw, sh, desktop_dc, 0, 0, SRCCOPY)
user32.ReleaseDC(0, desktop_dc)


# --- Create Tkinter Window Shell ---
root = tk.Tk()
root.overrideredirect(True)          # Borderless Window
root.attributes("-topmost", True)    # Always on Top
root.state("zoomed")                 # Maximized State
root.config(cursor="none")           # Hide mouse cursor

root.update()
hwnd = root.winfo_id()
window_dc = user32.GetDC(hwnd)

start_time = time.time()

# Main timeline iteration tick
def tick():
    elapsed_ms = (time.time() - start_time) * 1000.0
    frame_index = int(math.floor(elapsed_ms / 33.33333))
    
    # End timeline boundary check
    if frame_index >= 1260:
        cleanup_and_exit()
        return

    # Visual State Processing
    if frame_index < 438:
        flips = sum(1 for t in flip_times if t <= frame_index)
        scale_x = -1.0 if (flips % 2 != 0) else 1.0
        angle = -20.0 if frame_index >= 286 else 0.0
        
        if angle == 0.0:
            if scale_x == 1.0:
                gdi32.BitBlt(window_dc, 0, 0, sw, sh, mem_dc, 0, 0, SRCCOPY)
            else:
                # Perform horizontal scale flips using inverse destination width
                gdi32.StretchBlt(window_dc, sw, 0, -sw, sh, mem_dc, 0, 0, sw, sh, SRCCOPY)
        else:
            # Perform rotation matrix mappings
            pts = get_parallelogram(scale_x, angle)
            gdi32.PlgBlt(window_dc, ctypes.byref(pts), mem_dc, 0, 0, sw, sh, 0, 0, 0)
            
    elif frame_index < 665:
        flips1 = sum(1 for t in flip_times1 if t <= frame_index)
        scale_x1 = -1.0 if (flips1 % 2 != 0) else 1.0

        flips2 = sum(1 for t in flip_times2 if t <= frame_index)
        scale_x2 = -1.0 if (flips2 % 2 != 0) else 1.0
        
        # Scaling + Translate animations starting at frame 622
        grid_scale = 1.0
        grid_tx = 0.0
        grid_ty = 0.0
        
        if frame_index >= 622:
            anim_progress = min(1.0, (frame_index - 622) / 15.0) # 15 frames = 500ms
            grid_scale = 1.0 + (0.3 - 1.0) * anim_progress
            grid_tx = (sw * 0.13817330210772832 * 3.0) * anim_progress
            grid_ty = (sh * 0.3541666666666667 * 3.0) * anim_progress
            
        w = int(sw * grid_scale)
        h = int(sh * grid_scale)
        tx = int(grid_tx)
        ty = int(grid_ty)
        w_half = w // 2
        
        # Draw Left Half (bg2) into dynamic canvas coordinates
        if scale_x1 == 1.0:
            gdi32.StretchBlt(window_dc, tx, ty, w_half, h, mem_dc, 0, 0, sw // 2, sh, SRCCOPY)
        else:
            gdi32.StretchBlt(window_dc, tx + w_half, ty, -w_half, h, mem_dc, 0, 0, sw // 2, sh, SRCCOPY)
            
        # Draw Right Half (bg3) into dynamic canvas coordinates
        if scale_x2 == 1.0:
            gdi32.StretchBlt(window_dc, tx + w_half, ty, w_half, h, mem_dc, sw // 2, 0, sw // 2, sh, SRCCOPY)
        else:
            gdi32.StretchBlt(window_dc, tx + w, ty, -w_half, h, mem_dc, sw // 2, 0, sw // 2, sh, SRCCOPY)
            
    else:
        # Hide layouts completely (Set display context to black)
        gdi32.PatBlt(window_dc, 0, 0, sw, sh, BLACKNESS)

    root.after(10, tick)

def cleanup_and_exit():
    user32.ReleaseDC(hwnd, window_dc)
    gdi32.DeleteObject(hbitmap)
    gdi32.DeleteDC(mem_dc)
    root.destroy()
    sys.exit(0)

def on_key(event):
    if event.keysym == "Escape":
        cleanup_and_exit()

root.bind("<Key>", on_key)
root.after(10, tick)
root.mainloop()