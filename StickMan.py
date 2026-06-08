import tkinter as tk
import math
import random
import time
import json

class DesktopPet:
    def __init__(self, root):
        self.root = root
        self.root.title("Alan Becker - Desktop Pet")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        
        # Make background transparent
        try:
            self.root.wm_attributes('-transparentcolor', '#1a1a1a')
            self.root.wm_attributes('-alpha', 0.95)
        except:
            pass
        
        # Window size
        self.width = 450
        self.height = 550
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, 
                                bg='#1a1a1a', highlightthickness=0)
        self.canvas.pack()
        
        # Desktop position
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.x_pos = self.screen_width // 2 - self.width // 2
        self.y_pos = self.screen_height - self.height - 50
        self.root.geometry(f'{self.width}x{self.height}+{int(self.x_pos)}+{int(self.y_pos)}')
        
        # Movement variables
        self.walking = True
        self.walk_speed = 2
        self.direction = 1  # 1 = right, -1 = left
        self.target_x = None
        
        # Jumping variables
        self.is_jumping = False
        self.jump_velocity = 0
        self.jump_height = 0
        self.original_y = self.y_pos
        
        # Pet stats
        self.stats = {
            'name': 'Stickie',
            'level': 1,
            'exp': 0,
            'exp_needed': 100,
            'health': 100,
            'max_health': 100,
            'hunger': 80,
            'happiness': 80,
            'energy': 80,
            'strength': 10,
            'defense': 10,
            'coins': 50,
        }
        
        # Pet state
        self.state = "walking"  # idle, walking, jumping, sleeping, eating, playing, training, battle
        self.expression = "normal"
        self.anim_time = 0
        self.last_update = time.time()
        
        # Animation variables
        self.arm_angle = 0
        self.leg_angle = 0
        self.tail_angle = 0
        self.blink_timer = 0
        
        # Inventory
        self.inventory = {
            'apple': 3,
            'toy': 2,
            'potion': 1
        }
        
        # Battle system
        self.in_battle = False
        self.enemy = None
        self.battle_log = []
        self.battle_ui_elements = []
        
        # Load save data
        self.load_game()
        
        # Create UI
        self.create_ui()
        
        # Bind events
        self.bind_controls()
        
        # Start game loops
        self.update_stats()
        self.animation_loop()
        self.walk_loop()  # Desktop walking loop
        
        # Show welcome message
        self.show_message(f"Welcome {self.stats['name']}! I walk around!", "#ffff00")
        
        # Auto-save
        self.auto_save()
    
    def create_ui(self):
        # Stats panel
        self.canvas.create_rectangle(5, 5, self.width-5, 130, 
                                    fill='black', outline='white', stipple='gray50')
        
        # Name and level
        self.name_text = self.canvas.create_text(15, 20, text=f"{self.stats['name']}", 
                                                  fill='white', font=('Arial', 14, 'bold'), anchor='w')
        self.level_text = self.canvas.create_text(200, 20, text=f"Lv.{self.stats['level']}", 
                                                   fill='yellow', font=('Arial', 12), anchor='w')
        
        # Health bar
        self.canvas.create_text(15, 45, text="Health:", fill='white', font=('Arial', 10), anchor='w')
        self.health_bar_bg = self.canvas.create_rectangle(80, 38, 280, 53, fill='gray', outline='')
        self.health_bar = self.canvas.create_rectangle(80, 38, 80 + (self.stats['health']/self.stats['max_health'])*200, 53, 
                                                        fill='red', outline='')
        self.health_text = self.canvas.create_text(290, 45, text=f"{self.stats['health']}/{self.stats['max_health']}", 
                                                    fill='white', font=('Arial', 8), anchor='w')
        
        # Hunger bar
        self.canvas.create_text(15, 65, text="Hunger:", fill='white', font=('Arial', 10), anchor='w')
        self.hunger_bar = self.canvas.create_rectangle(80, 58, 80 + self.stats['hunger']*2, 73, 
                                                       fill='orange', outline='')
        
        # Happiness bar
        self.canvas.create_text(15, 85, text="Happiness:", fill='white', font=('Arial', 10), anchor='w')
        self.happiness_bar = self.canvas.create_rectangle(80, 78, 80 + self.stats['happiness']*2, 93, 
                                                          fill='yellow', outline='')
        
        # Energy bar
        self.canvas.create_text(15, 105, text="Energy:", fill='white', font=('Arial', 10), anchor='w')
        self.energy_bar = self.canvas.create_rectangle(80, 98, 80 + self.stats['energy']*2, 113, 
                                                       fill='cyan', outline='')
        
        # Exp bar
        self.exp_bar = self.canvas.create_rectangle(5, 135, 5 + (self.stats['exp']/self.stats['exp_needed'])*(self.width-10), 148,
                                                     fill='purple', outline='')
        self.exp_text = self.canvas.create_text(self.width//2, 141, text=f"EXP: {self.stats['exp']}/{self.stats['exp_needed']}", 
                                                 fill='white', font=('Arial', 8))
        
        # Inventory panel
        self.canvas.create_rectangle(5, self.height-80, self.width-5, self.height-5,
                                      fill='black', outline='white', stipple='gray50')
        self.inv_text = self.canvas.create_text(self.width//2, self.height-70, 
                                                text=f"🍎:{self.inventory['apple']}  🧸:{self.inventory['toy']}  🧪:{self.inventory['potion']}  💰:{self.stats['coins']}",
                                                fill='white', font=('Arial', 9))
        
        # Message area
        self.message_text = self.canvas.create_text(self.width//2, self.height-45, text="", 
                                                     fill='white', font=('Arial', 10, 'bold'))
        
        # Action buttons
        button_y = self.height - 35
        self.create_button("Feed", 10, button_y, self.feed, 60)
        self.create_button("Play", 80, button_y, self.play, 60)
        self.create_button("Train", 150, button_y, self.train, 60)
        self.create_button("Sleep", 220, button_y, self.sleep, 60)
        self.create_button("Battle", 290, button_y, self.start_battle, 60)
        self.create_button("Jump", 360, button_y, self.jump, 50)
        
        # Close button
        self.close_btn = self.canvas.create_rectangle(self.width-25, 5, self.width-5, 25, 
                                                      fill='red', outline='white')
        self.close_text = self.canvas.create_text(self.width-15, 15, text='X', fill='white', font=('Arial', 10))
        self.canvas.tag_bind(self.close_btn, '<Button-1>', lambda e: self.close())
        self.canvas.tag_bind(self.close_text, '<Button-1>', lambda e: self.close())
    
    def create_button(self, text, x, y, command, width):
        btn = self.canvas.create_rectangle(x, y, x+width, y+28, fill='#333', outline='white')
        btn_text = self.canvas.create_text(x+width//2, y+14, text=text, fill='white', font=('Arial', 9))
        self.canvas.tag_bind(btn, '<Button-1>', lambda e: command())
        self.canvas.tag_bind(btn_text, '<Button-1>', lambda e: command())
    
    def draw_stickman(self):
        self.canvas.delete("stickman")
        
        center_x = self.width // 2
        base_y = self.height - 170
        
        # Jump offset
        jump_offset = self.jump_height
        
        head_y = base_y - 70 + jump_offset
        body_y = base_y - 40 + jump_offset
        
        # Head
        if self.expression == "angry":
            head_color = "#ffcccc"
        elif self.expression == "happy":
            head_color = "#ccffcc"
        elif self.expression == "surprised":
            head_color = "#ccccff"
        else:
            head_color = "white"
        
        self.canvas.create_oval(center_x-22, head_y-22, center_x+22, head_y+22, 
                                outline='black', width=3, fill=head_color, tags="stickman")
        
        # Eyes with blink
        if self.blink_timer > 0:
            self.canvas.create_line(center_x-12, head_y-5, center_x-4, head_y-5, fill='black', width=2, tags="stickman")
            self.canvas.create_line(center_x+4, head_y-5, center_x+12, head_y-5, fill='black', width=2, tags="stickman")
        else:
            if self.expression == "angry":
                self.canvas.create_line(center_x-16, head_y-10, center_x-7, head_y-5, fill='black', width=2, tags="stickman")
                self.canvas.create_line(center_x+16, head_y-10, center_x+7, head_y-5, fill='black', width=2, tags="stickman")
                self.canvas.create_oval(center_x-12, head_y-5, center_x-7, head_y+1, fill='black', tags="stickman")
                self.canvas.create_oval(center_x+7, head_y-5, center_x+12, head_y+1, fill='black', tags="stickman")
            elif self.expression == "happy":
                self.canvas.create_arc(center_x-16, head_y-12, center_x-5, head_y-2, start=0, extent=-180,
                                       outline='black', width=2, style=tk.ARC, tags="stickman")
                self.canvas.create_arc(center_x+5, head_y-12, center_x+16, head_y-2, start=0, extent=-180,
                                       outline='black', width=2, style=tk.ARC, tags="stickman")
            elif self.expression == "surprised":
                self.canvas.create_oval(center_x-13, head_y-8, center_x-5, head_y, fill='white', outline='black', width=1, tags="stickman")
                self.canvas.create_oval(center_x+5, head_y-8, center_x+13, head_y, fill='white', outline='black', width=1, tags="stickman")
                self.canvas.create_oval(center_x-10, head_y-6, center_x-8, head_y-4, fill='black', tags="stickman")
                self.canvas.create_oval(center_x+8, head_y-6, center_x+10, head_y-4, fill='black', tags="stickman")
            else:
                self.canvas.create_oval(center_x-12, head_y-6, center_x-6, head_y, fill='black', tags="stickman")
                self.canvas.create_oval(center_x+6, head_y-6, center_x+12, head_y, fill='black', tags="stickman")
        
        # Mouth
        if self.state == "sleeping":
            self.canvas.create_text(center_x+25, head_y-15, text="z", fill='white', font=('Arial', 12), tags="stickman")
            self.canvas.create_text(center_x+32, head_y-25, text="z", fill='white', font=('Arial', 16), tags="stickman")
            self.canvas.create_text(center_x+42, head_y-38, text="z", fill='white', font=('Arial', 20), tags="stickman")
        elif self.expression == "happy":
            self.canvas.create_arc(center_x-14, head_y+5, center_x+14, head_y+18, start=0, extent=-180,
                                   outline='black', width=2, style=tk.ARC, tags="stickman")
        elif self.expression == "angry":
            self.canvas.create_line(center_x-12, head_y+10, center_x+12, head_y+10, fill='black', width=2, tags="stickman")
        else:
            self.canvas.create_arc(center_x-12, head_y+5, center_x+12, head_y+15, start=0, extent=-180,
                                   outline='black', width=2, style=tk.ARC, tags="stickman")
        
        # Body
        body_end_x = center_x + (self.tail_angle * 0.3)
        self.canvas.create_line(center_x, body_y, body_end_x, body_y+70, fill='black', width=4, tags="stickman")
        
        # Arms (animated for walking)
        arm_angle = self.arm_angle if self.state == "walking" else 0
        if self.state == "training":
            arm_angle = 40 + arm_angle
        
        arm_left_x = center_x - 28 - arm_angle
        arm_right_x = center_x + 28 + arm_angle
        
        self.canvas.create_line(center_x, body_y+15, arm_left_x, body_y+50, fill='black', width=3, tags="stickman")
        self.canvas.create_line(center_x, body_y+15, arm_right_x, body_y+50, fill='black', width=3, tags="stickman")
        
        # Legs (animated for walking)
        leg_angle = self.leg_angle if self.state == "walking" else 0
        if self.state == "jumping":
            leg_angle = 30
        
        leg_left_x = center_x - 22 + leg_angle
        leg_right_x = center_x + 22 - leg_angle
        
        self.canvas.create_line(center_x, body_y+70, leg_left_x, body_y+110, fill='black', width=3, tags="stickman")
        self.canvas.create_line(center_x, body_y+70, leg_right_x, body_y+110, fill='black', width=3, tags="stickman")
        
        # Feet
        self.canvas.create_line(leg_left_x, body_y+110, leg_left_x-12, body_y+118, fill='black', width=3, tags="stickman")
        self.canvas.create_line(leg_right_x, body_y+110, leg_right_x+12, body_y+118, fill='black', width=3, tags="stickman")
        
        # Tail
        tail_x = center_x - 25 - self.tail_angle
        self.canvas.create_line(center_x-15, body_y+50, tail_x, body_y+65, fill='black', width=2, tags="stickman")
        
        # Walking dust particles
        if self.state == "walking" and self.walking:
            dust_x = center_x - 30 if self.direction == -1 else center_x + 30
            self.canvas.create_oval(dust_x-3, base_y+20, dust_x+3, base_y+26, 
                                    fill='gray', outline='', tags="stickman")
        
        if self.in_battle:
            self.canvas.create_text(center_x, head_y-45, text="⚔️ BATTLE ⚔️", 
                                    fill='red', font=('Arial', 12, 'bold'), tags="stickman")
    
    def walk_loop(self):
        """Makes the stickman walk across the desktop"""
        if self.walking and not self.in_battle and self.state != "sleeping" and not self.is_jumping:
            # Move window position
            self.x_pos += self.walk_speed * self.direction
            
            # Check boundaries
            if self.x_pos <= 0:
                self.x_pos = 0
                self.direction = 1
                self.show_message("Oof! Hit the wall!", "#ffff00")
                self.expression = "surprised"
                self.root.after(500, lambda: setattr(self, 'expression', 'normal'))
            elif self.x_pos >= self.screen_width - self.width:
                self.x_pos = self.screen_width - self.width
                self.direction = -1
                self.show_message("Oof! Hit the wall!", "#ffff00")
                self.expression = "surprised"
                self.root.after(500, lambda: setattr(self, 'expression', 'normal'))
            
            # Update window position
            self.root.geometry(f'{self.width}x{self.height}+{int(self.x_pos)}+{int(self.y_pos - self.jump_height)}')
            self.state = "walking"
        else:
            self.state = "idle"
        
        self.root.after(20, self.walk_loop)
    
    def jump(self):
        """Make the stickman jump"""
        if not self.is_jumping and not self.in_battle:
            self.is_jumping = True
            self.jump_velocity = -12
            self.state = "jumping"
            self.show_message("Jump! 🦘", "#00ff00")
            
            def update_jump():
                if self.is_jumping:
                    self.jump_height += self.jump_velocity
                    self.jump_velocity += 0.8  # gravity
                    
                    # Update window Y position
                    self.root.geometry(f'{self.width}x{self.height}+{int(self.x_pos)}+{int(self.y_pos - self.jump_height)}')
                    
                    if self.jump_height <= 0 and self.jump_velocity > 0:
                        self.is_jumping = False
                        self.jump_height = 0
                        self.jump_velocity = 0
                        self.state = "walking"
                        self.root.geometry(f'{self.width}x{self.height}+{int(self.x_pos)}+{int(self.y_pos)}')
                        return
                    
                    self.root.after(20, update_jump)
            
            update_jump()
    
    def animation_loop(self):
        self.anim_time += 0.1
        
        if self.state == "walking":
            self.arm_angle = 25 * math.sin(self.anim_time * 4)
            self.leg_angle = 25 * math.sin(self.anim_time * 4)
            self.tail_angle = 15 * math.sin(self.anim_time * 5)
        elif self.state == "jumping":
            self.arm_angle = 30
            self.leg_angle = 30
            self.tail_angle = 20
        elif self.state == "playing":
            self.arm_angle = 30 * math.sin(self.anim_time * 5)
            self.leg_angle = 25 * math.sin(self.anim_time * 5)
            self.tail_angle = 25 * math.sin(self.anim_time * 6)
        elif self.state == "training":
            self.arm_angle = 25 * math.sin(self.anim_time * 8)
            self.leg_angle = 15 * math.sin(self.anim_time * 8)
            self.tail_angle = 10 * math.sin(self.anim_time * 4)
        elif self.state == "sleeping":
            self.arm_angle = 5 * math.sin(self.anim_time)
            self.leg_angle = 5 * math.sin(self.anim_time)
            self.tail_angle = 3 * math.sin(self.anim_time)
        else:
            self.arm_angle = 8 * math.sin(self.anim_time * 1.5)
            self.leg_angle = 5 * math.sin(self.anim_time * 2)
            self.tail_angle = 12 * math.sin(self.anim_time * 3)
        
        # Blinking
        if self.blink_timer > 0:
            self.blink_timer -= 1
        elif random.random() < 0.003:
            self.blink_timer = 5
        
        self.draw_stickman()
        self.root.after(50, self.animation_loop)
    
    def update_stats(self):
        current_time = time.time()
        dt = min(current_time - self.last_update, 5)
        self.last_update = current_time
        
        if not self.in_battle and self.state != "sleeping":
            self.stats['hunger'] = max(0, self.stats['hunger'] - 0.8 * dt)
            self.stats['happiness'] = max(0, self.stats['happiness'] - 0.5 * dt)
            self.stats['energy'] = max(0, self.stats['energy'] - 0.6 * dt)
            
            if self.stats['hunger'] < 20:
                self.stats['happiness'] = max(0, self.stats['happiness'] - 1 * dt)
            
            if self.stats['hunger'] < 10 or self.stats['happiness'] < 10:
                self.stats['health'] = max(0, self.stats['health'] - 2 * dt)
            elif self.stats['health'] < self.stats['max_health'] and self.stats['hunger'] > 50:
                self.stats['health'] = min(self.stats['max_health'], self.stats['health'] + 1 * dt)
        
        if self.state == "sleeping":
            self.stats['energy'] = min(100, self.stats['energy'] + 8 * dt)
            self.stats['health'] = min(self.stats['max_health'], self.stats['health'] + 3 * dt)
        
        # Check death
        if self.stats['health'] <= 0:
            self.stats['health'] = self.stats['max_health'] // 2
            self.stats['hunger'] = 50
            self.stats['energy'] = 50
            self.show_message("You died! Revived with half health!", "#ff0000")
        
        # Update UI
        self.update_ui()
        
        self.root.after(1000, self.update_stats)
    
    def update_ui(self):
        self.canvas.coords(self.health_bar, 80, 38, 80 + (self.stats['health']/self.stats['max_health'])*200, 53)
        self.canvas.coords(self.hunger_bar, 80, 58, 80 + self.stats['hunger']*2, 73)
        self.canvas.coords(self.happiness_bar, 80, 78, 80 + self.stats['happiness']*2, 93)
        self.canvas.coords(self.energy_bar, 80, 98, 80 + self.stats['energy']*2, 113)
        
        exp_width = (self.stats['exp'] / self.stats['exp_needed']) * (self.width - 10)
        self.canvas.coords(self.exp_bar, 5, 135, 5 + exp_width, 148)
        self.canvas.itemconfig(self.exp_text, text=f"EXP: {self.stats['exp']}/{self.stats['exp_needed']}")
        
        self.canvas.itemconfig(self.level_text, text=f"Lv.{self.stats['level']}")
        self.canvas.itemconfig(self.inv_text, 
                               text=f"🍎:{self.inventory['apple']}  🧸:{self.inventory['toy']}  🧪:{self.inventory['potion']}  💰:{self.stats['coins']}")
    
    def show_message(self, msg, color):
        self.canvas.itemconfig(self.message_text, text=msg, fill=color)
        self.root.after(3000, lambda: self.canvas.itemconfig(self.message_text, text=""))
    
    def gain_exp(self, amount):
        self.stats['exp'] += amount
        while self.stats['exp'] >= self.stats['exp_needed']:
            self.stats['exp'] -= self.stats['exp_needed']
            self.stats['level'] += 1
            self.stats['exp_needed'] = int(self.stats['exp_needed'] * 1.2)
            self.stats['max_health'] += 20
            self.stats['health'] = self.stats['max_health']
            self.stats['strength'] += 3
            self.stats['defense'] += 2
            self.show_message(f"LEVEL UP! Now level {self.stats['level']}! 🎉", "#ff00ff")
        
        self.update_ui()
        self.save_game()
    
    def feed(self):
        if self.inventory['apple'] > 0 and self.stats['hunger'] < 95:
            self.inventory['apple'] -= 1
            self.stats['hunger'] = min(100, self.stats['hunger'] + 30)
            self.stats['happiness'] = min(100, self.stats['happiness'] + 10)
            self.show_message("Yummy! +30 Hunger, +10 Happiness", "#00ff00")
            self.gain_exp(5)
            self.update_ui()
        else:
            self.show_message("No apples or not hungry!", "#ff0000")
    
    def play(self):
        if self.inventory['toy'] > 0 and self.stats['energy'] > 20:
            self.inventory['toy'] -= 1
            self.stats['happiness'] = min(100, self.stats['happiness'] + 40)
            self.stats['energy'] = max(0, self.stats['energy'] - 15)
            self.show_message("Wheee! +40 Happiness! 🎉", "#00ff00")
            self.state = "playing"
            self.root.after(2500, lambda: setattr(self, 'state', 'walking'))
            self.gain_exp(10)
            self.update_ui()
        else:
            self.show_message("No toys or too tired!", "#ff0000")
    
    def train(self):
        if self.stats['energy'] >= 30:
            self.stats['energy'] -= 20
            self.stats['hunger'] -= 10
            gain_strength = random.randint(1, 3)
            self.stats['strength'] += gain_strength
            self.show_message(f"Training! +{gain_strength} Strength! 💪", "#00ff00")
            self.state = "training"
            self.root.after(2500, lambda: setattr(self, 'state', 'walking'))
            self.gain_exp(15)
            self.update_ui()
        else:
            self.show_message("Not enough energy! Let me sleep!", "#ff0000")
    
    def sleep(self):
        if self.stats['energy'] < 90:
            self.walking = False
            self.state = "sleeping"
            self.show_message("Zzz... Energy and health restored! 😴", "#00ffff")
            self.root.after(4000, lambda: setattr(self, 'walking', True))
            self.root.after(4000, lambda: setattr(self, 'state', 'walking'))
        else:
            self.show_message("Not tired! Go play!", "#ffff00")
    
    def start_battle(self):
        if not self.in_battle and self.stats['energy'] > 20 and self.stats['health'] > 30:
            self.walking = False
            enemies = [
                {"name": "Slime", "health": 50, "max_health": 50, "strength": 8, "exp": 30, "coins": 20},
                {"name": "Goblin", "health": 80, "max_health": 80, "strength": 12, "exp": 50, "coins": 40},
                {"name": "Dark Knight", "health": 120, "max_health": 120, "strength": 18, "exp": 80, "coins": 60},
            ]
            
            self.enemy = random.choice(enemies).copy()
            self.in_battle = True
            self.state = "battle"
            self.battle_log = []
            self.show_message(f"⚔️ Battle started! Fight {self.enemy['name']}!", "#ff0000")
            self.create_battle_ui()
        else:
            self.show_message("Too weak to fight! Rest first!", "#ff0000")
    
    def create_battle_ui(self):
        for elem in self.battle_ui_elements:
            self.canvas.delete(elem)
        self.battle_ui_elements = []
        
        panel = self.canvas.create_rectangle(50, 150, self.width-50, 400, fill='black', outline='red', width=2)
        self.battle_ui_elements.append(panel)
        
        name = self.canvas.create_text(self.width//2, 175, text=f"{self.enemy['name']}", 
                                        fill='red', font=('Arial', 14, 'bold'))
        self.battle_ui_elements.append(name)
        
        bar_bg = self.canvas.create_rectangle(100, 190, self.width-100, 205, fill='gray', outline='')
        self.battle_ui_elements.append(bar_bg)
        
        self.enemy_hp_fill = self.canvas.create_rectangle(100, 190, 
                                                          100 + (self.enemy['health']/self.enemy['max_health'])*(self.width-200), 
                                                          205, fill='red', outline='')
        self.battle_ui_elements.append(self.enemy_hp_fill)
        
        self.battle_log_text = self.canvas.create_text(self.width//2, 310, text="", 
                                                        fill='white', font=('Arial', 10), anchor='s')
        self.battle_ui_elements.append(self.battle_log_text)
        
        # Battle buttons
        attack_btn = self.canvas.create_rectangle(70, 350, 170, 380, fill='#333', outline='white')
        attack_text = self.canvas.create_text(120, 365, text="ATTACK", fill='white', font=('Arial', 10, 'bold'))
        self.battle_ui_elements.extend([attack_btn, attack_text])
        self.canvas.tag_bind(attack_btn, '<Button-1>', lambda e: self.battle_attack())
        self.canvas.tag_bind(attack_text, '<Button-1>', lambda e: self.battle_attack())
        
        heal_btn = self.canvas.create_rectangle(190, 350, 290, 380, fill='#333', outline='white')
        heal_text = self.canvas.create_text(240, 365, text="HEAL", fill='white', font=('Arial', 10, 'bold'))
        self.battle_ui_elements.extend([heal_btn, heal_text])
        self.canvas.tag_bind(heal_btn, '<Button-1>', lambda e: self.battle_heal())
        self.canvas.tag_bind(heal_text, '<Button-1>', lambda e: self.battle_heal())
        
        run_btn = self.canvas.create_rectangle(310, 350, 390, 380, fill='#333', outline='white')
        run_text = self.canvas.create_text(350, 365, text="RUN", fill='white', font=('Arial', 10, 'bold'))
        self.battle_ui_elements.extend([run_btn, run_text])
        self.canvas.tag_bind(run_btn, '<Button-1>', lambda e: self.battle_run())
        self.canvas.tag_bind(run_text, '<Button-1>', lambda e: self.battle_run())
    
    def battle_attack(self):
        if not self.in_battle:
            return
        
        damage = self.stats['strength'] + random.randint(1, 8)
        self.enemy['health'] -= damage
        self.battle_log.append(f"You hit for {damage} damage!")
        
        if self.enemy['health'] <= 0:
            self.battle_victory()
            return
        
        enemy_damage = max(1, self.enemy['strength'] + random.randint(1, 6) - self.stats['defense']//3)
        self.stats['health'] -= enemy_damage
        self.battle_log.append(f"Enemy hits for {enemy_damage} damage!")
        
        self.update_ui()
        self.update_battle_ui()
        
        if self.stats['health'] <= 0:
            self.battle_defeat()
    
    def battle_heal(self):
        if self.inventory['potion'] > 0 and self.stats['health'] < self.stats['max_health']:
            self.inventory['potion'] -= 1
            heal_amount = 30 + self.stats['level'] * 2
            self.stats['health'] = min(self.stats['max_health'], self.stats['health'] + heal_amount)
            self.battle_log.append(f"You healed {heal_amount} HP!")
            self.update_ui()
            self.update_battle_ui()
            
            # Enemy attacks back
            enemy_damage = max(1, self.enemy['strength'] + random.randint(1, 5) - self.stats['defense']//3)
            self.stats['health'] -= enemy_damage
            self.battle_log.append(f"Enemy hits for {enemy_damage} damage!")
            
            if self.stats['health'] <= 0:
                self.battle_defeat()
            self.update_ui()
            self.update_battle_ui()
        else:
            self.battle_log.append("No potions!")
            self.update_battle_ui()
    
    def battle_run(self):
        if random.random() < 0.5:
            self.battle_log.append("You escaped!")
            self.update_battle_ui()
            self.end_battle()
        else:
            self.battle_log.append("Failed to escape!")
            enemy_damage = self.enemy['strength'] + random.randint(1, 5)
            self.stats['health'] -= enemy_damage
            self.battle_log.append(f"Enemy hits for {enemy_damage} damage!")
            self.update_ui()
            self.update_battle_ui()
            
            if self.stats['health'] <= 0:
                self.battle_defeat()
    
    def battle_victory(self):
        exp_gain = self.enemy['exp']
        coin_gain = self.enemy['coins']
        self.gain_exp(exp_gain)
        self.stats['coins'] += coin_gain
        self.show_message(f"Victory! +{exp_gain} EXP, +{coin_gain} coins!", "#00ff00")
        self.end_battle()
        self.update_ui()
    
    def battle_defeat(self):
        self.show_message("Defeated! Lost 30 coins!", "#ff0000")
        self.stats['health'] = self.stats['max_health'] // 2
        self.stats['coins'] = max(0, self.stats['coins'] - 30)
        self.end_battle()
        self.update_ui()
    
    def update_battle_ui(self):
        health_percent = self.enemy['health'] / self.enemy['max_health']
        new_width = 100 + health_percent * (self.width-200)
        self.canvas.coords(self.enemy_hp_fill, 100, 190, new_width, 205)
        
        log_display = "\n".join(self.battle_log[-3:])
        self.canvas.itemconfig(self.battle_log_text, text=log_display)
    
    def end_battle(self):
        self.in_battle = False
        self.state = "walking"
        self.walking = True
        self.enemy = None
        for elem in self.battle_ui_elements:
            self.canvas.delete(elem)
        self.battle_ui_elements = []
    
    def save_game(self):
        save_data = {
            'stats': self.stats,
            'inventory': self.inventory,
            'save_time': time.time()
        }
        try:
            with open('stickman_pet_save.json', 'w') as f:
                json.dump(save_data, f)
        except:
            pass
    
    def load_game(self):
        try:
            with open('stickman_pet_save.json', 'r') as f:
                save_data = json.load(f)
                self.stats = save_data['stats']
                self.inventory = save_data['inventory']
        except:
            pass
    
    def auto_save(self):
        self.save_game()
        self.root.after(60000, self.auto_save)
    
    def bind_controls(self):
        # Click on stickman
        self.canvas.tag_bind("stickman", '<Button-1>', lambda e: self.on_click())
        
        # Drag window
        self.canvas.bind('<Button-3>', self.start_drag)
        self.canvas.bind('<B3-Motion>', self.on_drag)
        
        # Keyboard shortcuts
        self.root.bind('<f>', lambda e: self.feed())
        self.root.bind('<p>', lambda e: self.play())
        self.root.bind('<t>', lambda e: self.train())
        self.root.bind('<s>', lambda e: self.sleep())
        self.root.bind('<b>', lambda e: self.start_battle())
        self.root.bind('<space>', lambda e: self.jump())
        self.root.bind('<Up>', lambda e: self.jump())
    
    def on_click(self):
        self.stats['happiness'] = min(100, self.stats['happiness'] + 10)
        self.show_message(f"Thanks for petting me! +10 Happiness ❤️", "#00ff00")
        self.update_ui()
    
    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.window_start_x = self.x_pos
        self.window_start_y = self.y_pos
    
    def on_drag(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.x_pos = self.window_start_x + dx
        self.y_pos = self.window_start_y + dy
        self.root.geometry(f'{self.width}x{self.height}+{int(self.x_pos)}+{int(self.y_pos)}')
    
    def close(self):
        self.save_game()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    pet = DesktopPet(root)
    
    print("\n" + "="*60)
    print("   🎮 ALAN BECKER STICKMAN - WALKS & JUMPS ON DESKTOP! 🎮")
    print("="*60)
    print("\n✨ Your stickman now WALKS ACROSS YOUR SCREEN and JUMPS! ✨")
    print("\n📖 CONTROLS:")
    print("   • SPACE or UP ARROW → JUMP!")
    print("   • Click on stickman → Pet him (+Happiness)")
    print("   • Click buttons → Feed, Play, Train, Sleep, Battle")
    print("   • Keyboard shortcuts:")
    print("     - [F] Feed     - [P] Play")
    print("     - [T] Train    - [S] Sleep")
    print("     - [B] Battle    - [SPACE] Jump")
    print("   • Right-click + drag → Move window anywhere")
    print("\n🎯 Watch him walk back and forth across your desktop!")
    print("   Press SPACE to make him JUMP!")
    print("="*60 + "\n")
    
    root.mainloop()