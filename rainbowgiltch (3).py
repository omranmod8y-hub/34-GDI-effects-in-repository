import tkinter as tk
import colorsys

class RainbowDesktop:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        
        # Make it transparent-like (optional)
        self.root.attributes('-alpha', 0.7)
        
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.hue = 0
        self.rectangles = []
        
        # Create rectangles for rainbow effect
        self.num_rectangles = 20
        self.setup_rainbow()
        
        # Start animation
        self.animate()
        
        # Click to exit
        self.canvas.bind('<Button-1>', lambda e: self.root.destroy())
        
    def setup_rainbow(self):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        rect_width = width // self.num_rectangles
        
        for i in range(self.num_rectangles):
            x1 = i * rect_width
            x2 = (i + 1) * rect_width
            rect = self.canvas.create_rectangle(
                x1, 0, x2, height,
                outline='', fill='black'
            )
            self.rectangles.append(rect)
    
    def animate(self):
        self.hue = (self.hue + 0.005) % 1.0
        
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        
        for i, rect in enumerate(self.rectangles):
            # Calculate hue for each rectangle
            hue = (self.hue + (i / len(self.rectangles))) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            self.canvas.itemconfig(rect, fill=color)
        
        self.root.after(50, self.animate)

# Run rainbow desktop effect
if __name__ == "__main__":
    root = tk.Tk()
    app = RainbowDesktop(root)
    root.mainloop()