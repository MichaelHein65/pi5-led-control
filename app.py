#!/usr/bin/env python3
"""
LED Neon Control - Web-basierte Steuerung für APA102/DotStar LED-Panel
Raspberry Pi 5 - 30x10 LED Matrix
"""

from flask import Flask, render_template, jsonify, request
import time
import math
import threading
from datetime import datetime

app = Flask(__name__)

# LED Configuration
LED_WIDTH = 30
LED_HEIGHT = 10
LED_COUNT = LED_WIDTH * LED_HEIGHT
brightness = 50  # 0-100%
current_effect = "off"
static_color = [255, 0, 0]  # RGB
effect_thread = None
stop_effect = False

# Mock LED control for development/testing
class MockAPA102:
    """Mock APA102 LED strip for development without hardware"""
    def __init__(self, num_leds, clock_pin=None, data_pin=None):
        self.num_leds = num_leds
        self.pixels = [(0, 0, 0)] * num_leds
        self.brightness_value = 1.0
    
    def __setitem__(self, index, color):
        if isinstance(index, slice):
            for i in range(*index.indices(self.num_leds)):
                self.pixels[i] = color
        else:
            self.pixels[index] = color
    
    def show(self):
        pass
    
    @property
    def brightness(self):
        return self.brightness_value
    
    @brightness.setter
    def brightness(self, value):
        self.brightness_value = value

# BMP180/BMP280 Sensor mock
class MockBMP:
    """Mock BMP sensor for development without hardware"""
    @property
    def temperature(self):
        return 22.5 + (time.time() % 10) / 10
    
    @property
    def pressure(self):
        return 1013.25 + (time.time() % 20) / 20

# Try to import hardware libraries and initialize devices
try:
    import board
    import adafruit_dotstar as dotstar
    import adafruit_bmp280
    
    # Initialize APA102 LEDs
    pixels = dotstar.DotStar(board.SCK, board.MOSI, LED_COUNT, brightness=0.5, auto_write=False)
    print("Using real APA102 hardware")
    
    # Initialize BMP280 sensor
    try:
        i2c = board.I2C()
        bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
        print("Using real BMP280 sensor")
    except (OSError, RuntimeError):
        bmp = MockBMP()
        print("Using mock BMP sensor (sensor not found)")
        
except (ImportError, NotImplementedError):
    pixels = MockAPA102(LED_COUNT)
    bmp = MockBMP()
    print("Using mock APA102 and BMP sensor (development mode)")


def get_pixel_index(x, y):
    """Convert 2D coordinates to 1D pixel index for serpentine layout"""
    if y % 2 == 0:
        # Even rows go left to right
        return y * LED_WIDTH + x
    else:
        # Odd rows go right to left
        return y * LED_WIDTH + (LED_WIDTH - 1 - x)


def set_brightness(value):
    """Set global brightness (0-100)"""
    global brightness
    brightness = max(0, min(100, value))
    pixels.brightness = brightness / 100.0


def clear_leds():
    """Turn off all LEDs"""
    for i in range(LED_COUNT):
        pixels[i] = (0, 0, 0)
    pixels.show()


def hsv_to_rgb(h, s, v):
    """Convert HSV color to RGB (h: 0-360, s: 0-1, v: 0-1)"""
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


# LED Effects
def effect_rainbow():
    """Rainbow effect - cycling colors"""
    global stop_effect
    offset = 0
    while not stop_effect:
        for i in range(LED_COUNT):
            hue = (i * 360 / LED_COUNT + offset) % 360
            pixels[i] = hsv_to_rgb(hue, 1.0, 1.0)
        pixels.show()
        offset = (offset + 2) % 360
        time.sleep(0.03)


def effect_breathing():
    """Breathing effect - pulsing white light"""
    global stop_effect
    while not stop_effect:
        for i in range(100):
            if stop_effect:
                break
            intensity = int((math.sin(i * math.pi / 50) + 1) / 2 * 255)
            for j in range(LED_COUNT):
                pixels[j] = (intensity, intensity, intensity)
            pixels.show()
            time.sleep(0.02)


