import time
import board
import adafruit_dotstar
import numpy as np

# Konfiguration
NUM_LEDS = 300
GROUPS = 10
GROUP_SIZE = NUM_LEDS // GROUPS
WAVE_SPEED = 0.15  # LANGSAM!
GAMMA = 2.2

# LED-Strip Setup
leds = adafruit_dotstar.DotStar(
    clock=board.SCK,
    data=board.MOSI,
    n=NUM_LEDS,
    brightness=1.0,
    auto_write=False
)

# Gamma-Korrektur
def apply_gamma(value):
    return value ** GAMMA

# Regenbogen-Farben je nach Phase
def get_color(phase):
    phase = phase % 1.0
    r = max(0, np.cos(2 * np.pi * (phase)) * 0.5 + 0.5)
    g = max(0, np.cos(2 * np.pi * (phase - 1/3)) * 0.5 + 0.5)
    b = max(0, np.cos(2 * np.pi * (phase - 2/3)) * 0.5 + 0.5)
    return int(apply_gamma(r) * 255), int(apply_gamma(g) * 255), int(apply_gamma(b) * 255)

# Hauptloop
frame = 0
while True:
    leds.fill((0, 0, 0))
    for i in range(NUM_LEDS):
        group_pos = i % GROUP_SIZE
        center = GROUP_SIZE // 2
        distance = abs(group_pos - center)
        norm = max(0.0, 1.0 - (distance / center))  # Dreiecksform
        brightness = apply_gamma(norm)
        phase = (frame / 400 + i / NUM_LEDS) % 1.0  # LANGSAMER PHASENFORTSCHRITT
        color = get_color(phase)
        leds[i] = tuple(int(c * brightness) for c in color)
    leds.show()
    time.sleep(WAVE_SPEED)
    frame += 1
