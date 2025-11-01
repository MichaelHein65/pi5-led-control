#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ===================================================================
#   D R E H - S C H A L T E R   (einfach True / False setzen)
# ===================================================================
rotate_x = False   # oben ↔ unten spiegeln
rotate_y = True    # links ↔ rechts spiegeln
rotate_z = True    # 180-Grad-Drehung (beide Achsen zugleich)

# ===================================================================
#   I M P O R T E
# ===================================================================
from flask import Flask, request, jsonify, send_from_directory
from threading import Lock
import threading, time, math, colorsys, datetime
import board, adafruit_dotstar
import busio
import bmp180

# ===================================================================
#   S E N S O R   I N I T I A L I S I E R U N G
# ===================================================================
i2c = busio.I2C(board.SCL, board.SDA)
sensor = bmp180.BMP180(i2c)
sensor.sea_level_pressure = 1013.25

temperature = 0.0
pressure = 0.0

def sensor_loop():
    global temperature, pressure
    while True:
        try:
            temperature = sensor.temperature
            pressure = sensor.pressure * 100
        except Exception as e:
            print("Sensorfehler:", e)
        time.sleep(5)

threading.Thread(target=sensor_loop, daemon=True).start()

# ===================================================================
#   P A N E L - K O N S T A N T E N
# ===================================================================
PANEL_WIDTH  = 30
PANEL_HEIGHT = 10
NUM_LEDS     = PANEL_WIDTH * PANEL_HEIGHT

brightness   = 0.3
static_color = (255, 0, 0)

# LED Status Cache für Web-Vorschau
led_state_cache = [(0, 0, 0)] * NUM_LEDS

# ===================================================================
#   B A S I S - S N A K E - M A P P I N G   (ohne Drehung!)
# ===================================================================
def xy_to_index_unrotated(x: int, y: int) -> int:
    if x % 2 == 0:
        return x * PANEL_HEIGHT + y
    else:
        return x * PANEL_HEIGHT + (PANEL_HEIGHT - 1 - y)

# ===================================================================
#   D R E H - L O G I K
# ===================================================================
def apply_rotation(x: int, y: int) -> tuple[int, int]:
    if rotate_z:
        x = PANEL_WIDTH - 1 - x
        y = PANEL_HEIGHT - 1 - y
    if rotate_y:
        x = PANEL_WIDTH - 1 - x
    if rotate_x:
        y = PANEL_HEIGHT - 1 - y
    return x, y

def xy_to_index(x: int, y: int) -> int:
    rx, ry = apply_rotation(x, y)
    return xy_to_index_unrotated(rx, ry)

# ===================================================================
#   L E D   S H O W   W R A P P E R
# ===================================================================
def update_leds():
    """LEDs anzeigen und Status für Web-Vorschau cachen"""
    global led_state_cache
    with led_lock:
        led_state_cache = [tuple(leds[i]) for i in range(NUM_LEDS)]
        update_leds()

# ===================================================================
#   LED - INIT
# ===================================================================
leds = adafruit_dotstar.DotStar(
    board.SCK, board.MOSI, NUM_LEDS,
    brightness=brightness, auto_write=False
)
led_lock = Lock()
stop_event = threading.Event()

# ===================================================================
#   Z I F F E R N - P A T T E R N S   &   F A R B E N
# ===================================================================
digit_patterns = {
    '0': [" WWW ","W   W","W   W","W   W","W   W"," WWW "],
    '1': ["  W  "," WW  ","  W  ","  W  ","  W  "," WWW "],
    '2': [" WWW ","W   W","   W ","  W  "," W   ","WWWWW"],
    '3': [" WWW ","W   W","   W ","  WW ","W   W"," WWW "],
    '4': ["   W ","  WW "," W W ","W  W ","WWWWW","   W "],
    '5': ["WWWWW","W    ","WWWW ","    W","W   W"," WWW "],
    '6': [" WWW ","W    ","WWWW ","W   W","W   W"," WWW "],
    '7': ["WWWWW","    W","   W ","  W  "," W   ","W    "],
    '8': [" WWW ","W   W"," WWW ","W   W","W   W"," WWW "],
    '9': [" WWW ","W   W","W   W"," WWWW","    W"," WWW "],
    ':': [" B "," B ","BBB","BBB"," B "," B "],
    '.' : ["  ", "  ", "  ", "  ", " W", " W"],
    '°' : ["    ", ".  .", " . ", "    ", "    ", "    "],
    'C' : [" .. ", ".  ", ".   ", ".  ", " .. "],
    'h' : [".   ", ".   ", "... ", ".  .", ".  ."],
    'P' : ["... ", ".  .", "... ", ".   ", ".   "],
    'a' : ["    ", " .. ", "   .", " ...", ".  ."]
}
color_map = {' ': (20,0,0), 'W': (255,255,255), 'B': (200,200,20)}