def effect_sine_wave():
    """Sine wave effect - wave moving across the panel"""
    global stop_effect
    offset = 0
    while not stop_effect:
        for x in range(LED_WIDTH):
            for y in range(LED_HEIGHT):
                wave = math.sin((x + offset) * math.pi / 5)
                intensity = int((wave + 1) / 2 * 255)
                hue = (x * 12 + offset * 3) % 360
                color = hsv_to_rgb(hue, 1.0, intensity / 255.0)
                pixels[get_pixel_index(x, y)] = color
        pixels.show()
        offset = (offset + 1) % 360
        time.sleep(0.05)


def effect_flash():
    """Flash effect - strobe light"""
    global stop_effect
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    idx = 0
    while not stop_effect:
        for i in range(LED_COUNT):
            pixels[i] = colors[idx]
        pixels.show()
        time.sleep(0.1)
        clear_leds()
        time.sleep(0.1)
        idx = (idx + 1) % len(colors)


def effect_diagnose():
    """Diagnose effect - test each LED individually"""
    global stop_effect
    while not stop_effect:
        for i in range(LED_COUNT):
            if stop_effect:
                break
            clear_leds()
            pixels[i] = (255, 255, 255)
            pixels.show()
            time.sleep(0.02)


def effect_clock():
    """Clock effect - shows current time with seconds ring"""
    global stop_effect
    while not stop_effect:
        now = datetime.now()
        hour = now.hour % 12
        minute = now.minute
        second = now.second
        
        clear_leds()
        
        # Hour markers (top row)
        for h in range(12):
            x = int(h * LED_WIDTH / 12)
            if x < LED_WIDTH:
                pixels[get_pixel_index(x, 0)] = (100, 100, 100)
        
        # Current hour (brighter)
        hour_x = int(hour * LED_WIDTH / 12)
        if hour_x < LED_WIDTH:
            pixels[get_pixel_index(hour_x, 0)] = (255, 0, 0)
        
        # Minute indicators (second row)
        minute_x = int(minute * LED_WIDTH / 60)
        if minute_x < LED_WIDTH:
            pixels[get_pixel_index(minute_x, 2)] = (0, 255, 0)
        
        # Second ring (outer ring)
        second_pos = int(second * LED_COUNT / 60)
        for i in range(max(0, second_pos - 2), min(LED_COUNT, second_pos + 3)):
            pixels[i] = (0, 0, 255)
        
        pixels.show()
        time.sleep(0.1)


def effect_caterpillar():
    """Caterpillar effect - moving segment"""
    global stop_effect
    length = 10
    position = 0
    while not stop_effect:
        clear_leds()
        for i in range(length):
            idx = (position + i) % LED_COUNT
            hue = (i * 360 / length) % 360
            pixels[idx] = hsv_to_rgb(hue, 1.0, 1.0)
        pixels.show()
        position = (position + 1) % LED_COUNT
        time.sleep(0.05)


