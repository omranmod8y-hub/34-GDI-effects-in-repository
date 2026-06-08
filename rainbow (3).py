import tkinter as tk
import colorsys
import math
import threading
import time
from tkinter import ttk
import sys

class RainbowDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌈 Rainbow GDL Desktop")
        self.root.geometry("400x600")
        self.root.configure(bg='#1a1a2e')
        
        # Desktop window settings
        self.desktop_window = None
        self.running = False
        self.animation_thread = None
        
        # Animation parameters
        self.hue = 0
        self.speed = 0.02
        self.brightness = 0.8
        self.wave_intensity = 0.5
        self.color_count = 30
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🌈 Rainbow GDL Desktop", 
                        font=("Arial", 20, "bold"), 
                        bg='#1a1a2e', fg='white')
        title.pack(pady=20)
        
        # Status
        self.status_label = tk.Label(self.root, text="● Not Active", 
                                     font=("Arial", 12),
                                     bg='#1a1a2e', fg='red')
        self.status_label.pack(pady=10)
        
        # Control buttons frame
        btn_frame = tk.Frame(self.root, bg='#1a1a2e')
        btn_frame.pack(pady=20)
        
        self.start_btn = tk.Button(btn_frame, text="▶ START", 
                                   command=self.start_desktop,
                                   font=("Arial", 14, "bold"),
                                   bg='#00ff88', fg='black',
                                   padx=30, pady=10)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(btn_frame, text="⏹ STOP", 
                                  command=self.stop_desktop,
                                  font=("Arial", 14, "bold"),
                                  bg='#ff4444', fg='white',
                                  padx=30, pady=10,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Settings frame
        settings_frame = tk.LabelFrame(self.root, text="Settings", 
                                       font=("Arial", 12, "bold"),
                                       bg='#1a1a2e', fg='white')
        settings_frame.pack(pady=20, padx=20, fill=tk.X)
        
        # Speed slider
        tk.Label(settings_frame, text="Animation Speed:", 
                bg='#1a1a2e', fg='white').pack(pady=5)
        self.speed_slider = tk.Scale(settings_frame, from_=0.005, to=0.05,
                                     orient=tk.HORIZONTAL, resolution=0.001,
                                     command=self.update_speed,
                                     bg='#1a1a2e', fg='white')
        self.speed_slider.set(0.02)
        self.speed_slider.pack(fill=tk.X, padx=20)
        
        # Brightness slider
        tk.Label(settings_frame, text="Brightness:", 
                bg='#1a1a2e', fg='white').pack(pady=5)
        self.brightness_slider = tk.Scale(settings_frame, from_=0.3, to=1.0,
                                         orient=tk.HORIZONTAL, resolution=0.01,
                                         command=self.update_brightness,
                                         bg='#1a1a2e', fg='white')
        self.brightness_slider.set(0.8)
        self.brightness_slider.pack(fill=tk.X, padx=20)
        
        # Wave intensity slider
        tk.Label(settings_frame, text="Wave Effect:", 
                bg='#1a1a2e', fg='white').pack(pady=5)
        self.wave_slider = tk.Scale(settings_frame, from_=0.0, to=1.0,
                                   orient=tk.HORIZONTAL, resolution=0.01,
                                   command=self.update_wave,
                                   bg='#1a1a2e', fg='white')
        self.wave_slider.set(0.5)
        self.wave_slider.pack(fill=tk.X, padx=20)
        
        # Color count selector
        tk.Label(settings_frame, text="Color Bands:", 
                bg='#1a1a2e', fg='white').pack(pady=5)
        self.color_var = tk.IntVar(value=30)
        color_spin = tk.Spinbox(settings_frame, from_=10, to=100,
                                textvariable=self.color_var,
                                command=self.update_colors,
                                bg='#1a1a2e', fg='white')
        color_spin.pack(pady=5)
        
        # Info label
        info_text = """
        🌈 Rainbow GDL Desktop Effect
        
        • Creates a dynamic rainbow overlay on your desktop
        • Gradual Dynamic Lighting (GDL) with smooth transitions
        • Click on the rainbow window to interact with desktop
        • Press ESC to exit the effect
        • Adjust settings in real-time
        """
        
        info_label = tk.Label(self.root, text=info_text, 
                             font=("Arial", 9),
                             bg='#1a1a2e', fg='#888888',
                             justify=tk.LEFT)
        info_label.pack(pady=20, padx=20)
        
    def update_speed(self, val):
        self.speed = float(val)
        
    def update_brightness(self, val):
        self.brightness = float(val)
        
    def update_wave(self, val):
        self.wave_intensity = float(val)
        
    def update_colors(self):
        self.color_count = self.color_var.get()
        if self.desktop_window and self.running:
            self.restart_desktop()
    
    def start_desktop(self):
        if not self.running:
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="● Active - Rainbow on Desktop", fg='#00ff88')
            
            # Start desktop effect in separate thread
            self.animation_thread = threading.Thread(target=self.create_desktop_effect, daemon=True)
            self.animation_thread.start()
    
    def stop_desktop(self):
        self.running = False
        if self.desktop_window:
            try:
                self.desktop_window.destroy()
            except:
                pass
            self.desktop_window = None
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Stopped", fg='red')
    
    def restart_desktop(self):
        if self.running:
            self.stop_desktop()
            time.sleep(0.5)
            self.start_desktop()
    
    def create_desktop_effect(self):
        # Create a new window for the desktop effect
        desktop = tk.Tk()
        self.desktop_window = desktop
        
        # Make it fullscreen and always on top
        desktop.attributes('-fullscreen', True)
        desktop.attributes('-topmost', True)
        desktop.configure(bg='black')
        
        # Make it click-through (optional - uncomment to allow clicking through)
        # desktop.attributes('-transparentcolor', 'black')
        
        # Bind escape key to close
        desktop.bind('<Escape>', lambda e: self.stop_desktop())
        
        # Create canvas
        canvas = tk.Canvas(desktop, highlightthickness=0, bg='black')
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Get screen dimensions
        width = desktop.winfo_screenwidth()
        height = desktop.winfo_screenheight()
        
        # Create rectangles for rainbow effect
        rect_width = width // self.color_count
        rectangles = []
        
        for i in range(self.color_count + 1):
            x1 = i * rect_width
            x2 = x1 + rect_width
            rect = canvas.create_rectangle(x1, 0, x2, height, outline='', fill='black')
            rectangles.append(rect)
        
        # Animation loop
        wave_offset = 0
        pulse = 0
        pulse_direction = 1
        
        while self.running:
            try:
                # Update animation parameters
                self.hue = (self.hue + self.speed) % 1.0
                wave_offset += 0.05
                pulse += 0.01 * pulse_direction
                
                if pulse >= 1.0:
                    pulse = 1.0
                    pulse_direction = -1
                elif pulse <= 0.0:
                    pulse = 0.0
                    pulse_direction = 1
                
                # Update each rectangle with dynamic colors
                for i, rect in enumerate(rectangles):
                    # Calculate hue with wave effect
                    hue = (self.hue + (i / len(rectangles)) + 
                          math.sin(wave_offset + i * 0.1) * self.wave_intensity * 0.1)
                    hue = hue % 1.0
                    
                    # Dynamic saturation and value for GDL effect
                    saturation = 0.8 + math.sin(self.hue * 5 + i * 0.05) * 0.2
                    value = self.brightness + math.sin(self.hue * 3 + pulse * 10) * 0.1
                    value = min(1.0, max(0.3, value))
                    
                    # Convert to RGB
                    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
                    color = '#{:02x}{:02x}{:02x}'.format(
                        int(rgb[0] * 255),
                        int(rgb[1] * 255),
                        int(rgb[2] * 255)
                    )
                    
                    canvas.itemconfig(rect, fill=color)
                
                desktop.update()
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"Animation error: {e}")
                break
        
        try:
            desktop.destroy()
        except:
            pass
    
    def on_closing(self):
        self.stop_desktop()
        self.root.destroy()

# Alternative: Direct Desktop Wallpaper Setter (Windows)
class RainbowWallpaperSetter:
    @staticmethod
    def set_rainbow_wallpaper():
        """Set actual desktop wallpaper to rainbow gradient"""
        try:
            from PIL import Image, ImageDraw
            import ctypes
            import os
            
            # Get screen resolution
            user32 = ctypes.windll.user32
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
            
            # Create rainbow image
            img = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(img)
            
            for x in range(width):
                hue = x / width
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 0.9)
                color = tuple(int(c * 255) for c in rgb)
                draw.line([(x, 0), (x, height)], fill=color)
            
            # Save and set as wallpaper
            temp_path = os.path.join(os.environ['TEMP'], 'rainbow_gdl_wallpaper.bmp')
            img.save(temp_path)
            
            # Set wallpaper
            SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, temp_path, 3)
            
            return True
        except Exception as e:
            print(f"Error setting wallpaper: {e}")
            return False

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = RainbowDesktopApp(root)
    
    # Add menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Set as Wallpaper", 
                         command=lambda: RainbowWallpaperSetter.set_rainbow_wallpaper())
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.on_closing)
    
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Controls", 
                         command=lambda: print("ESC to exit effect, Click to interact"))
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()