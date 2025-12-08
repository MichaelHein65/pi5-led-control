# LED Neon Control

Web-basierte Steuerung für ein 30x10 DotStar LED-Panel.

## Features

- 🕐 **Uhr-Anzeige** mit Regenbogen-Sekundenring
- 🌈 **Effekte**: Rainbow, Breathing, Sine Wave, Flash, Raupe
- 📜 **Laufschrift** mit einstellbarer Farbe und Geschwindigkeit
- 🌤️ **Wetter-Anzeige** für Rodgau (automatisch um x:55 Uhr)
  - Temperatur, Beschreibung, Luftfeuchtigkeit und **Luftdruck (hPa)**
- 🎨 **Statische Farbe** mit Helligkeitsregler

## Installation

```bash
cd /home/pi/ledcontrol
source led-venv/bin/activate
pip install flask adafruit-blinka adafruit-circuitpython-dotstar requests
```

## Starten

```bash
source /home/pi/ledcontrol/led-venv/bin/activate
python led_webapp.py
```

## Web-Interface

Das Web-Interface bietet:
- **ALLES AN / AUS** - Schnellsteuerung mit Farbwahl
- **Laufschrift** - Text eingeben mit Geschwindigkeit und Farbwahl
- **Wetter-Button** (gelb) - Aktuelle Wetterdaten anzeigen
- **Uhr-Button** (lila) - Digitaluhr mit Sekundenring starten
- **Helligkeitsregler** - Globale Helligkeit anpassen
- **Effekt-Buttons** - Verschiedene LED-Animationen
- **Live-Vorschau** - Canvas zeigt LED-Status in Echtzeit

## API Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/effect/<idx>` | POST | Effekt starten (0-7) |
| `/off` | POST | LEDs ausschalten |
| `/static_on` | POST | Statische Farbe an |
| `/static_color` | POST | Farbe setzen (hue: 0-1) |
| `/brightness` | POST | Helligkeit (value: 0-1) |
| `/scrolltext` | POST | Laufschrift (text, speed, hue) |
| `/test_weather` | POST | Wetter-Laufschrift testen |
| `/led_status` | GET | LED-Status für Vorschau |

## Effekte

| Index | Name |
|-------|------|
| 0 | Rainbow |
| 1 | Breathing |
| 2 | Sine Wave |
| 3 | Flash |
| 4 | Diagnose |
| 5 | Clock |
| 6 | Rainbow Caterpillar |
| 7 | Rainbow Wave |

## Wetter-Feature

- Automatisch um **x:55 Uhr** jede Stunde
- Zeigt: Temperatur, Beschreibung, Luftfeuchtigkeit, **Luftdruck**
- Farbe basiert auf Temperatur (blau=kalt, grün=mild, rot=heiß)
- Nach 2 Durchläufen → zurück zur Uhr

## Buchstaben

Unterstützt: A-Z, Ä, Ö, Ü, ß, 0-9, Sonderzeichen (!, ?, ., -, ,, :)

## Version

**v1.0.2** (Dezember 2025)
