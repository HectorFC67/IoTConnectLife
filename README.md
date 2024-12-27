# IoT Connect Life

This project runs on a Raspberry Pi and integrates:

- A **DHT11** temperature and humidity sensor.
- An **ultrasonic distance sensor**.
- A **buzzer** and an **LCD display**.
- **Data logging** to InfluxDB.
- **Data visualization** through Grafana.

---

## Features

1. **Distance Detection**:  
   The ultrasonic sensor measures distance. If a certain threshold is reached, a buzzer and on-screen alert will trigger.

2. **Temperature & Humidity Monitoring**:  
   The DHT11 sensor records temperature and humidity.

3. **LCD Display**:  
   Shows real-time readings (distance, temperature, humidity) and system messages.

4. **Data Storage in InfluxDB**:  
   Logs all sensor data (distance, temperature, humidity) as time-series data.

5. **Grafana Dashboards**:  
   Visualizes data stored in InfluxDB using customizable charts.

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

- **Raspberry Pi OS**
- **Python 3**
- **InfluxDB (v1.x)**
- **Grafana**
- Required Python libraries:
  - `RPi.GPIO`
  - `Adafruit_DHT`
  - `influxdb`
  - `grove.py` (if using Grove libraries)

---

## What Does ConnectLife Do?

**ConnectLife** is a project designed to simulate the security and monitoring system of a smart home. It continuously monitors the ultrasonic sensor, which acts as a virtual peephole at the front door, detecting whether there is something near. The system defines "near" as being less than 10 cm away. When this condition is met, the buzzer is activated, sounding an alert until the object moves farther than 10 cm away.

Additionally, by pressing a button, the system switches modes. Instead of using the ultrasonic sensor, it starts using the Temperature & Humidity Sensor (DHT11) to measure the indoor temperature and humidity. Pressing the button again switches the system back to ultrasonic sensor mode.

All data collected by the system is displayed in real-time on an LCD screen for the user's convenience. Moreover, the system logs all collected data into **InfluxDB** and **Grafana**, enabling the user to monitor historical data locally in an easy-to-use interface.

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

```plaintext
.
├── conectLife.py            # Main Python script
└──README.md                # This file
```
conectLife.py: Contains the code to read from sensors, write data to InfluxDB, and display on LCD.

---

## Usage

1. Wire up the sensors according to your Raspberry Pi GPIO pins defined in the code (TRIG_ECHO, BUZZER_PIN, etc.).
2. Activate the enviorament:

```bash
source kklcd/bin/activate
```

3. Run InfluxDB and Grafana Server:

```bash
sudo systemctl start influxdb
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

4. Run the Python script:

```bash
python conectLife.py
```

5. Open Grafana in your browser at http://(RaspberryPiIP):3000.
6. Create or open a dashboard, add a panel, and configure queries (InfluxQL) to view your data. For example:

```bash
SELECT mean("temperature") 
FROM "sensores"
```

Watch your real-time sensor data and alert triggers in Grafana’s dashboard.

---

## How It Works

1. **Data Collection**:  
   - The ultrasonic sensor measures distances and checks against a threshold to trigger alerts.
   - The DHT11 sensor captures temperature and humidity values when prompted.

2. **Data Display**:  
   - All real-time readings (distance, temperature, humidity) and alerts are displayed on an LCD.

3. **Data Logging**:  
   - Sensor data is logged into an InfluxDB time-series database for storage.

4. **Data Visualization**:  
   - Grafana retrieves the stored data from InfluxDB and visualizes it in customizable dashboards.

---

## Troubleshooting

If Grafana doesn't display data:
  1. Ensure that `conectLife.py` is running and properly logging data to InfluxDB.
  2. Verify InfluxDB's service status and inspect the logs for errors.
  3. Check your database configuration:
     - Database name in `conectLife.py` matches the one configured in Grafana.
  4. Use the InfluxDB CLI to query the database and confirm data insertion.
```bash
influx
USE sensorbicho
SELECT * FROM sensores LIMIT 10
```

If data still doesn't appear in Grafana, review your query syntax or ensure the correct time filter is applied.

---

This document provides all necessary information for setting up, using, and troubleshooting the **IoT Connect Life** project.