# ===================================================================
#   U H R - E F F E K T
# ===================================================================
def get_outer_ring_leds():
    return (
        [(x,0) for x in range(PANEL_WIDTH)] +
        [(PANEL_WIDTH-1,y) for y in range(1,PANEL_HEIGHT)] +
        [(x,PANEL_HEIGHT-1) for x in reversed(range(PANEL_WIDTH-1))] +
        [(0,y) for y in reversed(range(1,PANEL_HEIGHT-1))]
    )

def show_clock():
    now      = datetime.datetime.now()
    time_str = f"{now.hour:02}:{now.minute:02}"

    start_y  = 2
    total_w  = sum(len(digit_patterns[c][0]) + 1 for c in time_str) - 1
    start_x  = (PANEL_WIDTH - total_w) // 2

    with led_lock:
        # Für Test: alle 5 Minuten in den ersten 20 s Regenbogen
        if now.minute % 30 == 0 and now.second < 20:
            for j in range(NUM_LEDS):
                hue = (j / NUM_LEDS + time.time() * 0.1) % 1.0
                r, g, b = [int(c * 255 * 0.5) for c in colorsys.hsv_to_rgb(hue, 1, 1)]
                leds[j] = (r, g, b)
        else:
            # Hintergrund
            for i in range(NUM_LEDS):
                leds[i] = color_map[' ']

        # Ziffern zeichnen (korrekte Orientierung)
        off_x = start_x
        for ch in time_str:
            # für jede Zeile (Row)
            for row, col_str in enumerate(digit_patterns[ch]):
                for col, bit in enumerate(col_str):
                    if bit != ' ':
                        idx = xy_to_index(off_x + col, start_y + row)
                        leds[idx] = color_map[bit]
            off_x += len(digit_patterns[ch][0]) + 1

        # Sekundenring
        ring   = get_outer_ring_leds()
        pos    = (now.second + now.microsecond/1e6) / 60 * len(ring)
        snake  = 10
        for i in range(snake):
            ox, oy = ring[int((pos + i) % len(ring))]
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(i / snake, 1, 1)]
            idx     = xy_to_index(ox, oy)
            leds[idx] = (r, g, b)

        # LED-Buffer anzeigen
        update_leds()


def run_clock_effect():
    print(">> Effekt 5: Uhr gestartet")
    try:
        while not stop_event.is_set():
            show_clock()
            time.sleep(0.05)
    finally:
        leds.auto_write = True


def run_rainbow_effect():
    print(">> Effekt 1: Rainbow gestartet")
    try:
        while not stop_event.is_set():
            with led_lock:
                for j in range(NUM_LEDS):
                    hue = (j/NUM_LEDS + time.time()*0.1)%1.0
                    leds[j] = tuple(int(c*255) for c in colorsys.hsv_to_rgb(hue,1,1))
                update_leds()
            time.sleep(0.02)
    finally:
        leds.auto_write = True

def run_rainbow_effect():
    print(">> Effekt 1: Rainbow gestartet")
    try:
        while not stop_event.is_set():
            with led_lock:
                for j in range(NUM_LEDS):
                    hue = (j/NUM_LEDS + time.time()*0.1)%1.0
                    leds[j] = tuple(int(c*255) for c in colorsys.hsv_to_rgb(hue,1,1))
                update_leds()
            time.sleep(0.02)
    finally:
        leds.auto_write = True

def run_breathing_effect():
    print(">> Effekt 2: Atemlicht gestartet")
    step=0
    try:
        while not stop_event.is_set():
            val=int(((math.sin(step)+1)/2)*255*brightness)
            with led_lock:
                for i in range(NUM_LEDS): leds[i]=(val,val,val)
                update_leds()
            step+=0.1
            time.sleep(0.02)
    finally:
        leds.auto_write = True

def run_sine_wave_effect():
    print(">> Effekt 3: Sinuswelle gestartet")
    off=0
    try:
        while not stop_event.is_set():
            with led_lock:
                for i in range(NUM_LEDS):
                    sine=(math.sin((i+off)*0.2)+1)/2
                    hue=(0.55+0.15*sine)%1
                    r,g,b=[int(c*255*brightness) for c in colorsys.hsv_to_rgb(hue,1,1)]
                    leds[i]=(r,g,b)
                update_leds()
            off+=1
            time.sleep(0.03)
    finally:
        leds.auto_write = True

def run_flash_effect():
    print(">> Effekt 4: Flash gestartet")
    cols=[(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255)]
    try:
        while not stop_event.is_set():
            for c in cols:
                if stop_event.is_set(): break
                with led_lock:
                    for i in range(NUM_LEDS): leds[i]=c
                    update_leds()
                time.sleep(0.2)
    finally:
        leds.auto_write = True

def run_diagnose_effect():
    print(">> Diagnose gestartet")
    try:
        with led_lock:
            while not stop_event.is_set():
                for i in range(NUM_LEDS):
                    if stop_event.is_set(): break
                    for j in range(NUM_LEDS): leds[j]=(0,0,0)
                    leds[i]=(255,255,255); update_leds()
                    time.sleep(0.02)
                break
    finally:
        with led_lock:
            for i in range(NUM_LEDS): leds[i]=(0,0,0)
            update_leds()
        leds.auto_write = True

