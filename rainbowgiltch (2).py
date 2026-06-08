import tkinter as tk
import colorsys

class RainbowBar:
    def __init__(self, root):
        self.root = root
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Create window at bottom of screen
        bar_height = 100
        self.root.geometry(f"{screen_width}x{bar_height}+0+{screen_height - bar_height}")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)  # Remove window decorations
        
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.hue = 0
        self.animate()
        
        # Double-click to exit
        self.canvas.bind('<Double-Button-1>', lambda e: self.root.destroy())
        
    def animate(self):
        self.hue = (self.hue + 0.01) % 1.0
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        self.canvas.delete('all')
        
        # Create rainbow gradient
        for x in range(width):
            hue = (self.hue + (x / width)) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 0.8)
            color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            self.canvas.create_line(x, 0, x, height, fill=color)
        
        self.root.after(20, self.animate)

# Run rainbow bar
root = tk.Tk()
app = RainbowBar(root)
root.mainloop()