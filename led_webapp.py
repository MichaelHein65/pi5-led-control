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
import threading, time, math, colorsys, datetime, os
import board, adafruit_dotstar
import requests  # Füge zu den Imports hinzu

# ===================================================================
#   P A N E L - K O N S T A N T E N
# ===================================================================
PANEL_WIDTH  = 30
PANEL_HEIGHT = 10
NUM_LEDS     = PANEL_WIDTH * PANEL_HEIGHT

brightness   = 0.3
static_color = (255, 0, 0)

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
#   LED - INIT
# ===================================================================
leds = adafruit_dotstar.DotStar(
    board.SCK, board.MOSI, NUM_LEDS,
    brightness=brightness, auto_write=False
)
led_lock = Lock()
stop_event = threading.Event()

# LED Status Cache für Web-Vorschau
led_state_cache = [(0, 0, 0)] * NUM_LEDS

# ===================================================================
#   L E D   S H O W   W R A P P E R
# ===================================================================
def update_leds():
    """LEDs anzeigen und Status für Web-Vorschau cachen"""
    global led_state_cache
    led_state_cache = [tuple(leds[i]) for i in range(NUM_LEDS)]
    leds.show()

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
}
color_map = {' ': (20,0,0), 'W': (255,255,255), 'B': (200,200,20)}

# ===================================================================
#   B U C H S T A B E N - P A T T E R N S   (5x6 Pixel)
# ===================================================================
letter_patterns = {
    'A': ["  W  "," W W ","W   W","WWWWW","W   W","W   W"],
    'B': ["WWWW ","W   W","WWWW ","W   W","W   W","WWWW "],
    'C': [" WWWW","W    ","W    ","W    ","W    "," WWWW"],
    'D': ["WWWW ","W   W","W   W","W   W","W   W","WWWW "],
    'E': ["WWWWW","W    ","WWWW ","W    ","W    ","WWWWW"],
    'F': ["WWWWW","W    ","WWWW ","W    ","W    ","W    "],
    'G': [" WWWW","W    ","W  WW","W   W","W   W"," WWW "],
    'H': ["W   W","W   W","WWWWW","W   W","W   W","W   W"],
    'I': [" WWW ","  W  ","  W  ","  W  ","  W  "," WWW "],
    'J': ["  WWW","   W ","   W ","   W ","W  W "," WW  "],
    'K': ["W   W","W  W ","WWW  ","W  W ","W   W","W   W"],
    'L': ["W    ","W    ","W    ","W    ","W    ","WWWWW"],
    'M': ["W   W","WW WW","W W W","W   W","W   W","W   W"],
    'N': ["W   W","WW  W","W W W","W  WW","W   W","W   W"],
    'O': [" WWW ","W   W","W   W","W   W","W   W"," WWW "],
    'P': ["WWWW ","W   W","WWWW ","W    ","W    ","W    "],
    'Q': [" WWW ","W   W","W   W","W W W","W  W "," WW W"],
    'R': ["WWWW ","W   W","WWWW ","W  W ","W   W","W   W"],
    'S': [" WWWW","W    "," WWW ","    W","    W","WWWW "],
    'T': ["WWWWW","  W  ","  W  ","  W  ","  W  ","  W  "],
    'U': ["W   W","W   W","W   W","W   W","W   W"," WWW "],
    'V': ["W   W","W   W","W   W"," W W "," W W ","  W  "],
    'W': ["W   W","W   W","W   W","W W W","WW WW","W   W"],
    'X': ["W   W"," W W ","  W  ","  W  "," W W ","W   W"],
    'Y': ["W   W"," W W ","  W  ","  W  ","  W  ","  W  "],
    'Z': ["WWWWW","   W ","  W  "," W   ","W    ","WWWWW"],
    'Ä': [" W W ","     "," WWW ","W   W","WWWWW","W   W"],
    'Ö': [" W W ","     "," WWW ","W   W","W   W"," WWW "],
    'Ü': [" W W ","     ","W   W","W   W","W   W"," WWW "],
    'ß': [" WW  ","W  W ","W WW ","W   W","W   W","W WW "],
    ' ': ["     ","     ","     ","     ","     ","     "],
    '!': ["  W  ","  W  ","  W  ","  W  ","     ","  W  "],
    '?': [" WWW ","W   W","   W ","  W  ","     ","  W  "],
    '.': ["     ","     ","     ","     ","     ","  W  "],
    '-': ["     ","     ","WWWWW","     ","     ","     "],
    ',': ["     ","     ","     ","     ","  W  "," W   "],
    ':': ["     ","  W  ","     ","     ","  W  ","     "],
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
}

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

