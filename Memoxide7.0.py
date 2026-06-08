import ctypes
import random
import time
import math
import threading
import sys

# --- Windows API Constants ---
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32
winmm = ctypes.windll.winmm

SRCCOPY = 0x00CC0020
SRCINVERT = 0x00660046
SRCPAINT = 0x00EE0086
SRCAND = 0x008800C6
NOTSRCCOPY = 0x00330008
PATINVERT = 0x005A0049
DSTINVERT = 0x00550009

MB_YESNO = 0x04
MB_ICONEXCLAMATION = 0x30
MB_SYSTEMMODAL = 0x1000
IDYES = 6
IDNO = 7

# Global screen variables
HDC = None
SW = 0
SH = 0

def init_gdi():
    global HDC, SW, SH
    HDC = user32.GetDC(0)
    SW = user32.GetSystemMetrics(0)
    SH = user32.GetSystemMetrics(1)

def cleanup_gdi():
    user32.ReleaseDC(0, HDC)
    user32.InvalidateRect(0, None, True)

# --- Sound Functions ---
def sound1():
    try:
        winmm.PlaySoundW("sound1.wav", None, 0x00020000 | 0x00000001)
    except:
        pass

def sound2():
    try:
        winmm.PlaySoundW("sound2.wav", None, 0x00020000 | 0x00000001)
    except:
        pass

def sound3():
    try:
        winmm.PlaySoundW("sound3.wav", None, 0x00020000 | 0x00000001)
    except:
        pass

def sound4():
    try:
        winmm.PlaySoundW("sound4.wav", None, 0x00020000 | 0x00000001)
    except:
        pass

def sound5():
    try:
        winmm.PlaySoundW("sound5.wav", None, 0x00020000 | 0x00000001)
    except:
        pass

def sound7():
    try:
        winmm.PlaySoundW("sound7.wav", None, 0x00020000 | 0x00000001)
    except:
        pass

def sound8():
    try:
        winmm.PlaySoundW("sound8.wav", None, 0x00020000 | 0x00000001)
    except:
        pass

def sound9():
    try:
        winmm.PlaySoundW("sound9.wav", None, 0x00020000 | 0x00000001)
    except:
        pass

def sound11():
    try:
        winmm.PlaySoundW("sound11.wav", None, 0x00020000 | 0x00000001)
    except:
        pass

