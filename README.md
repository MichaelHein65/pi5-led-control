# LED Neon Control

Web-basierte Steuerung für ein 30x10 DotStar LED-Panel.

## Features

- 🕐 **Uhr-Anzeige** mit Regenbogen-Sekundenring
- 🌈 **Effekte**: Rainbow, Breathing, Sine Wave, Flash, Raupe
- 📜 **Laufschrift** mit einstellbarer Farbe und Geschwindigkeit
- 🌤️ **Wetter-Anzeige** für Ein Ort (automatisch um x:55 Uhr)
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

### API Key Konfiguration

Der OpenWeather API Key muss als Umgebungsvariable gesetzt werden:

```bash
# .env Datei erstellen
echo 'OPENWEATHER_API_KEY=dein_key_hier' > .env
```

Hole dir einen kostenlosen Key unter: https://openweathermap.org/api

## Buchstaben

Unterstützt: A-Z, Ä, Ö, Ü, ß, 0-9, Sonderzeichen (!, ?, ., -, ,, :)

## Version

**v1.0.3** (Dezember 2025)

## Auto-Helligkeit (Sonnenstand)

- Standort: `LATITUDE=50.0`, `LONGITUDE=8.9`, Zeitzone `Europe/Berlin` in `led_webapp.py`.
- Quelle: https://api.sunrise-sunset.org liefert Sonnenauf/-untergang, Cache wird 1x/Tag aktualisiert.
- Verhalten:
  - Nacht: MIN_BRIGHTNESS (0.1) von 1h vor Sonnenuntergang bis 1h nach Sonnenaufgang.
  - Ramp-Up: 2h nach Sonnenaufgang hoch auf MAX_BRIGHTNESS (1.0).
  - Abend: 3h vor Sonnenuntergang dimmen, 1h vorher Minimum.
  - Tag: MAX_BRIGHTNESS.
- Manuelles Override: Helligkeits-Slider setzt den Wert für 5 Minuten fest; danach übernimmt die Automatik wieder. Im Log erscheint `>> Auto-Helligkeit: ...`.

## Wetter-Troubleshooting (OpenWeather)

1. `.env` prüfen: `cat /home/pi/ledcontrol/.env` → `OPENWEATHER_API_KEY=<dein key>`.
2. Test-Endpoint lokal: `curl -X POST http://localhost:5050/test_weather`.
   - Erwartet: `success:true` und `key:"89d0...f867"`.
   - Bei 401: Key falsch/gesperrt oder mit Whitespaces; `.env` korrigieren, Service neu starten.
3. Logs: `journalctl -u ledserver.service -n 30 | grep Wetter-Fehler`.
4. Direkt gegen API: `curl "https://api.openweathermap.org/data/2.5/weather?q=Ein Ort,DE&appid=<KEY>&units=metric&lang=de"`.

## Git / GitHub Workflow (Kurz)

- Status prüfen: `git status -sb`
- Änderungen ansehen: `git diff` oder `git diff --stat`
- Commit: `git add <files> && git commit -m "Kurze, präzise Nachricht"`
- GitHub-Remote setzen (falls noch nicht): `git remote add origin git@github.com:<user>/ledcontrol.git`
- Push: `git push -u origin main`

Hinweis: Secrets wie `.env` nicht ins Repo committen.
