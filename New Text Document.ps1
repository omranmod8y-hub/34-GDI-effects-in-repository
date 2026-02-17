Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Threading;

public class MultiWash {
    [DllImport("user32.dll")] public static extern IntPtr GetDC(IntPtr hWnd);
    [DllImport("gdi32.dll")] public static extern bool PlgBlt(IntPtr hdcDest, POINT[] lpPoint, IntPtr hdcSrc, int xSrc, int ySrc, int wSrc, int hSrc, IntPtr hbmMask, int xMask, int yMask);
    [DllImport("user32.dll")] public static extern bool ReleaseDC(IntPtr hWnd, IntPtr hDC);

    [StructLayout(LayoutKind.Sequential)]
    public struct POINT {
        public int x;
        public int y;
    }

    public static void GridWash() {
        IntPtr hdc = GetDC(IntPtr.Zero);
        int w = 1920, h = 1080;
        int cols = 3, rows = 3;
        int cellW = w / cols;
        int cellH = h / rows;
        Random rand = new Random();

        for (int t = 0; t < 150; t++) {
            for (int i = 0; i < cols; i++) {
                for (int j = 0; j < rows; j++) {
                    int cx = i * cellW + cellW / 2;
                    int cy = j * cellH + cellH / 2;
                    int r = rand.Next(100, 300);
                    double angle = (t + i + j) * 0.2;

                    POINT[] pts = new POINT[3];
                    pts[0].x = cx + (int)(r * Math.Cos(angle));
                    pts[0].y = cy + (int)(r * Math.Sin(angle));
                    pts[1].x = cx + (int)(r * Math.Cos(angle + 2 * Math.PI / 3));
                    pts[1].y = cy + (int)(r * Math.Sin(angle + 2 * Math.PI / 3));
                    pts[2].x = cx + (int)(r * Math.Cos(angle + 4 * Math.PI / 3));
                    pts[2].y = cy + (int)(r * Math.Sin(angle + 4 * Math.PI / 3));

                    PlgBlt(hdc, pts, hdc, i * cellW, j * cellH, cellW, cellH, IntPtr.Zero, 0, 0);
                }
            }
            Thread.Sleep(30);
        }

        ReleaseDC(IntPtr.Zero, hdc);
    }
}
"@ -Language CSharp

[MultiWash]::GridWash()