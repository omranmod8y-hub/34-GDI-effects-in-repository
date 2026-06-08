import turtle
import random
import time

# Set up screen with DARK MODE
screen = turtle.Screen()
screen.title("Cat and Dog - Find the Gold (Dark Mode)")
screen.bgcolor("#0a0a2a")  # Deep dark blue
screen.setup(width=800, height=600)
screen.tracer(0)

# Draw ground (dark ground)
ground = turtle.Turtle()
ground.speed(0)
ground.color("#1a1a3a")  # Dark ground
ground.penup()
ground.goto(-400, -200)
ground.pendown()
ground.begin_fill()
for _ in range(2):
    ground.forward(800)
    ground.right(90)
    ground.forward(100)
    ground.right(90)
ground.end_fill()
ground.hideturtle()

# Decorative stars in background
stars = []
for _ in range(50):
    star = turtle.Turtle()
    star.shape("circle")
    star.color("white")
    star.shapesize(0.2, 0.2)
    star.penup()
    star.speed(0)
    star.goto(random.randint(-380, 380), random.randint(-180, 250))
    star.hideturtle()
    stars.append(star)

# Dog (player) - glowing effect
dog = turtle.Turtle()
dog.shape("turtle")
dog.color("#d4731a")  # Warm orange-brown
dog.penup()
dog.speed(0)
dog.goto(0, -150)
dog.setheading(90)

# Cat (enemy) - neon orange
cat = turtle.Turtle()
cat.shape("turtle")
cat.color("#ff6b35")  # Neon orange
cat.penup()
cat.speed(0)
cat.goto(random.randint(-350, 350), random.randint(-150, 150))

# Gold coin - with glow effect
gold = turtle.Turtle()
gold.shape("circle")
gold.color("#ffd700")  # Bright gold
gold.penup()
gold.speed(0)
gold.shapesize(1.5, 1.5)
gold.goto(random.randint(-350, 350), random.randint(-150, 150))

# Glow effect for gold (alternating colors)
def gold_glow():
    if time_left > 0 and lives > 0:
        colors = ["#ffd700", "#ffed4a", "#ffd700"]
        current = gold.color()[0]
        next_color = colors[(colors.index(current) + 1) % len(colors)] if current in colors else "#ffd700"
        gold.color(next_color)
        screen.ontimer(gold_glow, 200)

# Score display - neon green
score_display = turtle.Turtle()
score_display.speed(0)
score_display.color("#00ff88")  # Neon green
score_display.penup()
score_display.hideturtle()
score_display.goto(0, 260)
score = 0
score_display.write(f"💰 GOLD: {score}", align="center", font=("Courier", 24, "bold"))

# Timer display - neon cyan
timer_display = turtle.Turtle()
timer_display.speed(0)
timer_display.color("#00ffff")  # Neon cyan
timer_display.penup()
timer_display.hideturtle()
timer_display.goto(0, 220)
time_left = 45
timer_display.write(f"⏱️ TIME: {time_left}", align="center", font=("Courier", 20, "bold"))

# Lives display - neon pink hearts
lives_display = turtle.Turtle()
lives_display.speed(0)
lives_display.color("#ff3366")  # Neon pink
lives_display.penup()
lives_display.hideturtle()
lives_display.goto(0, 180)
lives = 3
lives_display.write(f"❤️ LIVES: {'❤️ ' * lives}", align="center", font=("Courier", 20, "normal"))

# Border decoration
border = turtle.Turtle()
border.speed(0)
border.color("#00ffff")
border.penup()
border.goto(-390, -250)
border.pendown()
border.pensize(3)
for _ in range(2):
    border.forward(780)
    border.right(90)
    border.forward(500)
    border.right(90)
border.hideturtle()

# Movement functions
def move_up():
    y = dog.ycor()
    if y < 180:
        dog.sety(y + 20)

def move_down():
    y = dog.ycor()
    if y > -180:
        dog.sety(y - 20)

def move_left():
    x = dog.xcor()
    if x > -380:
        dog.setx(x - 20)

def move_right():
    x = dog.xcor()
    if x < 380:
        dog.setx(x + 20)

# Keyboard bindings
screen.listen()
screen.onkeypress(move_up, "Up")
screen.onkeypress(move_down, "Down")
screen.onkeypress(move_left, "Left")
screen.onkeypress(move_right, "Right")

# Cat movement (simple AI - moves toward dog)
def move_cat():
    if time_left > 0 and lives > 0:
        cat_x, cat_y = cat.position()
        dog_x, dog_y = dog.position()
        
        # Move cat toward dog
        if cat_x < dog_x:
            cat.setx(cat_x + random.randint(3, 8))
        else:
            cat.setx(cat_x - random.randint(3, 8))
            
        if cat_y < dog_y:
            cat.sety(cat_y + random.randint(3, 8))
        else:
            cat.sety(cat_y - random.randint(3, 8))
        
        # Keep cat within bounds
        if cat.xcor() > 380:
            cat.setx(380)
        if cat.xcor() < -380:
            cat.setx(-380)
        if cat.ycor() > 180:
            cat.sety(180)
        if cat.ycor() < -180:
            cat.sety(-180)
    
    if time_left > 0 and lives > 0:
        screen.ontimer(move_cat, 300)

