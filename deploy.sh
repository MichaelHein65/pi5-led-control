#!/bin/bash
# LED WebApp Test & Deploy Script

echo "========================================="
echo "LED WebApp - Test & Deploy"
echo "========================================="

# 1. Syntax prüfen
echo -e "\n[1/4] Syntax-Überprüfung..."
python3 -m py_compile led_webapp.py
if [ $? -eq 0 ]; then
    echo "✓ Syntax OK"
else
    echo "✗ FEHLER: Syntax-Fehler in led_webapp.py"
    exit 1
fi

# 2. Auf Pi testen
echo -e "\n[2/4] Kopiere Datei auf Pi..."
scp led_webapp.py pi5:/home/pi/ledcontrol/led_webapp.py
if [ $? -eq 0 ]; then
    echo "✓ Datei auf Pi kopiert"
else
    echo "✗ FEHLER: Konnte nicht auf Pi kopieren"
    exit 1
fi

# 3. Service neu starten
echo -e "\n[3/4] Starte Service auf Pi neu..."
ssh pi5 "
    echo 'Stoppe LED-Service...'
    sudo systemctl stop ledserver.service
    sleep 2
    
    echo 'Starte LED-Service...'
    sudo systemctl start ledserver.service
    sleep 2
    
    echo 'Überprüfe Service-Status...'
    sudo systemctl status ledserver.service --no-pager
"

# 4. Test-API-Call
echo -e "\n[4/4] Teste API..."
sleep 2
curl -X POST http://100.66.12.52:5050/effect/0
if [ $? -eq 0 ]; then
    echo -e "\n✓ API antwortet!"
else
    echo -e "\n✗ API antwortet nicht"
fi

echo -e "\n========================================="
echo "✓ Deploy abgeschlossen"
echo "========================================="
