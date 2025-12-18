# LED Control Copilot Instructions

## Architecture Overview

This is a Flask-based web controller for a 30×10 APA102/DotStar LED matrix (300 LEDs) on Raspberry Pi 5, with real-time web visualization and BMP180 sensor integration.

**Key Components:**
- `led_webapp.py` - Flask backend with threaded LED effects
- `index.html` - Responsive web UI with live LED preview canvas
- Hardware: SPI LEDs (GPIO10/11), I2C sensor (GPIO2/3)

## Critical Patterns

### LED Coordinate System
Uses **snake-pattern mapping** where even columns go top-to-bottom, odd columns bottom-to-top:
```python
xy_to_index(x, y)  # Converts 2D coords to 1D LED strip index
apply_rotation()    # Applies rotate_x/y/z transforms (lines 7-9)
```

### Thread-Safe LED Updates
**Always use `update_leds()` instead of `leds.show()`** - this wrapper:
1. Caches LED state for web preview (`led_state_cache`)
2. Ensures thread-safe access via `led_lock`
3. Powers the `/led_status` endpoint for canvas visualization

### Effect Threading Pattern
All effects follow this structure:
```python
def run_effect():
    try:
        while not stop_event.is_set():
            with led_lock:
                # Modify leds[i] = (r, g, b)
                update_leds()  # NOT leds.show()
            time.sleep(delay)
    finally:
        leds.auto_write = True
```

## Development Workflow

### Local Development → Pi Deployment
```bash
# On Mac - edit files locally, then deploy:
scp led_webapp.py index.html pi5:/home/pi/ledcontrol/

# On Pi - restart server:
ssh pi5
sudo systemctl stop ledserver.service  # Stop existing service
cd /home/pi/ledcontrol
source /home/pi/led-venv/bin/activate  # Critical: venv has Flask, board libs
python led_webapp.py
```

### Testing LED Effects
```bash
# Start effect via API:
curl -X POST http://100.66.12.52:5050/effect/0  # 0=rainbow, 1=breathing, etc.

# Check live LED state:
curl http://100.66.12.52:5050/led_status | head -c 300
```

## Project-Specific Conventions

### Rotation Configuration (lines 7-9)
Adjust physical LED orientation without rewiring:
```python
rotate_x = False  # Flip vertical
rotate_y = True   # Flip horizontal  
rotate_z = True   # 180° rotation
```

### Effect Mapping (index.html line ~126)
Effect titles in `effectTitles[]` map to backend functions via index:
- 0: `run_rainbow_effect` → "rainbow" button
- 5: `run_clock_effect` → "clock" button

### Web Preview Architecture
- Frontend polls `/led_status` every 100ms (index.html line ~236)
- Canvas renders 30×10 grid with same snake-pattern mapping
- `led_state_cache` updated atomically in `update_leds()`

## Common Pitfalls

1. **Forgetting venv**: Flask won't start without `source /home/pi/led-venv/bin/activate`
2. **Port conflicts**: Use `sudo fuser -k 5050/tcp` if "Address already in use"
3. **Missing viewport meta**: Without `<meta name="viewport">`, mobile shows desktop layout
4. **Direct `leds.show()` calls**: Breaks web preview - always use `update_leds()`

## Key Files

- `led_webapp.py` lines 85-101: Core `update_leds()` wrapper
- `led_webapp.py` lines 120-310: Effect implementations (rainbow, clock, etc.)
- `index.html` lines 219-243: Canvas rendering and polling logic
- `start_led_server.sh`: Production startup script for systemd

## Hardware Dependencies

Dependencies only available on Pi (not Mac):
- `board`, `adafruit_dotstar`, `busio`, `bmp180`
- Imports will fail locally - development requires Pi for testing