# --- GDI Payload Threads ---
def ran_tunnel(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.StretchBlt(hdc, 0, 0, random.randint(1, SW), random.randint(1, SH), 
                         hdc, 0, 0, SW, SH, SRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.1)

def cube_color_half(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        brush = gdi32.CreateSolidBrush(ctypes.windll.gdi32.RGB(
            random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)))
        gdi32.SelectObject(hdc, brush)
        gdi32.PatBlt(hdc, 0, 0, random.randint(1, SW), random.randint(1, SH), PATINVERT)
        gdi32.DeleteObject(brush)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def weird_invert(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 1, 1, SW, SH, hdc, 0, 0, SRCINVERT)
        gdi32.BitBlt(hdc, -1, -1, SW, SH, hdc, 0, 0, SRCINVERT)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def light(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 1, 0, SW, SH, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, -1, 0, SW, SH, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, 0, 1, SW, SH, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, 0, -1, SW, SH, hdc, 0, 0, SRCPAINT)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def light_dif(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 1, 0, SW, SH, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, -1, 0, SW, SH, hdc, 0, 0, SRCPAINT)
        gdi32.BitBlt(hdc, 0, 1, SW, SH, hdc, 0, 0, SRCAND)
        gdi32.BitBlt(hdc, 0, -1, SW, SH, hdc, 0, 0, SRCAND)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def text_out(stop_event):
    text = "Memoxide"
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.SetBkColor(hdc, ctypes.windll.gdi32.RGB(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.SetTextColor(hdc, ctypes.windll.gdi32.RGB(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        user32.TextOutW(hdc, random.randint(0, SW), random.randint(0, SH), text, len(text))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.001)

def move_screen_invert(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 0, -1, SW, SH, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, 0, SH - 1, SW, SH, hdc, 0, 0, NOTSRCCOPY)
        gdi32.BitBlt(hdc, -1, 0, SW, SH, hdc, 0, 0, SRCCOPY)
        gdi32.BitBlt(hdc, SW - 1, 0, SW, SH, hdc, 0, 0, NOTSRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def text_out2(stop_event):
    text = "Destruction"
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.SetBkColor(hdc, ctypes.windll.gdi32.RGB(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.SetTextColor(hdc, ctypes.windll.gdi32.RGB(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        user32.TextOutW(hdc, random.randint(0, SW), random.randint(0, SH), text, len(text))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.004)

def colors_half(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        brush = gdi32.CreateSolidBrush(ctypes.windll.gdi32.RGB(
            random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)))
        gdi32.SelectObject(hdc, brush)
        gdi32.PatBlt(hdc, 0, 0, SW, SH, PATINVERT)
        gdi32.DeleteObject(brush)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def weird_screen_movement(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, random.randint(0, 10), random.randint(0, 10),
                     random.randint(1, SW), random.randint(1, SH),
                     hdc, random.randint(0, 10), random.randint(0, 10), SRCCOPY)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.001)

def cursor_text(stop_event):
    text = "Hello!"
    cursorPt = ctypes.wintypes.POINT()
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        user32.GetCursorPos(ctypes.byref(cursorPt))
        gdi32.SetBkColor(hdc, ctypes.windll.gdi32.RGB(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        gdi32.SetTextColor(hdc, ctypes.windll.gdi32.RGB(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        user32.TextOutW(hdc, cursorPt.x, cursorPt.y, text, len(text))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def icons(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        user32.DrawIconW(hdc, random.randint(0, SW), random.randint(0, SH), 
                         user32.LoadIconW(0, 32512))  # IDI_ERROR
        user32.DrawIconW(hdc, random.randint(0, SW), random.randint(0, SH), 
                         user32.LoadIconW(0, 32515))  # IDI_WARNING
        user32.DrawIconW(hdc, random.randint(0, SW), random.randint(0, SH), 
                         user32.LoadIconW(0, 32512))
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def negative_invert(stop_event):
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        gdi32.BitBlt(hdc, 1, 1, SW, SH, hdc, 0, 0, 0x999999)
        gdi32.BitBlt(hdc, -1, -1, SW, SH, hdc, 0, 0, 0x999999)
        gdi32.BitBlt(hdc, 1, -1, SW, SH, hdc, 0, 0, 0x999999)
        gdi32.BitBlt(hdc, -1, 1, SW, SH, hdc, 0, 0, 0x999999)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

def redrawer(stop_event):
    while not stop_event.is_set():
        user32.InvalidateRect(0, None, True)
        time.sleep(1)

def sines(stop_event):
    angle = 0
    while not stop_event.is_set():
        hdc = user32.GetDC(0)
        brush = gdi32.CreateSolidBrush(ctypes.windll.gdi32.RGB(
            random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)))
        gdi32.SelectObject(hdc, brush)
        for i in range(0, SW + SH, 1):
            a = int(math.sin(angle) * 20)
            gdi32.BitBlt(hdc, 0, i, SW, 1, hdc, a, i, SRCCOPY)
            gdi32.BitBlt(hdc, 0, i, SW, 1, hdc, a, i, PATINVERT)
            gdi32.BitBlt(hdc, i, 0, 1, SH, hdc, i, a, SRCCOPY)
            gdi32.BitBlt(hdc, i, 0, 1, SH, hdc, i, a, PATINVERT)
            angle += math.pi / 40
        gdi32.DeleteObject(brush)
        user32.ReleaseDC(0, hdc)
        time.sleep(0.01)

# --- Main Execution ---
def main():
    init_gdi()
    
    # Warning dialogs
    result = user32.MessageBoxW(None, 
        "Warning! This software is GDI Only.\r\nAre you sure you want to run it?",
        "Memoxide.exe (safety version)",
        MB_YESNO | MB_ICONEXCLAMATION | MB_SYSTEMMODAL)
    if result != IDYES:
        cleanup_gdi()
        return
    
    result = user32.MessageBoxW(None,
        "it will save flie\r\nstill want to run it?",
        "LAST WARNING!!!",
        MB_YESNO | MB_ICONEXCLAMATION | MB_SYSTEMMODAL)
    if result != IDYES:
        cleanup_gdi()
        return
    
    time.sleep(5)
    
    # Phase 1: RanTunnel
    stop_event = threading.Event()
    t1 = threading.Thread(target=ran_tunnel, args=(stop_event,))
    t1.start()
    sound1()
    time.sleep(30)
    stop_event.set()
    t1.join()
    user32.InvalidateRect(0, None, True)
    time.sleep(0.1)
    
    # Phase 2: CubeColorHalf
    stop_event.clear()
    t2 = threading.Thread(target=cube_color_half, args=(stop_event,))
    t2.start()
    sound2()
    time.sleep(30)
    stop_event.set()
    t2.join()
    user32.InvalidateRect(0, None, True)
    time.sleep(0.1)
    
    # Phase 3: WeirdInvert
    stop_event.clear()
    t3 = threading.Thread(target=weird_invert, args=(stop_event,))
    t3.start()
    sound3()
    time.sleep(30)
    stop_event.set()
    t3.join()
    user32.InvalidateRect(0, None, True)
    time.sleep(0.1)
    
    # Phase 4: Light
    stop_event.clear()
    t4 = threading.Thread(target=light, args=(stop_event,))
    t4.start()
    sound4()
    time.sleep(30)
    stop_event.set()
    t4.join()
    user32.InvalidateRect(0, None, True)
    time.sleep(0.1)
    
    # Phase 5: LightDif
    stop_event.clear()
    t5 = threading.Thread(target=light_dif, args=(stop_event,))
    t5.start()
    sound5()
    time.sleep(30)
    stop_event.set()
    t5.join()
    user32.InvalidateRect(0, None, True)
    time.sleep(0.1)
    
    # Phase 6: TextOut
    stop_event.clear()
    t6 = threading.Thread(target=text_out, args=(stop_event,))
    t6.start()
    # sound6 not defined in original
    time.sleep(30)
    stop_event.set()
    t6.join()
    user32.InvalidateRect(0, None, True)
    time.sleep(0.1)
    
    # Phase 7: MoveScreenInvert
    stop_event.clear()
    t7 = threading.Thread(target=move_screen_invert, args=(stop_event,))
    t7.start()
    sound7()
    time.sleep(30)
    stop_event.set()
    t7.join()
    user32.InvalidateRect(0, None, True)
    time.sleep(0.1)
    
    # Phase 8: TextOut2 + ColorsHalf
    stop_event.clear()
    t8 = threading.Thread(target=text_out2, args=(stop_event,))
    t8a = threading.Thread(target=colors_half, args=(stop_event,))
    t8.start()
    t8a.start()
    sound8()
    time.sleep(30)
    stop_event.set()
    t8.join()
    t8a.join()
    user32.InvalidateRect(0, None, True)
    time.sleep(0.1)
    
    # Phase 9: WeirdScreenMovement + CursorText + Icons
    stop_event.clear()
    t9 = threading.Thread(target=weird_screen_movement, args=(stop_event,))
    t9a = threading.Thread(target=cursor_text, args=(stop_event,))
    t9b = threading.Thread(target=icons, args=(stop_event,))
    t9.start()
    t9a.start()
    t9b.start()
    sound9()
    time.sleep(30)
    stop_event.set()
    t9.join()
    t9a.join()
    t9b.join()
    user32.InvalidateRect(0, None, True)
    time.sleep(0.1)
    
    # Phase 10: NegativeInvert + Redrawer
    stop_event.clear()
    t10 = threading.Thread(target=negative_invert, args=(stop_event,))
    t10a = threading.Thread(target=redrawer, args=(stop_event,))
    t10.start()
    t10a.start()
    # sound10 not defined in original
    time.sleep(30)
    stop_event.set()
    t10.join()
    t10a.join()
    user32.InvalidateRect(0, None, True)
    time.sleep(0.1)
    
    # Phase 11: sines
    stop_event.clear()
    t11 = threading.Thread(target=sines, args=(stop_event,))
    t11.start()
    sound11()
    time.sleep(30)
    stop_event.set()
    t11.join()
    user32.InvalidateRect(0, None, True)
    
    cleanup_gdi()
    print("easdrogen execution complete. System restored.")

if __name__ == "__main__":
    main()