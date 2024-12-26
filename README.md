# IoT Connect Life

This project runs on a Raspberry Pi and integrates:

- A DHT11 temperature and humidity sensor
- An ultrasonic distance sensor
- A buzzer and an LCD display
- Data logging to InfluxDB
- Data visualization through Grafana

## Features

1. **Distance Detection**: The ultrasonic sensor measures distance. If a certain threshold is reached, a buzzer and on-screen alert will trigger.
2. **Temperature & Humidity**: The DHT11 sensor records temperature and humidity.
3. **LCD Display**: Shows real-time readings (distance, temperature, humidity) and system messages.
4. **InfluxDB**: Stores sensor data (distance, temperature, humidity) as time-series.
5. **Grafana Dashboards**: Visualizes data from InfluxDB in customizable charts.

---

## Hardware Requirements

- **Raspberry Pi** (e.g., Raspberry Pi 3, 4, etc.)
- **Ultrasonic Sensor** (HC-SR04 or similar; wired to GPIO)
- **DHT11** (or DHT22) temperature/humidity sensor
- **Buzzer** (wired to GPIO pin)
- **LCD Display** (I2C or Grove-based LCD)
- **Network Connection** (for installing packages and using Grafana)

---

## Software Requirements

- **Raspberry Pi OS (Debian-based)**
- **Python 3**
- **InfluxDB (v1.x)**
- **Grafana**
- Python libraries:
  - `RPi.GPIO`
  - `Adafruit_DHT`
  - `influxdb`
  - `grove.py` (if using Grove libraries)

Make sure to enable I2C on your Raspberry Pi (if you use an I2C-based LCD).

---

## Installation

### 1. Update Raspberry Pi
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python Dependencies

```bash
sudo apt install python3-pip -y
pip3 install Adafruit_DHT influxdb
```
(Adapt as needed for any additional libraries like grove.py.)

### 3. Install and Configure InfluxDB

```bash
sudo apt install influxdb -y
sudo systemctl start influxdb
sudo systemctl enable influxdb
```
Create a database (e.g., sensorbicho):

```bash
influx
CREATE DATABASE sensorbicho
EXIT
```

### 4. Install and Configure Grafana

```bash
sudo apt install software-properties-common wget -y
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update
sudo apt install grafana -y
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

Access Grafana in a browser at http://<RaspberryPiIP>:3000. Default credentials: admin / admin (you'll be prompted to change the password).

### 5. Configure InfluxDB as a Data Source in Grafana
  1. In Grafana, go to Configuration (gear icon) > Data Sources.
  2. Click Add data source and select InfluxDB.
  3. Set:
    - URL: http://localhost:8086
    - Database: sensorbicho
    - (No token needed for InfluxDB 1.x unless you configured authentication.)
  #### 4. Click Save & Test.

## Project Structure

```bash
.
├── conectLife.py            # Main Python script
├── README.md                # This file
└── ...
```
conectLife.py: Contains the code to read from sensors, write data to InfluxDB, and display on LCD.

## Usage

### 1. Wire up the sensors according to your Raspberry Pi GPIO pins defined in the code (TRIG_ECHO, BUZZER_PIN, etc.).
### 2. Run InfluxDB:

```bash
sudo systemctl start influxdb
```

### 3. Run the Python script:

```bash
python conectLife.py
```

### 4. Open Grafana in your browser at http://<RaspberryPiIP>:3000.
### 5. Create or open a dashboard, add a panel, and configure queries (InfluxQL) to view your data. For example:

```bash
SELECT mean("temperature") 
FROM "sensores" 
WHERE ("sensor"='dht11') AND $timeFilter 
GROUP BY time($interval) fill(null)
```

Watch your real-time sensor data and alert triggers in Grafana’s dashboard.

## How It Works

### 1. conectLife.py initializes GPIO, reads distance from the ultrasonic sensor, and checks a threshold for triggering the buzzer.
### 2. It also reads temperature/humidity from the DHT sensor when a button is pressed.
### 3. All sensor data is displayed on the LCD and then sent to InfluxDB via the Python InfluxDB client.
### 4. Grafana connects to InfluxDB to visualize the time-series data in customizable graphs.

## Troubleshooting
If no data appears in Grafana, ensure your Python script is running and that InfluxDB is started.

Check InfluxDB logs or CLI:

```bash
influx
USE sensorbicho
SELECT * FROM sensores LIMIT 10
```

Make sure you used the correct database name in your script and Grafana data source.
