import tkinter as tk
import random
import math

class HappyCatIcon:
    def __init__(self, parent):
        # Create a window for each cat
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.config(bg='black')
        self.window.attributes("-transparentcolor", "black")

        # The Happy Cat Emoji
        # You can use 😺, 😸, or 😻
        self.label = tk.Label(
            self.window, 
            text="😺", 
            font=("Segoe UI Emoji", 50), # Larger size
            fg="#FFCC00", # Golden Cat Color
            bg="black"
        )
        self.label.pack()

        # Screen dimensions
        self.sw = self.window.winfo_screenwidth()
        self.sh = self.window.winfo_screenheight()

        # Random starting position
        self.x = random.randint(0, self.sw - 100)
        self.y = random.randint(0, self.sh - 100)
        
        # Movement speed (Higher numbers = faster dancing)
        self.vel_x = random.uniform(5, 12) * random.choice([-1, 1])
        self.vel_y = random.uniform(5, 12) * random.choice([-1, 1])

        self.animate()

    def animate(self):
        # Move position
        self.x += self.vel_x
        self.y += self.vel_y

        # Bounce logic
        if self.x <= 0 or self.x >= self.sw - 80:
            self.vel_x *= -1
        if self.y <= 0 or self.y >= self.sh - 80:
            self.vel_y *= -1

        # Apply position with extra "jitter" to make it look like it's dancing
        jitter_x = random.randint(-4, 4)
        jitter_y = random.randint(-4, 4)
        
        try:
            self.window.geometry(f"+{int(self.x + jitter_x)}+{int(self.y + jitter_y)}")
            self.window.after(10, self.animate)
        except:
            pass # Handle window closing

class CatApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() # Hide the main controller window
        
        # Spawn 15 happy cats!
        self.cats = []
        for _ in range(15):
            self.cats.append(HappyCatIcon(self.root))

        # SAFETY: Press ESCAPE to close all cats immediately
        self.root.bind_all('<Escape>', lambda e: self.root.destroy())
        
        print("THE CATS ARE DANCING!")
        print("Press ESC to stop them.")
        
        self.root.mainloop()

if __name__ == "__main__":
    CatApp()