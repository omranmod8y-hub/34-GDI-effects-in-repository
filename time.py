import tkinter as tk
from tkinter import ttk, colorchooser, font
from datetime import datetime
import random

class ClockModMenu:
    def __init__(self):
        self.root = tk.Tk()
        
        # Make fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # Mod menu state
        self.mod_menu_visible = False
        self.mod_settings = {
            'time_color': '#00ff00',
            'date_color': '#00ff00',
            'bg_color': 'black',
            'font_style': 'Arial',
            'time_size': 120,
            'date_size': 40,
            'show_seconds': True,
            'show_date': True,
            'show_weekday': True,
            'time_format': 24,  # 24 or 12 hour
            'animation': 'none',  # none, rainbow, pulse, matrix
            'opacity': 1.0,
            'border_style': 'none'  # none, glow, box
        }
        
        self.animation_hue = 0
        self.pulse_value = 0
        self.pulse_direction = 1
        
        # Bind keys
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('f', self.toggle_fullscreen)
        self.root.bind('m', self.toggle_mod_menu)  # Press 'm' for mod menu!
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(expand=True, fill='both')
        
        # Clock display frame
        self.clock_frame = tk.Frame(self.main_frame, bg='black')
        self.clock_frame.pack(expand=True)
        
        # Time label
        self.time_label = tk.Label(
            self.clock_frame,
            font=(self.mod_settings['font_style'], self.mod_settings['time_size'], 'bold'),
            bg=self.mod_settings['bg_color'],
            fg=self.mod_settings['time_color']
        )
        self.time_label.pack()
        
        # Date label
        self.date_label = tk.Label(
            self.clock_frame,
            font=(self.mod_settings['font_style'], self.mod_settings['date_size']),
            bg=self.mod_settings['bg_color'],
            fg=self.mod_settings['date_color']
        )
        
        # Weekday label
        self.weekday_label = tk.Label(
            self.clock_frame,
            font=(self.mod_settings['font_style'], self.mod_settings['date_size'] - 10),
            bg=self.mod_settings['bg_color'],
            fg=self.mod_settings['date_color']
        )
        
        # Info label
        self.info_label = tk.Label(
            self.main_frame,
            font=('Arial', 12),
            bg='black',
            fg='gray',
            text="Press 'M' for Mod Menu | 'F' Fullscreen | 'ESC' Exit"
        )
        self.info_label.pack(side='bottom', pady=10)
        
        # Create mod menu
        self.create_mod_menu()
        
        # Start clock and animations
        self.update_clock()
        self.update_animations()
        
        self.root.mainloop()
    
    def create_mod_menu(self):
        """Create the mod menu panel"""
        self.mod_panel = tk.Toplevel(self.root)
        self.mod_panel.title("⚡ CLOCK MOD MENU ⚡")
        self.mod_panel.geometry("400x700")
        self.mod_panel.configure(bg='#1a1a2e')
        self.mod_panel.protocol("WM_DELETE_WINDOW", self.hide_mod_menu)
        self.mod_panel.withdraw()  # Hide initially
        
        # Make it stay on top
        self.mod_panel.attributes('-topmost', True)
        
        # Title
        title = tk.Label(self.mod_panel, text="═══ MOD MENU ═══", 
                        font=('Arial', 18, 'bold'), bg='#1a1a2e', fg='#ff6b6b')
        title.pack(pady=15)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.mod_panel)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Colors
        colors_tab = tk.Frame(notebook, bg='#1a1a2e')
        notebook.add(colors_tab, text="🎨 Colors")
        self.setup_colors_tab(colors_tab)
        
        # Tab 2: Fonts
        fonts_tab = tk.Frame(notebook, bg='#1a1a2e')
        notebook.add(fonts_tab, text="📝 Fonts")
        self.setup_fonts_tab(fonts_tab)
        
        # Tab 3: Display
        display_tab = tk.Frame(notebook, bg='#1a1a2e')
        notebook.add(display_tab, text="🖥️ Display")
        self.setup_display_tab(display_tab)
        
        # Tab 4: Effects
        effects_tab = tk.Frame(notebook, bg='#1a1a2e')
        notebook.add(effects_tab, text="✨ Effects")
        self.setup_effects_tab(effects_tab)
        
        # Tab 5: Presets
        presets_tab = tk.Frame(notebook, bg='#1a1a2e')
        notebook.add(presets_tab, text="🎯 Presets")
        self.setup_presets_tab(presets_tab)
        
        # Close button
        close_btn = tk.Button(self.mod_panel, text="Close Menu (M)", command=self.toggle_mod_menu,
                            bg='#ff6b6b', fg='white', font=('Arial', 12, 'bold'))
        close_btn.pack(pady=10)
    
    def setup_colors_tab(self, parent):
        """Setup colors customization tab"""
        # Time color
        tk.Label(parent, text="Time Color:", bg='#1a1a2e', fg='white', font=('Arial', 11)).pack(pady=5)
        time_color_btn = tk.Button(parent, text="Choose Time Color", 
                                  command=lambda: self.choose_color('time_color'),
                                  bg='#4a4a6a', fg='white')
        time_color_btn.pack(pady=5)
        
        # Date color
        tk.Label(parent, text="Date Color:", bg='#1a1a2e', fg='white', font=('Arial', 11)).pack(pady=5)
        date_color_btn = tk.Button(parent, text="Choose Date Color",
                                  command=lambda: self.choose_color('date_color'),
                                  bg='#4a4a6a', fg='white')
        date_color_btn.pack(pady=5)
        
        # Background color
        tk.Label(parent, text="Background Color:", bg='#1a1a2e', fg='white', font=('Arial', 11)).pack(pady=5)
        bg_color_btn = tk.Button(parent, text="Choose BG Color",
                                command=lambda: self.choose_color('bg_color'),
                                bg='#4a4a6a', fg='white')
        bg_color_btn.pack(pady=5)
        
        # Random color button
        def random_colors():
            self.mod_settings['time_color'] = f'#{random.randint(0, 0xFFFFFF):06x}'
            self.mod_settings['date_color'] = f'#{random.randint(0, 0xFFFFFF):06x}'
            self.apply_settings()
        
        random_btn = tk.Button(parent, text="🎲 Random Colors", command=random_colors,
                              bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'))
        random_btn.pack(pady=20)
    
    def setup_fonts_tab(self, parent):
        """Setup fonts customization tab"""
        # Font style
        tk.Label(parent, text="Font Style:", bg='#1a1a2e', fg='white', font=('Arial', 11)).pack(pady=5)
        fonts = ['Arial', 'Helvetica', 'Times', 'Courier', 'Verdana', 'Impact', 'Comic Sans MS']
        font_combo = ttk.Combobox(parent, values=fonts, state='readonly')
        font_combo.set(self.mod_settings['font_style'])
        font_combo.bind('<<ComboboxSelected>>', lambda e: self.update_setting('font_style', font_combo.get()))
        font_combo.pack(pady=5)
        
        # Time size
        tk.Label(parent, text="Time Size:", bg='#1a1a2e', fg='white', font=('Arial', 11)).pack(pady=5)
        time_size_slider = tk.Scale(parent, from_=40, to=200, orient='horizontal',
                                   command=lambda v: self.update_setting('time_size', int(v)))
        time_size_slider.set(self.mod_settings['time_size'])
        time_size_slider.pack(pady=5, padx=20, fill='x')
        
        # Date size
        tk.Label(parent, text="Date Size:", bg='#1a1a2e', fg='white', font=('Arial', 11)).pack(pady=5)
        date_size_slider = tk.Scale(parent, from_=20, to=80, orient='horizontal',
                                   command=lambda v: self.update_setting('date_size', int(v)))
        date_size_slider.set(self.mod_settings['date_size'])
        date_size_slider.pack(pady=5, padx=20, fill='x')
    
    def setup_display_tab(self, parent):
        """Setup display options tab"""
        # Show seconds
        seconds_var = tk.BooleanVar(value=self.mod_settings['show_seconds'])
        seconds_cb = tk.Checkbutton(parent, text="Show Seconds", variable=seconds_var,
                                   command=lambda: self.update_setting('show_seconds', seconds_var.get()),
                                   bg='#1a1a2e', fg='white', selectcolor='#1a1a2e')
        seconds_cb.pack(pady=5)
        
        # Show date
        date_var = tk.BooleanVar(value=self.mod_settings['show_date'])
        date_cb = tk.Checkbutton(parent, text="Show Date", variable=date_var,
                                command=lambda: self.update_setting('show_date', date_var.get()),
                                bg='#1a1a2e', fg='white', selectcolor='#1a1a2e')
        date_cb.pack(pady=5)
        
        # Show weekday
        weekday_var = tk.BooleanVar(value=self.mod_settings['show_weekday'])
        weekday_cb = tk.Checkbutton(parent, text="Show Weekday", variable=weekday_var,
                                   command=lambda: self.update_setting('show_weekday', weekday_var.get()),
                                   bg='#1a1a2e', fg='white', selectcolor='#1a1a2e')
        weekday_cb.pack(pady=5)
        
        # Time format
        tk.Label(parent, text="Time Format:", bg='#1a1a2e', fg='white', font=('Arial', 11)).pack(pady=5)
        format_frame = tk.Frame(parent, bg='#1a1a2e')
        format_frame.pack()
        
        def set_24h():
            self.update_setting('time_format', 24)
            format_24h_btn.config(relief='sunken')
            format_12h_btn.config(relief='raised')
        
        def set_12h():
            self.update_setting('time_format', 12)
            format_12h_btn.config(relief='sunken')
            format_24h_btn.config(relief='raised')
        
        format_24h_btn = tk.Button(format_frame, text="24-Hour", command=set_24h,
                                  bg='#4a4a6a', fg='white', width=10)
        format_24h_btn.pack(side='left', padx=5)
        
        format_12h_btn = tk.Button(format_frame, text="12-Hour", command=set_12h,
                                  bg='#4a4a6a', fg='white', width=10)
        format_12h_btn.pack(side='left', padx=5)
        
        if self.mod_settings['time_format'] == 24:
            format_24h_btn.config(relief='sunken')
        else:
            format_12h_btn.config(relief='sunken')
        
        # Opacity
        tk.Label(parent, text="Window Opacity:", bg='#1a1a2e', fg='white', font=('Arial', 11)).pack(pady=5)
        opacity_slider = tk.Scale(parent, from_=0.3, to=1.0, orient='horizontal', resolution=0.1,
                                 command=lambda v: self.update_setting('opacity', float(v)))
        opacity_slider.set(self.mod_settings['opacity'])
        opacity_slider.pack(pady=5, padx=20, fill='x')
    
    def setup_effects_tab(self, parent):
        """Setup effects tab"""
        tk.Label(parent, text="Animation Effect:", bg='#1a1a2e', fg='white', font=('Arial', 11)).pack(pady=5)
        
        effects = ['none', 'rainbow', 'pulse', 'matrix']
        effect_var = tk.StringVar(value=self.mod_settings['animation'])
        
        for effect in effects:
            rb = tk.Radiobutton(parent, text=effect.capitalize(), variable=effect_var, value=effect,
                               command=lambda e=effect: self.update_setting('animation', e),
                               bg='#1a1a2e', fg='white', selectcolor='#1a1a2e')
            rb.pack(pady=2)
        
        # Border effect
        tk.Label(parent, text="Border Style:", bg='#1a1a2e', fg='white', font=('Arial', 11)).pack(pady=10)
        borders = ['none', 'glow', 'box']
        border_var = tk.StringVar(value=self.mod_settings['border_style'])
        
        for border in borders:
            rb = tk.Radiobutton(parent, text=border.capitalize(), variable=border_var, value=border,
                               command=lambda b=border: self.update_setting('border_style', b),
                               bg='#1a1a2e', fg='white', selectcolor='#1a1a2e')
            rb.pack(pady=2)
    
    def setup_presets_tab(self, parent):
        """Setup presets tab"""
        presets = {
            "Cyberpunk": {'time_color': '#ff00ff', 'date_color': '#00ffff', 'bg_color': '#000000',
                         'font_style': 'Courier', 'animation': 'rainbow'},
            "Christmas": {'time_color': '#ff0000', 'date_color': '#00ff00', 'bg_color': '#0a0a0a',
                         'font_style': 'Arial', 'animation': 'pulse'},
            "Ocean": {'time_color': '#00bfff', 'date_color': '#87ceeb', 'bg_color': '#001a33',
                     'font_style': 'Verdana', 'animation': 'none'},
            "Sunset": {'time_color': '#ff6347', 'date_color': '#ffd700', 'bg_color': '#4a0e2e',
                      'font_style': 'Impact', 'animation': 'pulse'},
            "Matrix": {'time_color': '#00ff00', 'date_color': '#00ff00', 'bg_color': '#000000',
                      'font_style': 'Courier', 'animation': 'matrix'},
            "Neon": {'time_color': '#ff1493', 'date_color': '#7fff00', 'bg_color': '#0a0a0a',
                    'font_style': 'Arial', 'animation': 'rainbow'}
        }
        
        def apply_preset(preset_name):
            preset = presets[preset_name]
            for key, value in preset.items():
                if key in self.mod_settings:
                    self.mod_settings[key] = value
            self.apply_settings()
        
        for preset_name in presets:
            btn = tk.Button(parent, text=preset_name, command=lambda p=preset_name: apply_preset(p),
                           bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'), width=15)
            btn.pack(pady=5)
    
    def choose_color(self, setting):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(title=f"Choose {setting}", color=self.mod_settings[setting])
        if color[1]:
            self.update_setting(setting, color[1])
    
    def update_setting(self, key, value):
        """Update a mod setting"""
        self.mod_settings[key] = value
        self.apply_settings()
    
    def apply_settings(self):
        """Apply all current mod settings"""
        # Update colors and fonts
        self.time_label.config(
            font=(self.mod_settings['font_style'], self.mod_settings['time_size'], 'bold'),
            fg=self.mod_settings['time_color']
        )
        
        if self.mod_settings['show_date']:
            self.date_label.config(
                font=(self.mod_settings['font_style'], self.mod_settings['date_size']),
                fg=self.mod_settings['date_color']
            )
        
        if self.mod_settings['show_weekday']:
            self.weekday_label.config(
                font=(self.mod_settings['font_style'], self.mod_settings['date_size'] - 10),
                fg=self.mod_settings['date_color']
            )
        
        # Update background
        self.root.configure(bg=self.mod_settings['bg_color'])
        self.main_frame.configure(bg=self.mod_settings['bg_color'])
        self.clock_frame.configure(bg=self.mod_settings['bg_color'])
        
        # Update opacity
        self.root.attributes('-alpha', self.mod_settings['opacity'])
        
        # Update visibility
        if self.mod_settings['show_date']:
            self.date_label.pack()
        else:
            self.date_label.pack_forget()
            
        if self.mod_settings['show_weekday']:
            self.weekday_label.pack()
        else:
            self.weekday_label.pack_forget()
    
    def update_clock(self):
        """Update the clock display"""
        now = datetime.now()
        
        # Format time based on settings
        if self.mod_settings['time_format'] == 24:
            time_str = now.strftime("%H:%M")
            if self.mod_settings['show_seconds']:
                time_str += now.strftime(":%S")
        else:
            time_str = now.strftime("%I:%M")
            if self.mod_settings['show_seconds']:
                time_str += now.strftime(":%S")
            time_str = time_str.lstrip('0')  # Remove leading zero
            time_str += now.strftime(" %p")
        
        # Format date
        date_str = now.strftime("%B %d, %Y")
        weekday_str = now.strftime("%A")
        
        # Update labels
        self.time_label.config(text=time_str)
        
        if self.mod_settings['show_date']:
            self.date_label.config(text=date_str)
        
        if self.mod_settings['show_weekday']:
            self.weekday_label.config(text=weekday_str)
        
        # Apply border effects
        if self.mod_settings['border_style'] == 'glow':
            self.clock_frame.config(highlightbackground=self.mod_settings['time_color'],
                                   highlightcolor=self.mod_settings['time_color'],
                                   highlightthickness=3)
        elif self.mod_settings['border_style'] == 'box':
            self.clock_frame.config(highlightbackground='white',
                                   highlightcolor='white',
                                   highlightthickness=2)
        else:
            self.clock_frame.config(highlightthickness=0)
        
        self.root.after(1000, self.update_clock)
    
    def update_animations(self):
        """Update visual animations"""
        now = datetime.now()
        
        if self.mod_settings['animation'] == 'rainbow':
            # Rainbow color cycling
            self.animation_hue += 0.005
            if self.animation_hue > 1:
                self.animation_hue = 0
            import colorsys
            rgb = colorsys.hsv_to_rgb(self.animation_hue, 1.0, 1.0)
            hex_color = '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            self.time_label.config(fg=hex_color)
            if self.mod_settings['show_date']:
                self.date_label.config(fg=hex_color)
            if self.mod_settings['show_weekday']:
                self.weekday_label.config(fg=hex_color)
        
        elif self.mod_settings['animation'] == 'pulse':
            # Pulsing effect
            self.pulse_value += 0.02 * self.pulse_direction
            if self.pulse_value >= 1:
                self.pulse_direction = -1
            elif self.pulse_value <= 0.5:
                self.pulse_direction = 1
            
            # Scale font size
            new_size = int(self.mod_settings['time_size'] * (0.9 + self.pulse_value * 0.1))
            self.time_label.config(font=(self.mod_settings['font_style'], new_size, 'bold'))
        else:
            # Reset to normal size for other animations
            self.time_label.config(font=(self.mod_settings['font_style'], self.mod_settings['time_size'], 'bold'))
        
        self.root.after(50, self.update_animations)
    
    def toggle_mod_menu(self, event=None):
        """Toggle mod menu visibility"""
        if self.mod_menu_visible:
            self.hide_mod_menu()
        else:
            self.show_mod_menu()
    
    def show_mod_menu(self):
        """Show mod menu"""
        self.mod_panel.deiconify()
        self.mod_menu_visible = True
    
    def hide_mod_menu(self):
        """Hide mod menu"""
        self.mod_panel.withdraw()
        self.mod_menu_visible = False
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)

if __name__ == "__main__":
    ClockModMenu()