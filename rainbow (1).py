import tkinter as tk
import colorsys
import math
import random

class RainbowGDLDesktop:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        
        # Allow clicking through (optional - makes it non-interactive)
        # self.root.attributes('-transparentcolor', 'black')
        
        self.canvas = tk.Canvas(root, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Animation parameters
        self.angle = 0
        self.wave_offset = 0
        self.pulse = 0
        self.direction = 1
        
        # Get screen dimensions
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        
        # Create gradient layers
        self.layers = []
        self.num_layers = 5
        
        self.setup_layers()
        self.animate()
        
        # Press ESC to exit
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.bind('<Button-1>', lambda e: self.root.destroy())  # Click to exit
        
    def setup_layers(self):
        """Create multiple layers for dynamic rainbow effect"""
        for i in range(self.num_layers):
            layer = {
                'rects': [],
                'speed': 0.5 + (i * 0.3),
                'intensity': 0.5 + (i * 0.1),
                'offset': i * 50
            }
            
            # Create rectangles for this layer
            rect_width = 20
            num_rects = self.width // rect_width + 2
            
            for j in range(num_rects):
                x1 = j * rect_width
                x2 = x1 + rect_width
                rect = self.canvas.create_rectangle(
                    x1, 0, x2, self.height,
                    outline='', fill='black'
                )
                layer['rects'].append(rect)
            
            self.layers.append(layer)
    
    def get_rainbow_color(self, hue, saturation=1.0, value=1.0):
        """Convert HSV to hex color"""
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
    
    def animate(self):
        # Update animation parameters for looping
        self.angle += 0.02
        self.wave_offset += 0.03
        self.pulse += 0.02 * self.direction
        
        # Reverse pulse direction at boundaries
        if self.pulse >= 1.0:
            self.pulse = 1.0
            self.direction = -1
        elif self.pulse <= 0.0:
            self.pulse = 0.0
            self.direction = 1
        
        # Update each layer
        for layer in self.layers:
            base_hue = (self.angle * layer['speed']) % 1.0
            
            for i, rect in enumerate(layer['rects']):
                # Create dynamic hue with wave pattern
                hue = (base_hue + 
                      (i * 0.02) +  # Horizontal gradient
                      (math.sin(self.wave_offset + i * 0.05) * 0.1) +  # Wave effect
                      (self.pulse * 0.2))  # Pulse effect
                hue = hue % 1.0
                
                # Dynamic saturation and value for GDL effect
                saturation = 0.7 + (math.sin(self.angle * 2 + i * 0.03) * 0.3)
                value = 0.8 + (math.sin(self.angle * 3 + self.pulse * 5) * 0.2)
                
                color = self.get_rainbow_color(hue, saturation, value)
                self.canvas.itemconfig(rect, fill=color)
        
        # Continue looping
        self.root.after(30, self.animate)

# Run the effect
if __name__ == "__main__":
    root = tk.Tk()
    app = RainbowGDLDesktop(root)
    root.mainloop()