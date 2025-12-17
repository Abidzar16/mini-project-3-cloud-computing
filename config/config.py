"""
Shared configuration module for IoT monitoring system.
Loads settings from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'hivemq')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_KEEPALIVE = int(os.getenv('MQTT_KEEPALIVE', 60))

# MQTT Topics
TOPIC_ENERGY = os.getenv('TOPIC_ENERGY', 'iot/energy')
TOPIC_ROOM = os.getenv('TOPIC_ROOM', 'iot/room')
TOPIC_MOTOR = os.getenv('TOPIC_MOTOR', 'iot/motor')

# InfluxDB Configuration
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'my-super-secret-auth-token')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'iot-org')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'iot-data')

# Publisher Configuration
PUBLISH_INTERVAL = int(os.getenv('PUBLISH_INTERVAL', 5))

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
