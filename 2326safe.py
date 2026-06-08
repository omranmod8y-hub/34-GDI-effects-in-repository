import time
import random
import win32gui
import win32con
import win32api

# 1. Invert Blocks
def effect_invert_blocks(hdc, sw, sh):
    x = random.randint(0, sw - 150)
    y = random.randint(0, sh - 150)
    w = random.randint(50, 300)
    h = random.randint(50, 300)
    win32gui.PatBlt(hdc, x, y, w, h, win32con.DSTINVERT)

# 2. Screen Shake (Slight displacement)
def effect_screen_shake(hdc, sw, sh):
    dx = random.randint(-10, 10)
    dy = random.randint(-10, 10)
    win32gui.BitBlt(hdc, dx, dy, sw, sh, hdc, 0, 0, win32con.SRCCOPY)

# 3. Random Colored Pixels
def effect_color_pixels(hdc, sw, sh):
    for _ in range(200):
        x = random.randint(0, sw)
        y = random.randint(0, sh)
        color = win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        win32gui.SetPixel(hdc, x, y, color)

# 4. Vertical Screen Melt
def effect_screen_melt(hdc, sw, sh):
    x = random.randint(0, sw)
    y = random.randint(0, 15)
    w = random.randint(50, 150)
    win32gui.BitBlt(hdc, x, y, w, sh, hdc, x, 0, win32con.SRCCOPY)

# 5. Random Lines
def effect_random_lines(hdc, sw, sh):
    color = win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    pen = win32gui.CreatePen(win32con.PS_SOLID, random.randint(1, 5), color)
    old_pen = win32gui.SelectObject(hdc, pen)
    win32gui.MoveToEx(hdc, random.randint(0, sw), random.randint(0, sh))
    win32gui.LineTo(hdc, random.randint(0, sw), random.randint(0, sh))
    win32gui.SelectObject(hdc, old_pen)
    win32gui.DeleteObject(pen)

# 6. Random Ellipses
def effect_ellipses(hdc, sw, sh):
    color = win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    brush = win32gui.CreateSolidBrush(color)
    old_brush = win32gui.SelectObject(hdc, brush)
    x1 = random.randint(0, sw)
    y1 = random.randint(0, sh)
    x2 = x1 + random.randint(30, 120)
    y2 = y1 + random.randint(30, 120)
    win32gui.Ellipse(hdc, x1, y1, x2, y2)
    win32gui.SelectObject(hdc, old_brush)
    win32gui.DeleteObject(brush)

# 7. Bouncing Text
def effect_bouncing_text(hdc, sw, sh):
    color = win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    win32gui.SetTextColor(hdc, color)
    win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
    x = random.randint(0, sw - 100)
    y = random.randint(0, sh - 30)
    win32gui.DrawText(hdc, "GDI SAFE DEMO", -1, (x, y, x + 300, y + 50), win32con.DT_SINGLELINE)

# 8. Block Inversion Pattern
def effect_pattern_invert(hdc, sw, sh):
    x = random.randint(0, sw - 200)
    y = random.randint(0, sh - 200)
    w = random.randint(100, 300)
    h = random.randint(100, 300)
    brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    old_brush = win32gui.SelectObject(hdc, brush)
    win32gui.PatBlt(hdc, x, y, w, h, win32con.PATINVERT)
    win32gui.SelectObject(hdc, old_brush)
    win32gui.DeleteObject(brush)

# 9. Block Stretch/Distort
def effect_stretch(hdc, sw, sh):
    x = random.randint(0, sw - 150)
    y = random.randint(0, sh - 150)
    w = random.randint(100, 200)
    h = random.randint(100, 200)
    win32gui.StretchBlt(
        hdc, 
        x + random.randint(-15, 15), 
        y + random.randint(-15, 15), 
        w + random.randint(-30, 30), 
        h + random.randint(-30, 30), 
        hdc, 
        x, y, w, h, 
        win32con.SRCCOPY
    )

# 10. Color Merge Wash
def effect_color_wash(hdc, sw, sh):
    x = random.randint(0, sw - 250)
    y = random.randint(0, sh - 250)
    w = random.randint(150, 400)
    h = random.randint(150, 400)
    brush = win32gui.CreateSolidBrush(win32api.RGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    old_brush = win32gui.SelectObject(hdc, brush)
    win32gui.BitBlt(hdc, x, y, w, h, hdc, x, y, win32con.MERGECOPY)
    win32gui.SelectObject(hdc, old_brush)
    win32gui.DeleteObject(brush)

def run_gdi_demo():
    # Initialize Screen Dimensions
    sw = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    sh = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    
    # Get Device Context for the whole screen
    hdc = win32gui.GetDC(0)
    
    effects = [
        ("1. Invert Blocks", effect_invert_blocks),
        ("2. Screen Shake", effect_screen_shake),
        ("3. Color Pixels", effect_color_pixels),
        ("4. Screen Melt", effect_screen_melt),
        ("5. Random Lines", effect_random_lines),
        ("6. Ellipses", effect_ellipses),
        ("7. Text Draw", effect_bouncing_text),
        ("8. Pattern Invert", effect_pattern_invert),
        ("9. Stretch Distort", effect_stretch),
        ("10. Color Wash", effect_color_wash)
    ]
    
    duration_per_effect = 4.0 # seconds
    
    print("Starting GDI Visual Effects Demo...")
    print("This demonstration will run through 10 safe GDI operations.")
    print("The screen will automatically refresh and return to normal when finished.")
    time.sleep(2)
    
    for name, effect_func in effects:
        print(f"Running: {name}")
        start_time = time.time()
        
        while time.time() - start_time < duration_per_effect:
            effect_func(hdc, sw, sh)
            time.sleep(0.01) # Small delay to regulate speed and CPU usage
            
    # Clean up handles
    win32gui.ReleaseDC(0, hdc)
    
    print("\nDemo finished. Restoring screen...")
    # Force redraw of the entire desktop window to clear visual remnants
    win32gui.InvalidateRect(0, None, True)

if __name__ == "__main__":
    run_gdi_demo()