import board
import adafruit_dotstar

NUM_LEDS = 300  # Anpassen falls nötig

leds = adafruit_dotstar.DotStar(
    clock=board.SCK,
    data=board.MOSI,
    n=NUM_LEDS,
    brightness=1.0,
    auto_write=True
)

print("Schalte alle LEDs aus...")
leds.fill((0, 0, 0))
