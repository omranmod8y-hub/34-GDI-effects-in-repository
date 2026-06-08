import tkinter as tk
import random
import colorsys # Used for smooth rainbow color transitions

class RainbowCat:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.config(bg='black')
        self.window.attributes("-transparentcolor", "black")

        # Hue value for the rainbow (0.0 to 1.0)
        self.hue = random.random() 

        self.label = tk.Label(
            self.window, 
            text="😺", 
            font=("Segoe UI Emoji", 60), 
            fg="white", # Initial color
            bg="black"
        )
        self.label.pack()

        # Screen dimensions
        self.sw = self.window.winfo_screenwidth()
        self.sh = self.window.winfo_screenheight()

        # Movement physics
        self.x = random.randint(50, self.sw - 100)
        self.y = random.randint(50, self.sh - 100)
        self.vel_x = random.uniform(6, 12) * random.choice([-1, 1])
        self.vel_y = random.uniform(6, 12) * random.choice([-1, 1])

        self.animate()

    def update_color(self):
        # Cycle the hue
        self.hue += 0.02
        if self.hue > 1.0:
            self.hue = 0
            
        # Convert HSV color to RGB, then to Hex for Tkinter
        rgb = colorsys.hsv_to_rgb(self.hue, 1, 1)
        color_hex = '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        self.label.config(fg=color_hex)

    def animate(self):
        # Update Color
        self.update_color()

        # Update Position
        self.x += self.vel_x
        self.y += self.vel_y

        # Bounce
        if self.x <= 0 or self.x >= self.sw - 80:
            self.vel_x *= -1
        if self.y <= 0 or self.y >= self.sh - 80:
            self.vel_y *= -1

        # Dance Jitter
        jitter_x = random.randint(-4, 4)
        jitter_y = random.randint(-4, 4)

        try:
            self.window.geometry(f"+{int(self.x + jitter_x)}+{int(self.y + jitter_y)}")
            self.window.after(10, self.animate)
        except:
            pass

class RainbowApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Create 10 Rainbow Cats
        for _ in range(10):
            RainbowCat(self.root)

        # ESC to Close
        self.root.bind_all('<Escape>', lambda e: self.root.destroy())
        
        print("RAINBOW CATS ACTIVE")
        print("Press ESC to exit.")
        self.root.mainloop()

if __name__ == "__main__":
    RainbowApp()