# Update timer
def update_timer():
    global time_left
    if time_left > 0 and lives > 0:
        time_left -= 1
        timer_display.clear()
        timer_display.write(f"⏱️ TIME: {time_left}", align="center", font=("Courier", 20, "bold"))
        
        # Warning when time is low
        if time_left <= 10:
            timer_display.color("#ff3366")
            if time_left % 2 == 0:  # Blink effect
                screen.bgcolor("#1a0033")
            else:
                screen.bgcolor("#0a0a2a")
        
        screen.update()
        screen.ontimer(update_timer, 1000)
    elif lives > 0:
        game_over(win=True)
    else:
        game_over(win=False)

# Collision detection and scoring
def check_collisions():
    global score, lives
    
    # Check gold collection
    if dog.distance(gold) < 25:
        score += 1
        score_display.clear()
        score_display.write(f"💰 GOLD: {score}", align="center", font=("Courier", 24, "bold"))
        
        # Move gold to new random position
        gold.goto(random.randint(-350, 350), random.randint(-150, 150))
        
        # Visual feedback - screen flash
        try:
            screen.bgcolor("#ffff00")
            screen.update()
            time.sleep(0.05)
            screen.bgcolor("#0a0a2a")
        except:
            pass
        
        # Play a little celebration animation
        gold.shapesize(2, 2)
        screen.ontimer(lambda: gold.shapesize(1.5, 1.5), 100)
    
    # Check cat collision (dog loses a life)
    if dog.distance(cat) < 25:
        lives -= 1
        lives_display.clear()
        lives_display.write(f"❤️ LIVES: {'❤️ ' * lives if lives > 0 else '💀 '}", align="center", font=("Courier", 20, "normal"))
        
        # Teleport dog to safety
        dog.goto(0, -150)
        
        # Teleport cat away
        cat.goto(random.randint(-350, 350), random.randint(-150, 150))
        
        # Visual feedback (damage)
        try:
            screen.bgcolor("#ff0000")
            screen.update()
            time.sleep(0.1)
            screen.bgcolor("#0a0a2a")
        except:
            pass
        
        # Shake effect for dog
        original_pos = dog.position()
        for _ in range(5):
            dog.setx(dog.xcor() + random.randint(-5, 5))
            dog.sety(dog.ycor() + random.randint(-5, 5))
            screen.update()
            time.sleep(0.02)
        dog.goto(original_pos)
        
        # Check if game over due to lives
        if lives <= 0:
            game_over(win=False)
            return
    
    screen.update()
    if time_left > 0 and lives > 0:
        screen.ontimer(check_collisions, 50)

# Game over function with dark mode styling
def game_over(win):
    cat.hideturtle()
    dog.hideturtle()
    gold.hideturtle()
    
    game_over_text = turtle.Turtle()
    game_over_text.speed(0)
    game_over_text.penup()
    game_over_text.hideturtle()
    
    if win:
        if score >= 15:
            message = f"🏆 PERFECT! {score} GOLD PIECES! 🏆"
            game_over_text.color("#00ff88")
        else:
            message = f"✨ VICTORY! {score} GOLD PIECES! ✨"
            game_over_text.color("#00ffff")
    else:
        if score >= 10:
            message = f"💀 GAME OVER! {score} GOLD (Good job!) 💀"
        else:
            message = f"💀 GAME OVER! Only {score} GOLD. TRY AGAIN! 💀"
        game_over_text.color("#ff3366")
    
    game_over_text.write(message, align="center", font=("Courier", 20, "bold"))
    
    # Add restart instruction
    restart_text = turtle.Turtle()
    restart_text.speed(0)
    restart_text.color("#8888ff")
    restart_text.penup()
    restart_text.hideturtle()
    restart_text.goto(0, -50)
    restart_text.write("Press 'R' to restart or click to exit", align="center", font=("Arial", 12, "normal"))
    
    # Restart function
    def restart_game():
        screen.clearscreen()
        screen.bgcolor("#0a0a2a")
        # Re-import and restart (simplified - just reload the script logic)
        os.system("python " + __file__)
    
    screen.onkeypress(restart_game, "r")
    screen.update()

# Instructions with dark mode
def show_instructions():
    instruct = turtle.Turtle()
    instruct.speed(0)
    instruct.color("#00ffff")
    instruct.penup()
    instruct.hideturtle()
    
    # Dark panel background
    panel = turtle.Turtle()
    panel.speed(0)
    panel.color("#1a1a3a")
    panel.penup()
    panel.goto(-300, 50)
    panel.pendown()
    panel.begin_fill()
    for _ in range(2):
        panel.forward(600)
        panel.right(90)
        panel.forward(200)
        panel.right(90)
    panel.end_fill()
    panel.hideturtle()
    
    instructions = [
        "🐕 DOG: Collect GOLD coins (Avoid the NEON CAT!)",
        "🐱 CAT: Moves toward you - lose a life if caught",
        "⭐ Arrow Keys to move",
        "🎯 Goal: Collect as much gold as possible in 45 seconds",
        "❤️ You have 3 lives",
        "",
        "✨ DARK MODE ACTIVATED! ✨"
    ]
    
    y_pos = 80
    for line in instructions:
        instruct.goto(0, y_pos)
        if "DARK MODE" in line:
            instruct.color("#ff6b35")
        else:
            instruct.color("#00ff88" if "DOG" in line else "#00ffff")
        instruct.write(line, align="center", font=("Arial", 12, "bold" if "DARK" in line else "normal"))
        y_pos -= 25
    
    screen.update()
    time.sleep(3)
    instruct.clear()
    panel.clear()

# Start the game
gold_glow()  # Start gold glow effect
show_instructions()
screen.update()
screen.ontimer(move_cat, 500)
screen.ontimer(update_timer, 1000)
screen.ontimer(check_collisions, 50)

# Keep window open
screen.mainloop()