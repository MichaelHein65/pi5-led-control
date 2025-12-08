#!/bin/bash
cd /home/pi/ledcontrol

# Lade Umgebungsvariablen aus .env wenn vorhanden
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

source /home/pi/led-venv/bin/activate
python led_webapp.py
