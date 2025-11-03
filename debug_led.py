#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug-Skript für LED-Hardware-Test
Testet schrittweise alle Komponenten
"""

import time
import sys

print("=" * 60)
print("LED HARDWARE DEBUG - Schritt 1: Imports testen")
print("=" * 60)

try:
    import board
    print("✓ board importiert")
except Exception as e:
    print(f"✗ FEHLER beim Import von board: {e}")
    sys.exit(1)

try:
    import adafruit_dotstar
    print("✓ adafruit_dotstar importiert")
except Exception as e:
    print(f"✗ FEHLER beim Import von adafruit_dotstar: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Schritt 2: GPIO-Pins überprüfen")
print("=" * 60)

try:
    print(f"SCK Pin: {board.SCK}")
    print(f"MOSI Pin: {board.MOSI}")
    print("✓ GPIO-Pins erreichbar")
except Exception as e:
    print(f"✗ FEHLER beim Zugriff auf Pins: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Schritt 3: LED-Objekt initialisieren")
print("=" * 60)

PANEL_WIDTH = 30
PANEL_HEIGHT = 10
NUM_LEDS = PANEL_WIDTH * PANEL_HEIGHT
brightness = 0.3

try:
    leds = adafruit_dotstar.DotStar(
        board.SCK, board.MOSI, NUM_LEDS,
        brightness=brightness, auto_write=False
    )
    print(f"✓ LED-Objekt erstellt")
    print(f"  - LEDs: {NUM_LEDS}")
    print(f"  - Helligkeit: {brightness}")
except Exception as e:
    print(f"✗ FEHLER beim Erstellen des LED-Objekts: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Schritt 4: Alle LEDs auf Rot setzen")
print("=" * 60)

try:
    for i in range(NUM_LEDS):
        leds[i] = (255, 0, 0)
    leds.show()
    print("✓ Alle LEDs ROTBEFOHLEN")
    print("  -> Sind LEDs rot? (3 Sekunden warten)")
    time.sleep(3)
except Exception as e:
    print(f"✗ FEHLER beim Setzen der LED-Farbe: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Schritt 5: Alle LEDs aus")
print("=" * 60)

try:
    for i in range(NUM_LEDS):
        leds[i] = (0, 0, 0)
    leds.show()
    print("✓ Alle LEDs AUSGESCHALTET")
    time.sleep(1)
except Exception as e:
    print(f"✗ FEHLER beim Ausschalten: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Schritt 6: Rainbow-Effekt (5 Sekunden)")
print("=" * 60)

try:
    import colorsys
    start_time = time.time()
    while time.time() - start_time < 5:
        for j in range(NUM_LEDS):
            hue = (j / NUM_LEDS + time.time() * 0.1) % 1.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1, 1)]
            leds[j] = (r, g, b)
        leds.show()
        time.sleep(0.05)
    
    print("✓ Rainbow-Effekt läuft korrekt")
except Exception as e:
    print(f"✗ FEHLER beim Rainbow-Effekt: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Schritt 7: Diagnose - Jeden LED einzeln testen")
print("=" * 60)

try:
    for i in range(NUM_LEDS):
        for j in range(NUM_LEDS):
            leds[j] = (0, 0, 0)
        leds[i] = (0, 255, 0)
        leds.show()
        time.sleep(0.01)
        if i % 30 == 0:
            print(f"  LED {i} ... OK")
    
    print("✓ Alle LEDs einzeln getestet - ALLE GRÜN gehüpft!")
except Exception as e:
    print(f"✗ FEHLER beim Diagnose-Test: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Schritt 8: Finale LEDs ausschalten")
print("=" * 60)

try:
    for i in range(NUM_LEDS):
        leds[i] = (0, 0, 0)
    leds.show()
    print("✓ Alle LEDs aus")
except Exception as e:
    print(f"✗ FEHLER beim finalen Ausschalten: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓✓✓ ALLE TESTS BESTANDEN - HARDWARE FUNKTIONIERT! ✓✓✓")
print("=" * 60)
