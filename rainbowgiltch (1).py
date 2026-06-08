from PIL import Image, ImageDraw
import colorsys
import ctypes
import os

def set_windows_wallpaper(image_path):
    """Set wallpaper on Windows"""
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)

def create_and_set_rainbow_wallpaper():
    # Get screen resolution
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    
    # Create rainbow image
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    for x in range(width):
        hue = x / width
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        color = tuple(int(c * 255) for c in rgb)
        draw.line([(x, 0), (x, height)], fill=color)
    
    # Save and set as wallpaper
    temp_path = os.path.join(os.environ['TEMP'], 'rainbow_wallpaper.bmp')
    image.save(temp_path)
    set_windows_wallpaper(temp_path)
    print("Rainbow wallpaper set successfully!")

# Run
create_and_set_rainbow_wallpaper()