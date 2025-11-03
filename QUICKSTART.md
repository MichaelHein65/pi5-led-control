# 🚀 Quick Start Guide

Für diejenigen, die schnell anfangen möchten!

## Voraussetzung: Raspberry Pi 5 mit Raspberry OS

### 1️⃣ Automatisches Setup (empfohlen)

```bash
# Repository klonen
git clone https://github.com/MichaelHein65/pi5-led-control.git
cd pi5-led-control

# Setup Script ausführen (erstellt venv, installiert deps, etc.)
chmod +x setup.sh
./setup.sh
```

> ⚠️ Hinweis: `setup.sh` existiert noch nicht. Siehe "Manuelles Setup" darunter.

### 2️⃣ Manuelles Setup

```bash
# Virtual Environment erstellen
python3 -m venv led-venv
source led-venv/bin/activate

# Dependencies installieren
pip install flask adafruit-circuitpython-dotstar adafruit-blinka adafruit-circuitpython-bmp180

# SPI aktivieren (für LEDs)
sudo raspi-config
# Navigiere zu: Interface Options > SPI > Yes

# I2C aktivieren (für Sensor, optional)
sudo raspi-config
# Navigiere zu: Interface Options > I2C > Yes
```

### 3️⃣ Erste Tests

```bash
# Hardware-Test
python3 debug_led.py

# Wenn alles OK: ✅ Die LEDs sollten durchlaufen
# Wenn Error: Siehe SYSTEMATIC_DEBUG.md
```

### 4️⃣ Web-Server starten

```bash
# Terminal 1: Flask starten
source led-venv/bin/activate
python led_webapp.py

# Terminal 2 (oder Browser öffnen):
# http://raspberrypi.local:5050/ledcontrol/
```

### 5️⃣ Autostart einrichten (optional)

```bash
# Start-Script ausführbar machen
chmod +x start_led_server.sh

# Systemd Service erstellen
sudo nano /etc/systemd/system/ledserver.service
```

Inhalt:
```ini
[Unit]
Description=LED Control Web Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ledcontrol
ExecStart=/home/pi/ledcontrol/start_led_server.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Aktivieren:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ledserver.service
sudo systemctl start ledserver.service
```

## 🎮 Erste Schritte mit den LEDs

### Im Web-Interface:
1. **Rainbow** - Anklicken und genießen 🌈
2. **Helligkeit** - Mit dem Slider von 10-100% probieren
3. **Effekte** durchprobieren

### Mit curl (Terminal):
```bash
# Rainbow-Effekt
curl -X POST http://localhost:5050/effect/0

# Breathing-Effekt
curl -X POST http://localhost:5050/effect/1

# Alle ausschalten
curl -X POST http://localhost:5050/off

# LED-Status abrufen (JSON)
curl http://localhost:5050/led_status | python3 -m json.tool
```

## 🔧 Wichtige Konfigurationen

### Panel-Ausrichtung ändern

Datei: `led_webapp.py`, Zeilen 7-9

```python
rotate_x = False   # oben ↔ unten flippen
rotate_y = True    # links ↔ rechts flippen
rotate_z = True    # 180° Rotation
```

### Helligkeit Standard-Wert

Datei: `led_webapp.py`, Zeile 24

```python
brightness = 0.3   # 0.0 (dunkel) bis 1.0 (maximal)
```

## 🐛 Bei Problemen

1. **LEDs reagieren nicht:** `python3 debug_led.py`
2. **Web-Interface nicht erreichbar:** Port 5050 freigeben
3. **Sensor nicht gefunden:** `i2cdetect -y 1`

Für Details: siehe [SYSTEMATIC_DEBUG.md](SYSTEMATIC_DEBUG.md)

## 📚 Weiterführende Ressourcen

- [README.md](README.md) - Komplette Dokumentation
- [CHANGELOG.md](CHANGELOG.md) - Versions-Historie
- [BUGFIX.md](BUGFIX.md) - Letzte Bugfixes
- Copilot-Anleitung: siehe `.github/copilot-instructions.md`

## ✅ Checkliste für Setup

- [ ] Repository geklont
- [ ] Virtual Environment erstellt
- [ ] Dependencies installiert
- [ ] SPI aktiviert (raspi-config)
- [ ] I2C aktiviert (optional, für Sensor)
- [ ] `debug_led.py` erfolgreich gelaufen
- [ ] Web-Interface erreichbar
- [ ] Mindestens 1 LED-Effekt funktioniert
- [ ] (Optional) Autostart eingerichtet

## 🎉 Fertig!

Viel Spaß mit deinen LED-Effekten! 🌈✨

Bei Fragen: Issues auf GitHub erstellen oder README/Dokumentation lesen.
