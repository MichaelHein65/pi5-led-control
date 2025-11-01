import time
import board
import adafruit_dotstar

# Anzahl der LEDs anpassen
NUM_LEDS = 300

# APA102 LED-Streifen initialisieren
leds = adafruit_dotstar.DotStar(
    clock=board.SCK,
    data=board.MOSI,
    n=NUM_LEDS,
    brightness=0.5,
    auto_write=True
)

print("Starte Grundfarbentest...")

# Endlosschleife: Rot → Grün → Blau
while True:
    leds.fill((255, 0, 0))  # Rot
    print("Rot")
    time.sleep(1)

    leds.fill((0, 255, 0))  # Grün
    print("Grün")
    time.sleep(1)

    leds.fill((0, 0, 255))  # Blau
    print("Blau")
    time.sleep(1)
