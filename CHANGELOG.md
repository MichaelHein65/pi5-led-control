# CHANGELOG

Alle bemerkenswerten Änderungen an diesem Projekt sind in dieser Datei dokumentiert.

## [Unreleased]

## [1.0.2] - 2025-12-08

### ✨ Features
- **Wetteranzeige erweitert:** Luftdruck (hPa) wird jetzt zusätzlich zu Temperatur, Beschreibung und Luftfeuchtigkeit angezeigt
- **Neuer Uhr-Button:** Separater Button im Web-Interface um die Uhr-Anzeige zu starten
  - Lila/Violett Design passend zum Wetter-Button
  - Direkter Zugriff auf den Clock-Effekt

### 🎨 UI-Verbesserungen
- Wetter- und Uhr-Buttons als Paar untereinander angeordnet
- Einheitliches Design mit unterschiedlichen Farben (Gelb für Wetter, Lila für Uhr)

---

## [1.0.1] - 2025-11-03

### 🐛 Bugfix
- **KRITISCH:** LED-State-Cache und update_leds() Wrapper wiederhergestellt
  - Commit `b4a15bf` hatte versehentlich die Web-Vorschau-Architektur entfernt
  - Fehlende Komponenten: `led_state_cache`, `update_leds()`, `/led_status` Endpoint
  - **Impact:** Web-Interface konnte LED-Status nicht abrufen, Vorschau funktionierte nicht
  - **Lösung:** Alle Komponenten wiederhergestellt, Effekte nutzen wieder `update_leds()`
  
### ✅ Verifiziert
- Hardware funktioniert nach dem Fix wieder
- Alle LED-Effekte reagieren auf Befehle
- Web-Vorschau zeigt LED-Status korrekt an
- Uhr-Effekt (Effekt 6) läuft stabil

### 📚 Dokumentation hinzugefügt
- `BUGFIX.md` - Detaillierte Fehler-Dokumentation
- `DEBUG.md` - Debugging-Anleitung
- `SYSTEMATIC_DEBUG.md` - Systematischer Debug-Prozess
- `debug_led.py` - Automatisiertes Hardware-Test-Skript
- `deploy.sh` - Deploy- und Test-Automation

---

## [1.0.0] - 2025-10-XX

### ✨ Features
- Web-basierte LED-Steuerung mit Flask Backend
- 10 verschiedene LED-Effekte (Rainbow, Breathing, Sine Wave, Flash, Diagnose, Uhr, Raupe, Sensor-Display)
- Responsive Web-UI mit Neon-Design
- Echtzeit-Canvas-Vorschau (30×10 Grid)
- BMP180 Sensor-Integration (Temperatur & Luftdruck)
- Digitale Uhr mit animiertem Sekundenring
- Helligkeitsregelung
- Statische Farbsteuerung mit HSV-Slider

### 🛠️ Technisch
- Python 3 Flask Backend
- Thread-basierte LED-Effekt-Verwaltung
- Snake-Pattern LED-Mapping mit Rotation
- Thread-sichere LED-Buffer-Updates
- SPI-Kommunikation (APA102/DotStar)
- I2C Sensor-Integration (BMP180)

---

## Bekannte Probleme

### (GELÖST ✅) Web-Vorschau funktioniert nicht
**Status:** BEHOBEN in v1.0.1
**Symptom:** Canvas-Vorschau zeigt keine LEDs
**Ursache:** Commit b4a15bf entfernte `/led_status` Endpoint
**Fix:** siehe v1.0.1

---

## Zukünftige Verbesserungen

- [ ] MQTT-Integration für Smart-Home
- [ ] Konfiguration per JSON (statt hardcodiert)
- [ ] Web-UI zur Laufzeit-Konfiguration der Rotation
- [ ] Effekt-Verkettung
- [ ] SD-Karten-Speicherung für Szenen
- [ ] Voice-Control Integration
- [ ] REST API Dokumentation (Swagger/OpenAPI)

