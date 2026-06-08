import turtle
import colorsys

# Setup
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Rainbow GDL")

t = turtle.Turtle()
t.speed(0)
t.width(3)

def draw_rainbow_spiral():
    """Draw a rainbow spiral"""
    t.penup()
    t.goto(0, 0)
    t.pendown()
    
    for i in range(360):
        hue = i / 360.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        t.color(r, g, b)
        t.forward(i * 0.5)
        t.right(59)
    
    t.hideturtle()

def draw_rainbow_circles():
    """Draw concentric rainbow circles"""
    t.penup()
    t.goto(0, -100)
    t.pendown()
    
    radius = 20
    for i in range(18):
        hue = i / 18.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        t.color(r, g, b)
        t.circle(radius)
        radius += 15

# Choose your design
draw_rainbow_spiral()
# draw_rainbow_circles()

screen.mainloop()