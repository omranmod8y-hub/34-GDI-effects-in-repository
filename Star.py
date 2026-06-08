import tkinter as tk
import random
import math
import time

class StarfieldDesktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Desktop Starfield - Always on Top")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)  # Always on top
        self.root.configure(bg='black')
        
        # Make window transparent to clicks (so you can click through to desktop)
        try:
            # Windows: allows clicking through the window
            self.root.attributes('-transparentcolor', 'black')
            self.root.attributes('-disabled', True)
        except:
            pass
            
        # Get screen dimensions
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        
        # Create canvas for drawing
        self.canvas = tk.Canvas(
            self.root, 
            width=self.width, 
            height=self.height, 
            bg='black', 
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Star properties
        self.stars = []
        self.num_stars = 400
        self.running = True
        
        # Initialize stars
        self.create_stars()
        
        # Bind exit key
        self.root.bind('<Escape>', lambda e: self.exit_app())
        self.root.bind('<F12>', lambda e: self.exit_app())  # F12 also exits
        
        # Start animation
        self.animate()
        
        # Keep on top and focused
        self.root.focus_force()
        
    def create_stars(self):
        """Create random stars with different properties"""
        for _ in range(self.num_stars):
            star = {
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.choice([1, 2, 2, 3]),  # More smaller stars
                'brightness': random.uniform(0.2, 1.0),
                'speed': random.uniform(0.008, 0.05),
                'phase': random.uniform(0, 2 * math.pi),
                'twinkle_rate': random.uniform(0.5, 2.0),
                'id': None
            }
            self.stars.append(star)
    
    def get_star_color(self, brightness):
        """Convert brightness to grayscale hex color"""
        value = int(brightness * 255)
        return f'#{value:02x}{value:02x}{value:02x}'
    
    def draw_stars(self):
        """Draw all stars on canvas"""
        current_time = time.time()
        
        for star in self.stars:
            # Calculate twinkling effect
            twinkle = math.sin(current_time * star['speed'] * 15 * star['twinkle_rate'] + star['phase'])
            brightness = star['brightness'] + (twinkle * 0.25)
            brightness = max(0.15, min(1.0, brightness))
            
            color = self.get_star_color(brightness)
            
            # Draw or update star
            if star['id']:
                self.canvas.coords(star['id'], 
                                  star['x'] - star['size'], 
                                  star['y'] - star['size'],
                                  star['x'] + star['size'], 
                                  star['y'] + star['size'])
                self.canvas.itemconfig(star['id'], fill=color, outline=color)
            else:
                star['id'] = self.canvas.create_oval(
                    star['x'] - star['size'],
                    star['y'] - star['size'],
                    star['x'] + star['size'],
                    star['y'] + star['size'],
                    fill=color,
                    outline=color
                )
    
    def animate(self):
        """Animation loop"""
        if self.running:
            self.draw_stars()
            self.root.after(50, self.animate)  # 20 FPS
    
    def exit_app(self):
        """Exit the application"""
        self.running = False
        self.root.destroy()
    
    def run(self):
        """Start the starfield"""
        self.root.mainloop()

if __name__ == "__main__":
    app = StarfieldDesktop()
    app.run()