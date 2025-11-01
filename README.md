# 🌈 LED Neon Control

Web-basierte Steuerung für ein 30×10 APA102/DotStar LED-Panel auf Raspberry Pi 5.

## 🎨 Features

- **Web-Interface** mit Neon-Design
- **10 LED-Effekte**: Rainbow, Breathing, Sine Wave, Flash, Diagnose, Uhr, Raupe, Sensor-Display
- **Statische Farbsteuerung** mit Regenbogen-Slider
- **Helligkeitsregelung** (0-100%)
- **BMP180 Sensor-Integration** (Temperatur & Luftdruck)
- **Echtzeit-Uhr** mit Sekundenring

## 🛠️ Hardware

- Raspberry Pi 5
- 300x APA102/DotStar LEDs (30×10 Matrix, Snake-Pattern)
- BMP180 Sensor (I2C)
- Stromversorgung für LEDs (5V, ~18A bei voller Helligkeit)

### Verkabelung

| Komponente | GPIO Pin | Beschreibung |
|------------|----------|--------------|
| LED Data   | GPIO10 (MOSI) | SPI Data |
| LED Clock  | GPIO11 (SCK)  | SPI Clock |
| BMP180 SDA | GPIO2 (SDA)   | I2C Data |
| BMP180 SCL | GPIO3 (SCL)   | I2C Clock |

## 📦 Installation

### Voraussetzungen

```bash
sudo apt update
sudo apt install python3-pip python3-venv git
```

### Setup

```bash
# Repository klonen
git clone https://github.com/deinusername/ledcontrol.git
cd ledcontrol

# Virtual Environment erstellen
python3 -m venv led-venv
source led-venv/bin/activate

# Dependencies installieren
pip install flask adafruit-circuitpython-dotstar adafruit-blinka adafruit-circuitpython-bmp180

# SPI aktivieren (falls nicht aktiviert)
sudo raspi-config
# -> Interface Options -> SPI -> Enable
```

### Autostart einrichten

```bash
# Start-Script ausführbar machen
chmod +x start_led_server.sh

# Systemd Service erstellen (optional)
sudo nano /etc/systemd/system/ledcontrol.service
```

Service-Datei Inhalt:
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

[Install]
WantedBy=multi-user.target
```

Service aktivieren:
```bash
sudo systemctl enable ledcontrol.service
sudo systemctl start ledcontrol.service
```

## 🚀 Verwendung

### Manueller Start

```bash
cd /home/pi/ledcontrol
source led-venv/bin/activate
python led_webapp.py
```

### Web-Interface aufrufen

```
http://raspberrypi.local:5050/ledcontrol/
# oder
http://[IP-ADRESSE]:5050/ledcontrol/
```

## 🎮 Effekte

| Nr. | Name | Beschreibung |
|-----|------|--------------|
| 1 | Rainbow | Durchlaufender Regenbogen |
| 2 | Breathing | Pulsierendes weißes Licht |
| 3 | Sine Wave | Sinuswelle in Cyan/Blau |
| 4 | Flash | Blitzlicht in verschiedenen Farben |
| 5 | Diagnose | Einzelne LEDs durchlaufen (Test) |
| 6 | Clock | Digitale Uhr mit Sekundenring |
| 7 | Raupe | Regenbogen-Schlange (zufällige Bewegung) |
| 8 | °C / hPa | Temperatur & Luftdruck anzeigen |

## ⚙️ Konfiguration

### Panel-Ausrichtung anpassen

In `led_webapp.py` (Zeilen 7-9):

```python
rotate_x = False   # oben ↔ unten spiegeln
rotate_y = True    # links ↔ rechts spiegeln
rotate_z = True    # 180-Grad-Drehung
```

### LED-Anzahl ändern

```python
PANEL_WIDTH  = 30
PANEL_HEIGHT = 10
NUM_LEDS     = PANEL_WIDTH * PANEL_HEIGHT
```

## 🧪 Test-Scripts

- `led_test.py` - Basis-Test (Farben & Regenbogen)
- `led_wave_fade.py` - Wave-Effekt mit Gamma-Korrektur
- `Sensortest.py` - BMP180 Sensor auslesen

## 📁 Projekt-Struktur

```
ledcontrol/
├── led_webapp.py           # Flask Backend
├── index.html              # Web UI
├── start_led_server.sh     # Start-Script
├── led_test.py             # LED Test-Script
├── led_wave_fade.py        # Wave-Effekt Demo
├── Sensortest.py           # Sensor Test
└── README.md               # Diese Datei
```

## 🐛 Troubleshooting

### LEDs leuchten nicht
- SPI aktiviert? `sudo raspi-config` → Interface Options → SPI
- Stromversorgung ausreichend? (5V, min. 10A für 300 LEDs)
- Verkabelung korrekt? (Data→GPIO10, Clock→GPIO11)

### Sensor nicht gefunden
- I2C aktiviert? `sudo raspi-config` → Interface Options → I2C
- Sensor-Adresse prüfen: `i2cdetect -y 1` (sollte 0x77 zeigen)

### Web-Interface nicht erreichbar
- Port 5050 frei? `sudo netstat -tulpn | grep 5050`
- Firewall-Regel: `sudo ufw allow 5050`

## 📝 Lizenz

MIT License - Frei verwendbar für private und kommerzielle Projekte.

## 👤 Autor

Michael Hein - Raspberry Pi LED Control Project