def run_rainbow_caterpillar():
    print(">> Effekt 7: Regenbogen-Raupe gestartet")
    from random import choice, random
    speed=0.1; turn_interval=0.5; max_len=15
    bg=(0,30,0)
    dir=(1,0); x,y=PANEL_WIDTH//2, PANEL_HEIGHT//2
    body=[]; last=time.time()

    def new_dir(cur):
        opts=[(1,0),(-1,0),(0,1),(0,-1)]
        opts.remove((-cur[0],-cur[1])); return choice(opts)

    try:
        while not stop_event.is_set():
            if time.time()-last>turn_interval+random()*turn_interval:
                dir=new_dir(dir); last=time.time()
            x=(x+dir[0])%PANEL_WIDTH
            y=(y+dir[1])%PANEL_HEIGHT
            body.append((x,y));
            if len(body)>max_len: body.pop(0)

            with led_lock:
                for i in range(NUM_LEDS): leds[i]=bg
                for i,(cx,cy) in enumerate(body):
                    hue=(i/max_len+time.time()*0.2)%1
                    r,g,b=[int(c*255) for c in colorsys.hsv_to_rgb(hue,1,1)]
                    leds[xy_to_index(cx,cy)]=(r,g,b)
                update_leds()
            time.sleep(speed)
    finally:
        leds.auto_write = True
# Neue Funktion für Effekt 8

def run_sensor_display():
    print(">> Effekt 8: Temperatur & Druck (wechselnd)")
    show_temp = True
    try:
        while not stop_event.is_set():
            with led_lock:
                leds.fill((0, 0, 10)) if show_temp else leds.fill((10, 10, 0))

                text = f"{temperature:.1f} °C" if show_temp else f"{(pressure/100):.0f} hPa"
                color = (255, 255, 0) if show_temp else (0, 200, 255)

                x_offset = 2
                for i, ch in enumerate(text):
                    pattern = digit_patterns.get(ch, ["     "]*6)
                    for pr, rowdata in enumerate(pattern):
                        for pc, pixel in enumerate(rowdata):
                            if pixel != ' ':
                                x = x_offset + i*6 + pc
                                y = 2 + pr  # vertikal etwas mittiger
                                if 0 <= x < PANEL_WIDTH and 0 <= y < PANEL_HEIGHT:
                                    leds[xy_to_index(x, y)] = color

                update_leds()

            time.sleep(1)
            if int(time.time()) % 10 == 0:
                show_temp = not show_temp
    finally:
        leds.auto_write = True

# ===================================================================
#   F L A S K  +  T H R E A D - C O N T R O L
# ===================================================================
app = Flask(__name__)
led_lock = Lock()
stop_event = threading.Event()
effect_thread = None

def stop_current_effect():
    stop_event.set()
    if effect_thread and effect_thread.is_alive():
        effect_thread.join(timeout=1)
    stop_event.clear()

@app.route('/effect/<int:idx>', methods=['POST'])
def start_effect(idx):
    global effect_thread
    mapping={
        0:run_rainbow_effect,
        1:run_breathing_effect,
        2:run_sine_wave_effect,
        3:run_flash_effect,
        4:run_diagnose_effect,
        5:run_clock_effect,
        6:run_rainbow_caterpillar,
        7:run_sensor_display,
    }
    if idx not in mapping:
        return jsonify(success=False,error="Unbekannter Effekt")
    with led_lock:
        stop_current_effect()
        leds.auto_write=False
        effect_thread=threading.Thread(target=mapping[idx]); effect_thread.start()
    return jsonify(success=True)

@app.route('/off', methods=['POST'])
def off():
    with led_lock:
        stop_current_effect()
        for i in range(NUM_LEDS): leds[i]=(0,0,0)
        update_leds()
    return jsonify(success=True)

@app.route('/static_color',methods=['POST'])
def set_static_color():
    global static_color
    h=float(request.get_json().get('hue',0.0))
    static_color=tuple(int(c*255) for c in colorsys.hsv_to_rgb(h,1,brightness))
    return jsonify(success=True)

@app.route('/static_on',methods=['POST'])
def static_on():
    with led_lock:
        stop_current_effect()
        for i in range(NUM_LEDS): leds[i]=static_color
        update_leds()
    return jsonify(success=True)

@app.route('/brightness',methods=['POST'])
def set_brightness():
    global brightness
    val=float(request.get_json().get('value',0.5))
    with led_lock:
        brightness=max(0.1,min(1.0,val))
        leds.brightness=brightness
    return jsonify(success=True,value=brightness)

@app.route('/ledcontrol/<path:fname>')
def ui(fname): return send_from_directory('/home/pi/ledcontrol',fname)

@app.route('/ledcontrol/')
def ui_index(): return send_from_directory('/home/pi/ledcontrol','index.html')

@app.route('/led_status')
def led_status():
    """LED Status für Web-Vorschau"""
    return jsonify(leds=led_state_cache)

# ===================================================================
#   M A I N
# ===================================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
