import time
import board
import adafruit_dotstar

MAX_LEDS = 400  # Sicherheitspuffer – einfach mal großzügig
DELAY = 0.05    # Sekunden zwischen den LEDs

leds = adafruit_dotstar.DotStar(
    clock=board.SCK,
    data=board.MOSI,
    n=MAX_LEDS,
    brightness=0.3,
    auto_write=True
)

print("Starte LED-Zähltest...")

for i in range(MAX_LEDS):
    leds.fill((0, 0, 0))        # Alle aus
    leds[i] = (255, 0, 0)       # Eine LED rot
    print(f"LED #{i+1} leuchtet")
    time.sleep(DELAY)

