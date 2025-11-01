import time
import board
import adafruit_dotstar
import colorsys

# Anzahl deiner LEDs – bitte anpassen
NUM_LEDS = 299

# Initialisierung des APA102-Streifens über SPI
leds = adafruit_dotstar.DotStar(
    clock=board.SCK,              # Clock-Pin → GPIO11
    data=board.MOSI,              # Data-Pin  → GPIO10
    n=NUM_LEDS,
    brightness=0.4,
    auto_write=True
)

# Funktion: HSV → RGB
def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

print("Starte LED-Test...")

# Jede LED nacheinander rot
for i in range(NUM_LEDS):
    leds[i] = (255, 0, 0)
    time.sleep(0.05)

# Grün
leds.fill((0, 255, 0))
time.sleep(1)

# Blau
leds.fill((0, 0, 255))
time.sleep(1)

# Regenbogenlauf
print("Regenbogenlauf...")
while True:
    for j in range(256):
        hue = j / 256.0  # 0.0 bis 1.0
        for i in range(NUM_LEDS):
            pixel_hue = (hue + i / NUM_LEDS) % 1.0
            leds[i] = hsv_to_rgb(pixel_hue, 1.0, 1.0)
        time.sleep(0.02)