def effect_sensor_display():
    """Sensor display - shows temperature and pressure as bars"""
    global stop_effect
    while not stop_effect:
        clear_leds()
        
        # Temperature (0-40°C mapped to height)
        temp = bmp.temperature
        temp_height = int((temp / 40.0) * LED_HEIGHT)
        temp_height = max(0, min(LED_HEIGHT, temp_height))
        
        # Show temperature in left half (blue to red)
        for x in range(LED_WIDTH // 2):
            for y in range(temp_height):
                ratio = y / LED_HEIGHT
                pixels[get_pixel_index(x, y)] = (int(ratio * 255), 0, int((1 - ratio) * 255))
        
        # Pressure (980-1040 hPa mapped to height)
        pressure = bmp.pressure
        pressure_height = int(((pressure - 980) / 60.0) * LED_HEIGHT)
        pressure_height = max(0, min(LED_HEIGHT, pressure_height))
        
        # Show pressure in right half (green)
        for x in range(LED_WIDTH // 2, LED_WIDTH):
            for y in range(pressure_height):
                pixels[get_pixel_index(x, y)] = (0, 255, 0)
        
        pixels.show()
        time.sleep(0.5)


def effect_gradient():
    """Gradient effect - smooth color transitions"""
    global stop_effect
    offset = 0
    while not stop_effect:
        for y in range(LED_HEIGHT):
            for x in range(LED_WIDTH):
                hue = ((x + y + offset) * 360 / (LED_WIDTH + LED_HEIGHT)) % 360
                pixels[get_pixel_index(x, y)] = hsv_to_rgb(hue, 1.0, 1.0)
        pixels.show()
        offset = (offset + 1) % 360
        time.sleep(0.05)


def effect_sparkle():
    """Sparkle effect - random twinkling LEDs"""
    global stop_effect
    import random
    while not stop_effect:
        # Fade all LEDs
        for i in range(LED_COUNT):
            r, g, b = pixels.pixels[i] if hasattr(pixels, 'pixels') else (0, 0, 0)
            pixels[i] = (int(r * 0.9), int(g * 0.9), int(b * 0.9))
        
        # Add new sparkles
        for _ in range(5):
            idx = random.randint(0, LED_COUNT - 1)
            hue = random.randint(0, 360)
            pixels[idx] = hsv_to_rgb(hue, 1.0, 1.0)
        
        pixels.show()
        time.sleep(0.05)


def effect_static_color():
    """Static color - all LEDs same color"""
    global stop_effect, static_color
    for i in range(LED_COUNT):
        pixels[i] = tuple(static_color)
    pixels.show()
    while not stop_effect:
        time.sleep(0.1)


EFFECTS = {
    "rainbow": effect_rainbow,
    "breathing": effect_breathing,
    "sine_wave": effect_sine_wave,
    "flash": effect_flash,
    "diagnose": effect_diagnose,
    "clock": effect_clock,
    "caterpillar": effect_caterpillar,
    "sensor_display": effect_sensor_display,
    "gradient": effect_gradient,
    "sparkle": effect_sparkle,
    "static": effect_static_color,
    "off": clear_leds
}


def start_effect(effect_name):
    """Start a LED effect in a background thread"""
    global effect_thread, stop_effect, current_effect
    
    # Stop current effect
    stop_effect = True
    if effect_thread and effect_thread.is_alive():
        effect_thread.join(timeout=1.0)
    
    stop_effect = False
    current_effect = effect_name
    
    if effect_name == "off":
        clear_leds()
        return
    
    if effect_name in EFFECTS:
        effect_thread = threading.Thread(target=EFFECTS[effect_name])
        effect_thread.daemon = True
        effect_thread.start()


# Flask Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/api/effects', methods=['GET'])
def get_effects():
    """Get list of available effects"""
    return jsonify({
        "effects": list(EFFECTS.keys()),
        "current": current_effect
    })


@app.route('/api/effect', methods=['POST'])
def set_effect():
    """Set current effect"""
    data = request.json
    effect_name = data.get('effect', 'off')
    
    if effect_name in EFFECTS:
        start_effect(effect_name)
        return jsonify({"success": True, "effect": effect_name})
    else:
        return jsonify({"success": False, "error": "Unknown effect"}), 400


@app.route('/api/brightness', methods=['POST'])
def set_brightness_api():
    """Set brightness level"""
    data = request.json
    value = data.get('brightness', 50)
    set_brightness(value)
    return jsonify({"success": True, "brightness": brightness})


@app.route('/api/color', methods=['POST'])
def set_color():
    """Set static color"""
    global static_color
    data = request.json
    static_color = [
        data.get('r', 255),
        data.get('g', 0),
        data.get('b', 0)
    ]
    if current_effect == "static":
        start_effect("static")
    return jsonify({"success": True, "color": static_color})


@app.route('/api/sensor', methods=['GET'])
def get_sensor_data():
    """Get sensor data (temperature and pressure)"""
    return jsonify({
        "temperature": round(bmp.temperature, 1),
        "pressure": round(bmp.pressure, 1)
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current status"""
    return jsonify({
        "effect": current_effect,
        "brightness": brightness,
        "color": static_color,
        "temperature": round(bmp.temperature, 1),
        "pressure": round(bmp.pressure, 1)
    })


if __name__ == '__main__':
    # Initialize
    set_brightness(50)
    clear_leds()
    
    # Start server
    print("🌈 LED Neon Control Server starting...")
    print(f"LED Panel: {LED_WIDTH}x{LED_HEIGHT} = {LED_COUNT} LEDs")
    app.run(host='0.0.0.0', port=5000, debug=False)
