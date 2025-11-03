# LED Kette - Systematisches Debugging

## Aktuelle Situation
- Hardware: **Unverändert** (war vorher funktionsfähig)
- Problem: LEDs reagieren nicht mehr

## Debug-Plan

### SCHRITT 1: Auf Pi SSH-Verbindung herstellen
```bash
ssh pi5
cd /home/pi/ledcontrol
```

### SCHRITT 2: Python-Debug-Skript ausführen
```bash
source /home/pi/led-venv/bin/activate
python3 debug_led.py
```

Dies testet der Reihe nach:
1. **Imports** - Flask, Board, LEDs
2. **GPIO-Pins** - SCK und MOSI erreichbar?
3. **LED-Objekt** - Kann der LED-Strip initialisiert werden?
4. **Alle LEDs Rot** - Leuchten LEDs komplett rot auf?
5. **Alle aus** - Können LEDs ausgeschaltet werden?
6. **Rainbow** - Funktioniert der Effekt?
7. **Einzelne LEDs** - Sind alle 300 LEDs ansprechbar?

### SCHRITT 3: Ausgabe analysieren

Wenn die Ausgabe bei **Schritt X** hängt oder abbricht:

| Fehler bei Schritt | Ursache | Lösung |
|-------------------|--------|---------|
| Import board | GPIO/SPI nicht verfügbar | Raspberry Pi nicht richtig gebootet? |
| LED-Objekt | SPI-Kommunikation fehlgeschlagen | `sudo ls -la /dev/spidev*` prüfen |
| Alle LEDs Rot | Keine LED leuchtet | Stromversorgung der LEDs? |
| Alle LEDs Rot | Nur partial LEDs leuchten | LED-Fehler im Strip? |
| Einzelne LEDs | Nur einzelne LEDs don't leuchten | Defekte LED im Strip? |

### SCHRITT 4: Wenn Debugging erfolgreich

Wenn **debug_led.py** komplett läuft:
1. Die Hardware funktioniert
2. Das Problem ist im LED-Webapp-Code oder der Flask-Anwendung

### SCHRITT 5: Wenn Hardware defekt

Falls der Hardware-Test fehlschlägt:
1. **Stromversorgung überprüfen:**
   ```bash
   sudo systemctl stop ledserver.service
   # Multimeter an LED-Stromversorgung anschließen
   # Sollte ~5V sein
   ```

2. **SPI überprüfen:**
   ```bash
   ls -la /dev/spidev*
   # Sollte existieren
   ```

3. **GPIO überprüfen:**
   ```bash
   gpio readall
   # GPIO10 (MOSI) und GPIO11 (SCK) sollten vorhanden sein
   ```

## Was war die letzte funktionierende Änderung?

Wir müssen wissen:
1. Wann funktionierte die LED-Kette zuletzt?
2. Welche Dateien wurden seit dann geändert?
3. Wurde die Systemd-Service angepasst?

Bitte prüfe:
```bash
git log --oneline | head -20
```

Dann können wir die exakten Änderungen sehen.
