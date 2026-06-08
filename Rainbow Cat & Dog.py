import tkinter as tk
import random
import colorsys

class RainbowPet:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.config(bg='black')
        self.window.attributes("-transparentcolor", "black")

        # Randomly choose between a Cat and a Dog
        self.emoji = random.choice(["😺", "🐶", "😸", "🐕", "😹", "🐩"])
        
        # Unique starting hue so they aren't all the same color at once
        self.hue = random.random() 

        self.label = tk.Label(
            self.window, 
            text=self.emoji, 
            font=("Segoe UI Emoji", 60), 
            fg="white", 
            bg="black"
        )
        self.label.pack()

        # Screen dimensions
        self.sw = self.window.winfo_screenwidth()
        self.sh = self.window.winfo_screenheight()

        # Movement physics
        self.x = random.randint(50, self.sw - 100)
        self.y = random.randint(50, self.sh - 100)
        
        # Random speeds for a "chaotic" look
        self.vel_x = random.uniform(7, 14) * random.choice([-1, 1])
        self.vel_y = random.uniform(7, 14) * random.choice([-1, 1])

        self.animate()

    def update_rainbow_color(self):
        # Shift the hue slightly
        self.hue += 0.015
        if self.hue > 1.0: self.hue = 0
            
        # Convert HSV to RGB
        rgb = colorsys.hsv_to_rgb(self.hue, 1, 1)
        color_hex = '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        self.label.config(fg=color_hex)

    def animate(self):
        self.update_rainbow_color()

        # Update Position
        self.x += self.vel_x
        self.y += self.vel_y

        # Bounce Logic
        if self.x <= 0 or self.x >= self.sw - 100:
            self.vel_x *= -1
        if self.y <= 0 or self.y >= self.sh - 100:
            self.vel_y *= -1

        # The "Dancing" Jitter Shaking
        jitter_x = random.randint(-6, 6)
        jitter_y = random.randint(-6, 6)

        try:
            self.window.geometry(f"+{int(self.x + jitter_x)}+{int(self.y + jitter_y)}")
            self.window.after(10, self.animate)
        except:
            pass

class RainbowApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() # Hide the invisible main controller
        
        print("RAINBOW CATS & DOGS ACTIVE!")
        print("Spawning 10 pets...")
        print("PRESS ESCAPE TO EXIT")
        
        # Create 10 mixed pets
        for _ in range(10):
            RainbowPet(self.root)

        # Safety: Close everything on Escape press
        self.root.bind_all('<Escape>', lambda e: self.root.destroy())
        
        self.root.mainloop()

if __name__ == "__main__":
    RainbowApp()