# ===================================================================
#   W E I T E R E   E F F E K T E
# ===================================================================
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

def run_rainbow_wave_effect():
    print(">> Effekt 3b: Rainbow Wave gestartet")
    off=0
    try:
        while not stop_event.is_set():
            with led_lock:
                for i in range(NUM_LEDS):
                    sine=(math.sin((i+off)*0.2)+1)/2
                    hue=(off*0.005+sine*0.1)%1.0  # Durchlaufe alle Farben des Regenbogens - langsamer
                    r,g,b=[int(c*255*brightness) for c in colorsys.hsv_to_rgb(hue,1,1)]
                    leds[i]=(r,g,b)
                update_leds()
            off+=1
            time.sleep(0.05)
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

# ===================================================================
#   L A U F S C H R I F T   E F F E K T
# ===================================================================
scroll_text = ""
scroll_speed = 5
scroll_hue = 0.5

def text_to_bitmap(text):
    """Konvertiert Text zu einer Bitmap (Liste von Spalten)"""
    bitmap = []
    for char in text:
        pattern = letter_patterns.get(char, letter_patterns.get(' '))
        char_width = len(pattern[0])
        for col in range(char_width):
            column = []
            for row in range(6):
                column.append(pattern[row][col] if col < len(pattern[row]) else ' ')
            bitmap.append(column)
        bitmap.append([' '] * 6)  # Leerzeichen zwischen Buchstaben
    return bitmap

def run_scrolltext_effect(max_loops=0):
    """Laufschrift-Effekt. max_loops=0 bedeutet unendlich."""
    global scroll_text, scroll_speed, scroll_hue
    print(f">> Laufschrift gestartet: '{scroll_text}' (loops: {'∞' if max_loops == 0 else max_loops})")
    
    bitmap = text_to_bitmap(scroll_text)
    bitmap = bitmap[::-1]
    total_width = len(bitmap)
    offset = -total_width
    
    delay = 0.1 - (scroll_speed - 1) * 0.008
    text_color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(scroll_hue, 1, brightness))
    bg_color = (0, 0, 0)
    
    loop_count = 0
    
    try:
        while not stop_event.is_set():
            with led_lock:
                for i in range(NUM_LEDS):
                    leds[i] = bg_color
                
                for bx, column in enumerate(bitmap):
                    screen_x = PANEL_WIDTH - 1 - (bx + offset)
                    if 0 <= screen_x < PANEL_WIDTH:
                        for row, pixel in enumerate(column):
                            screen_y = 2 + row
                            if 0 <= screen_y < PANEL_HEIGHT and pixel == 'W':
                                idx = xy_to_index(screen_x, screen_y)
                                leds[idx] = text_color
                
                update_leds()
            
            offset += 1
            if offset > PANEL_WIDTH:
                offset = -total_width
                loop_count += 1
                if max_loops > 0 and loop_count >= max_loops:
                    break
            
            time.sleep(delay)
    finally:
        leds.auto_write = True

# ===================================================================
#   W E T T E R   A B R U F
# ===================================================================
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
WEATHER_CITY = "Rodgau,DE"

