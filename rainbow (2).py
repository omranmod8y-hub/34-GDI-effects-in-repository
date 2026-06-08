import tkinter as tk
import colorsys
import math
import random

class Particle:
    def __init__(self, x, y, color_hue, size):
        self.x = x
        self.y = y
        self.color_hue = color_hue
        self.size = size
        self.life = 1.0
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 0.01
        self.size *= 0.99
        return self.life > 0

class RainbowGDLParticleSystem:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        
        self.canvas = tk.Canvas(root, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        
        self.particles = []
        self.hue_offset = 0
        self.time = 0
        
        # Create background gradient rectangles
        self.bg_rects = []
        rect_width = 30
        num_rects = self.width // rect_width + 2
        
        for i in range(num_rects):
            x1 = i * rect_width
            x2 = x1 + rect_width
            rect = self.canvas.create_rectangle(
                x1, 0, x2, self.height,
                outline='', fill='black'
            )
            self.bg_rects.append(rect)
        
        self.animate()
        
        # Controls
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.bind('<space>', lambda e: self.add_particle_burst())
        self.root.bind('<Button-1>', lambda e: self.add_particle_burst_at(e.x, e.y))
    
    def add_particle_burst(self, x=None, y=None):
        """Create burst of particles"""
        if x is None:
            x = random.randint(0, self.width)
        if y is None:
            y = random.randint(0, self.height)
        
        for _ in range(30):
            hue = (self.hue_offset + random.random()) % 1.0
            size = random.randint(3, 10)
            particle = Particle(x, y, hue, size)
            self.particles.append(particle)
    
    def add_particle_burst_at(self, x, y):
        self.add_particle_burst(x, y)
    
    def animate(self):
        # Update time and hue
        self.time += 0.02
        self.hue_offset = (self.hue_offset + 0.005) % 1.0
        
        # Update background gradient (looping GDL effect)
        for i, rect in enumerate(self.bg_rects):
            hue = (self.hue_offset + (i / len(self.bg_rects)) + 
                   math.sin(self.time * 0.5 + i * 0.1) * 0.1)
            hue = hue % 1.0
            
            # Dynamic brightness for GDL
            brightness = 0.5 + math.sin(self.time * 2 + i * 0.05) * 0.3
            rgb = colorsys.hsv_to_rgb(hue, 0.8, brightness)
            color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            self.canvas.itemconfig(rect, fill=color)
        
        # Update and draw particles
        for particle in self.particles[:]:
            # Delete old particle if exists
            if hasattr(particle, 'id'):
                self.canvas.delete(particle.id)
            
            # Update particle
            if not particle.update():
                self.particles.remove(particle)
                continue
            
            # Draw particle with dynamic color
            hue = (particle.color_hue + self.time * 0.1) % 1.0
            saturation = particle.life
            value = particle.life * 0.8 + 0.2
            
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            
            particle.id = self.canvas.create_oval(
                particle.x - particle.size,
                particle.y - particle.size,
                particle.x + particle.size,
                particle.y + particle.size,
                fill=color,
                outline=''
            )
        
        # Add random particles periodically
        if random.random() < 0.05:
            self.add_particle_burst()
        
        # Continue loop
        self.root.after(30, self.animate)

# Run particle system
if __name__ == "__main__":
    root = tk.Tk()
    app = RainbowGDLParticleSystem(root)
    root.mainloop()