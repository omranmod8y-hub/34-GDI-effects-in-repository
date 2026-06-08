import win32api
import win32con
import win32gui
import math
import time

def sines():
    desktop = win32gui.GetDesktopWindow()
    hdc = win32gui.GetWindowDC(desktop)
    sh = win32api.GetSystemMetrics(1)
    sw = win32api.GetSystemMetrics(0)
    angle = 0
    while True:
        hdc = win32gui.GetWindowDC(desktop)
        for i in range(int(sw + sh)):
            a = int(math.sin(angle) * 10)
            win32gui.BitBlt(hdc, 1, i, sw, 1, hdc, a, i, win32con.SRCCOPY)
            angle += math.pi / 40
        win32gui.ReleaseDC(desktop, hdc)
        #time.sleep(0.05)

if __name__ == '__main__':
    sines()

# by OverlordV1per github page: https://github.com/OverlordV1per
