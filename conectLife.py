import RPi.GPIO as GPIO
import time
import Adafruit_DHT
from grove.display.base import *
from grove.i2c import Bus
from grove.display.jhd1802 import JHD1802  # Asegúrate de tener esta importación correcta
from influxdb import InfluxDBClient       # Importar el cliente de InfluxDB

# Configuración de la numeración de pines
GPIO.setmode(GPIO.BCM)

# Definición del pin TRIG y ECHO combinados
TRIG_ECHO = 5  # GPIO5

# Buzzer
BUZZER_PIN = 26  # D26

# Definición del pin del botón
BUTTON_PIN = 25  # GPIO25

# Definición del pin del sensor de temperatura y humedad
DHT_SENSOR_PIN = 22  # GPIO22
DHT_SENSOR = Adafruit_DHT.DHT11  # O Adafruit_DHT.DHT22 si usas ese modelo

print("Sistema iniciado...")

# Configuración del pin
GPIO.setup(TRIG_ECHO, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN)

# Inicializar LCD
lcd = JHD1802()  # Inicializa el LCD
lcd.clear()
lcd.write("Sistema iniciado")
time.sleep(1)
lcd.clear()

ultrasonic_active = True

# Crear el cliente de InfluxDB antes del bucle principal
client = InfluxDBClient(host="localhost", port=8086, database="sensordata")

try:
    while True:
        # Verificar si el botón está presionado
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            # Detener la medición de distancia
            ultrasonic_active = False
            # Apagar el buzzer
            GPIO.output(BUZZER_PIN, False)
            print("Leyendo temperatura y humedad...")
            lcd.clear()
            lcd.write("Leyendo Temp/Hum")
            # Leer el sensor de temperatura y humedad
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_SENSOR_PIN)
            if humidity is not None and temperature is not None:
                print("****************************************")
                print("*   Temperatura: {:.1f}°C           *".format(temperature))
                print("*   Humedad: {:.1f}%               *".format(humidity))
                print("****************************************")

                # Mostrar en LCD
                lcd.clear()
                # Primera línea: temperatura
                lcd.setCursor(0,0)
                lcd.write("Temp:{:.1f}C".format(temperature))
                # Segunda línea: humedad
                lcd.setCursor(1,0)
                lcd.write("Hum:{:.1f}%".format(humidity))

                # Enviar datos a InfluxDB (temperatura y humedad)
                json_body = [
                    {
                        "measurement": "sensores",
                        "tags": {
                            "sensor": "dht11"
                        },
                        "fields": {
                            "temperature": float(temperature),
                            "humidity": float(humidity)
                        }
                    }
                ]
                client.write_points(json_body)

            else:
                print("Error al leer el sensor de temperatura y humedad.")
                lcd.clear()
                lcd.write("Error Temp/Hum")

            # Esperar un tiempo antes de volver a activar el sensor ultrasónico
            time.sleep(2)
            # Reactivar la medición de distancia
            ultrasonic_active = True

            # Esperar a que se suelte el botón antes de continuar
            while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                pass

        if ultrasonic_active:
            # Asegurarse de que el pin está en bajo
            GPIO.output(TRIG_ECHO, False)
            time.sleep(0.5)
            GPIO.output(TRIG_ECHO, True)
            time.sleep(0.00001)  # Pulso de 10 microsegundos
            GPIO.output(TRIG_ECHO, False)
            # Cambiar el pin a entrada para recibir el eco
            GPIO.setup(TRIG_ECHO, GPIO.IN)
            # Medir el tiempo de inicio y fin del pulso ECHO
            pulse_start = time.time()
            timeout_start = time.time()
            while GPIO.input(TRIG_ECHO) == 0:
                pulse_start = time.time()
                if pulse_start - timeout_start > 0.02:
                    print("Tiempo de espera excedido al iniciar la medición")
                    break
            pulse_end = time.time()
            timeout_end = time.time()
            while GPIO.input(TRIG_ECHO) == 1:
                pulse_end = time.time()
                if pulse_end - timeout_end > 0.02:
                    print("Tiempo de espera excedido al finalizar la medición")
                    break
            # Calcular duración del pulso
            pulse_duration = pulse_end - pulse_start
            # Calcular distancia
            distance = pulse_duration * 17150
            distance = round(distance, 2)

            # Limpiar LCD antes de mostrar nuevos datos
            lcd.clear()

            if 0 < distance < 500:
                print("Distancia: {} cm".format(distance))
                lcd.setCursor(0,0)
                lcd.write("Dist: {}cm".format(distance))

                # Enviar datos a InfluxDB (distancia)
                json_body = [
                    {
                        "measurement": "sensores",
                        "tags": {
                            "sensor": "ultrasonico"
                        },
                        "fields": {
                            "distance_cm": float(distance)
                        }
                    }
                ]
                client.write_points(json_body)

                if distance <= 10:
                    GPIO.output(BUZZER_PIN, True)
                    print("¡ALERTA! INTRUSO CERCA >:(")
                    lcd.setCursor(1,0)
                    lcd.write("ALERTA INTRUSO!")
                else:
                    GPIO.output(BUZZER_PIN, False)
            else:
                print("Nadie detectado")
                lcd.setCursor(0,0)
                lcd.write("Nadie detectado")
                GPIO.output(BUZZER_PIN, False)

            # Volver a configurar el pin como salida
            GPIO.setup(TRIG_ECHO, GPIO.OUT)
            GPIO.output(TRIG_ECHO, False)

            time.sleep(1)

except KeyboardInterrupt:
    # Limpiar configuración GPIO al terminar
    GPIO.output(BUZZER_PIN, False)
    GPIO.cleanup()
    print("Sistema detenido por el usuario.")
    lcd.clear()
    lcd.write("Sistema detenido")

except Exception as e:
    GPIO.cleanup()
    print("Ha ocurrido un error:", e)
    lcd.clear()
    lcd.write("Error en sistema")
