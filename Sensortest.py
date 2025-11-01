import time
import board
import busio
import bmp180
# oder:
# import circuitpython_bmp180

# I2C initialisieren
i2c = busio.I2C(board.SCL, board.SDA)

# BMP180 initialisieren
sensor = bmp180.BMP180(i2c)

# Messergebnisse ausgeben
while True:
    print(f"Temperatur: {sensor.temperature:.2f} °C")
    print(f"Luftdruck: {sensor.pressure:.2f} hPa")
    time.sleep(2)