def get_weather_text():
    """Holt aktuelles Wetter für Rodgau und formatiert als Laufschrift"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={WEATHER_CITY}&appid={OPENWEATHER_API_KEY}&units=metric&lang=de"
        res = requests.get(url, timeout=10)
        data = res.json()
        
        if res.status_code != 200:
            return "WETTER NICHT VERFÜGBAR", 0.5
        
        temp = round(data['main']['temp'])
        desc = data['weather'][0]['description'].upper()
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']  # Luftdruck in hPa
        
        # Umlaute ersetzen für LED-Anzeige
        desc = desc.replace('Ä', 'AE').replace('Ö', 'OE').replace('Ü', 'UE').replace('ß', 'SS')
        
        # Farbe basierend auf Temperatur (blau=kalt, grün=mild, rot=heiß)
        # -10°C = 0.66 (blau), 15°C = 0.33 (grün), 35°C = 0.0 (rot)
        temp_hue = max(0.0, min(0.66, 0.66 - (temp + 10) / 45 * 0.66))
        
        return f"RODGAU: {temp} GRAD - {desc} - {humidity}% FEUCHTE - {pressure} HPA", temp_hue
    except Exception as e:
        print(f"Wetter-Fehler: {e}")
        return "WETTER NICHT VERFÜGBAR", 0.5

def check_weather_time():
    """Prüft ob es x:55 Uhr ist und zeigt Wettermeldung"""
    global effect_thread, scroll_text, scroll_speed, scroll_hue
    
    last_weather_hour = -1
    
    while True:
        now = datetime.datetime.now()
        
        if now.minute == 55 and now.hour != last_weather_hour:
            last_weather_hour = now.hour
            
            weather_text, temp_hue = get_weather_text()
            print(f">> Wettermeldung: {weather_text}")
            
            scroll_text = weather_text
            scroll_speed = 10
            scroll_hue = temp_hue
            
            def weather_then_clock():
                global effect_thread
                run_scrolltext_effect(max_loops=2)  # Wetter: nur 2x
                time.sleep(0.1)
                if not stop_event.is_set():
                    leds.auto_write = False
                    run_clock_effect()
            
            with led_lock:
                stop_current_effect()
                leds.auto_write = False
            effect_thread = threading.Thread(target=weather_then_clock)
            effect_thread.start()
        
        time.sleep(30)

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
        7:run_rainbow_wave_effect,
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

@app.route('/led_status')
def led_status():
    """LED Status für Web-Vorschau"""
    return jsonify(leds=led_state_cache)

@app.route('/ledcontrol/<path:fname>')
def ui(fname): return send_from_directory('/home/pi/ledcontrol',fname)

@app.route('/ledcontrol/')
def ui_index(): return send_from_directory('/home/pi/ledcontrol','index.html')

@app.route('/scrolltext', methods=['POST'])
def start_scrolltext():
    global effect_thread, scroll_text, scroll_speed, scroll_hue
    data = request.get_json()
    scroll_text = data.get('text', 'HALLO')
    scroll_speed = data.get('speed', 5)
    scroll_hue = data.get('hue', 0.5)
    
    with led_lock:
        stop_current_effect()
        leds.auto_write = False
        effect_thread = threading.Thread(target=run_scrolltext_effect, args=(0,))  # 0 = unendlich
        effect_thread.start()
    return jsonify(success=True)

@app.route('/test_weather', methods=['POST'])
def test_weather():
    """Test-Endpoint für Wettermeldung"""
    global effect_thread, scroll_text, scroll_speed, scroll_hue
    
    weather_text, temp_hue = get_weather_text()
    print(f">> TEST Wettermeldung: {weather_text} (hue: {temp_hue})")
    
    scroll_text = weather_text
    scroll_speed = 10
    scroll_hue = temp_hue
    
    def weather_then_clock():
        global effect_thread
        run_scrolltext_effect(max_loops=2)  # Wetter: nur 2x
        time.sleep(0.1)
        if not stop_event.is_set():
            leds.auto_write = False
            run_clock_effect()
    
    with led_lock:
        stop_current_effect()
        leds.auto_write = False
    effect_thread = threading.Thread(target=weather_then_clock)
    effect_thread.start()
    
    return jsonify(success=True, text=weather_text, hue=temp_hue)

# ===================================================================
#   M A I N
# ===================================================================
if __name__ == '__main__':
    # Starte Wetter-Check im Hintergrund
    weather_thread = threading.Thread(target=check_weather_time, daemon=True)
    weather_thread.start()
    
    app.run(host='0.0.0.0', port=5050)
