# 🌈 LED Neon Control

Web-basierte Steuerung für ein 30×10 APA102/DotStar LED-Panel auf Raspberry Pi 5.

![LED Neon Control](https://img.shields.io/badge/LED-Neon%20Control-ff006e?style=for-the-badge)
![Raspberry Pi 5](https://img.shields.io/badge/Raspberry%20Pi-5-c51a4a?style=for-the-badge&logo=raspberry-pi)
![Python](https://img.shields.io/badge/Python-3.9+-3776ab?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask)

## 🎨 Features

- **Web-Interface** mit Neon-Design
- **10 LED-Effekte**:
  - 🌈 Rainbow - Zyklische Regenbogenfarben
  - 💨 Breathing - Pulsierendes weißes Licht
  - 🌊 Sine Wave - Welleneffekt über das Panel
  - ⚡ Flash - Stroboskop-Effekt
  - 🔍 Diagnose - Testet jede LED einzeln
  - 🕐 Uhr - Zeigt aktuelle Uhrzeit mit Sekundenring
  - 🐛 Raupe - Bewegendes Farbsegment
  - 📊 Sensor-Display - Visualisiert Sensor-Daten
  - 🎨 Gradient - Sanfte Farbübergänge
  - ✨ Sparkle - Funkelnde LEDs
- **Statische Farbsteuerung** mit Regenbogen-Slider
- **Helligkeitsregelung** (0-100%)
- **BMP180/BMP280 Sensor-Integration** (Temperatur & Luftdruck)
- **Echtzeit-Uhr** mit Sekundenring

## 📋 Voraussetzungen

### Hardware
- Raspberry Pi 5
- 30×10 APA102/DotStar LED-Panel (300 LEDs)
- BMP180 oder BMP280 Sensor (optional)
- Netzteil (5V, ausreichend für LEDs)

### Software
- Raspberry Pi OS (64-bit empfohlen)
- Python 3.9 oder höher
- pip (Python Package Manager)

## 🚀 Installation

### 1. Repository klonen

```bash
git clone https://github.com/MichaelHein65/pi5-led-control.git
cd pi5-led-control
```

### 2. Python Virtual Environment erstellen (empfohlen)

```bash
python3 -m venv venv
source venv/bin/activate  # Auf Linux/Mac
# oder
venv\Scripts\activate  # Auf Windows
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 4. Hardware-Verbindungen

#### APA102/DotStar LED-Panel
- **Clock (SCK)**: GPIO 11 (Pin 23)
- **Data (MOSI)**: GPIO 10 (Pin 19)
- **GND**: Ground
- **VCC**: 5V (externes Netzteil empfohlen)

#### BMP180/BMP280 Sensor
- **SDA**: GPIO 2 (Pin 3)
- **SCL**: GPIO 3 (Pin 5)
- **VCC**: 3.3V
- **GND**: Ground

### 5. I2C aktivieren (für BMP Sensor)

```bash
sudo raspi-config
# Navigiere zu: Interface Options > I2C > Enable
```

### 6. SPI aktivieren (für APA102 LEDs)

```bash
sudo raspi-config
# Navigiere zu: Interface Options > SPI > Enable
```

## 🎮 Verwendung

### Server starten

```bash
python3 app.py
```

Der Server startet auf Port 5000. Zugriff über:
- Lokal: `http://localhost:5000`
- Im Netzwerk: `http://<raspberry-pi-ip>:5000`

### Als Systemdienst einrichten (optional)

Erstelle eine systemd Service-Datei:

```bash
sudo nano /etc/systemd/system/led-control.service
```

Inhalt:

```ini
[Unit]
Description=LED Neon Control
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pi5-led-control
ExecStart=/home/pi/pi5-led-control/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Service aktivieren:

```bash
sudo systemctl daemon-reload
sudo systemctl enable led-control
sudo systemctl start led-control
```

Status prüfen:

```bash
sudo systemctl status led-control
```

## 📱 Web-Interface

Das Web-Interface bietet folgende Funktionen:

1. **Status-Anzeige**: Zeigt aktuellen Effekt und Helligkeit
2. **Sensor-Daten**: Echtzeit-Temperatur und Luftdruck
3. **Uhrzeit**: Aktuelle Zeit wird angezeigt
4. **Effekt-Auswahl**: 10 verschiedene LED-Effekte per Knopfdruck
5. **Farbsteuerung**: Regenbogen-Slider zur Auswahl statischer Farben
6. **Helligkeitsregelung**: Slider zur Anpassung der LED-Helligkeit

## 🛠️ Entwicklung

### Entwicklungsmodus (ohne Hardware)

Die Anwendung kann ohne echte Hardware entwickelt werden. Sie verwendet automatisch Mock-Objekte, wenn keine Hardware erkannt wird:

```bash
python3 app.py
```

### API-Endpoints

- `GET /api/effects` - Liste aller Effekte
- `POST /api/effect` - Effekt setzen
- `POST /api/brightness` - Helligkeit setzen
- `POST /api/color` - Statische Farbe setzen
- `GET /api/sensor` - Sensor-Daten abrufen
- `GET /api/status` - Aktuellen Status abrufen

## 🔧 Konfiguration

LED-Konfiguration kann in `app.py` angepasst werden:

```python
LED_WIDTH = 30   # Breite des LED-Panels
LED_HEIGHT = 10  # Höhe des LED-Panels
LED_COUNT = LED_WIDTH * LED_HEIGHT
```

## 🐛 Fehlerbehebung

### LEDs leuchten nicht
- Prüfe SPI-Verbindung (GPIO 10, 11)
- Überprüfe Stromversorgung (ausreichend für 300 LEDs)
- Aktiviere SPI: `sudo raspi-config`

### Sensor wird nicht erkannt
- Prüfe I2C-Verbindung (GPIO 2, 3)
- Aktiviere I2C: `sudo raspi-config`
- Teste I2C: `i2cdetect -y 1`

### Web-Interface nicht erreichbar
- Prüfe ob Server läuft: `sudo systemctl status led-control`
- Überprüfe Firewall-Einstellungen
- Teste lokalen Zugriff: `curl http://localhost:5000`

## 📄 Lizenz

Dieses Projekt ist Open Source und steht unter der MIT-Lizenz.

## 👨‍💻 Autor

Michael Hein

## 🙏 Danksagungen

- Adafruit für die hervorragenden LED- und Sensor-Bibliotheken
- Flask Framework für das Web-Backend
- Raspberry Pi Foundation