"""
IoT Subscriber - Receives sensor data from HiveMQ and writes to InfluxDB.
Subscribes to: Energy, Room, Motor topics.
"""
import json
import logging
import sys
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS

# Add parent directory to path for config import
sys.path.append('..')
from config.config import (
    MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE,
    TOPIC_ENERGY, TOPIC_ROOM, TOPIC_MOTOR,
    INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET,
    LOG_LEVEL
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Subscriber')


class InfluxDBWriter:
    """Handles writing data to InfluxDB with error handling."""
    
    def __init__(self):
        self.client = None
        self.write_api = None
        self.connected = False
        self.connect()
    
    def connect(self):
        """Connect to InfluxDB with retry logic."""
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            try:
                logger.info(f'Connecting to InfluxDB at {INFLUXDB_URL}...')
                self.client = InfluxDBClient(
                    url=INFLUXDB_URL,
                    token=INFLUXDB_TOKEN,
                    org=INFLUXDB_ORG
                )
                
                # Test connection
                self.client.ping()
                
                # Create write API with async batching
                self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
                
                self.connected = True
                logger.info(f'✓ Connected to InfluxDB (org: {INFLUXDB_ORG}, bucket: {INFLUXDB_BUCKET})')
                return
                
            except Exception as e:
                retry_count += 1
                logger.error(f'InfluxDB connection failed (attempt {retry_count}/{max_retries}): {e}')
                if retry_count < max_retries:
                    time.sleep(5)
                else:
                    logger.error('Failed to connect to InfluxDB after maximum retries')
                    raise
    
    def write_point(self, measurement, tags, fields):
        """Write a data point to InfluxDB."""
        if not self.connected:
            logger.warning('Not connected to InfluxDB. Attempting to reconnect...')
            self.connect()
        
        try:
            point = Point(measurement)
            
            # Add tags
            for tag_key, tag_value in tags.items():
                point = point.tag(tag_key, tag_value)
            
            # Add fields
            for field_key, field_value in fields.items():
                point = point.field(field_key, field_value)
            
            # Set timestamp
            point = point.time(datetime.utcnow(), WritePrecision.NS)
            
            # Write to InfluxDB
            self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
            logger.debug(f'Wrote point to InfluxDB: {measurement}')
            
        except Exception as e:
            logger.error(f'Error writing to InfluxDB: {e}')
            self.connected = False
    
    def close(self):
        """Close InfluxDB connection."""
        if self.write_api:
            self.write_api.close()
        if self.client:
            self.client.close()
        logger.info('InfluxDB connection closed')


class MQTTSubscriber:
    """MQTT Subscriber with InfluxDB integration."""
    
    def __init__(self):
        self.client = mqtt.Client(client_id='iot-subscriber', clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        # Configure automatic reconnection
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        
        self.connected = False
        self.influxdb = InfluxDBWriter()
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker."""
        if rc == 0:
            self.connected = True
            logger.info(f'✓ Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}')
            
            # Subscribe to all topics
            self.client.subscribe(TOPIC_ENERGY, qos=1)
            self.client.subscribe(TOPIC_ROOM, qos=1)
            self.client.subscribe(TOPIC_MOTOR, qos=1)
            
            logger.info(f'✓ Subscribed to topics:')
            logger.info(f'  - {TOPIC_ENERGY}')
            logger.info(f'  - {TOPIC_ROOM}')
            logger.info(f'  - {TOPIC_MOTOR}')
        else:
            self.connected = False
            logger.error(f'✗ Connection failed with code {rc}')
    
    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker."""
        self.connected = False
        if rc != 0:
            logger.warning(f'⚠ Unexpected disconnect (code {rc}). Reconnecting...')
        else:
            logger.info('Disconnected from MQTT broker')
    
    def on_message(self, client, userdata, msg):
        """Callback when message is received."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            logger.info(f'📩 Received from {topic}')
            logger.debug(f'Payload: {payload}')
            
            # Process based on topic
            if topic == TOPIC_ENERGY:
                self.process_energy_data(payload)
            elif topic == TOPIC_ROOM:
                self.process_room_data(payload)
            elif topic == TOPIC_MOTOR:
                self.process_motor_data(payload)
            else:
                logger.warning(f'Unknown topic: {topic}')
                
        except json.JSONDecodeError as e:
            logger.error(f'Invalid JSON payload: {e}')
        except Exception as e:
            logger.error(f'Error processing message: {e}')
    
    def process_energy_data(self, data):
        """Process and store energy monitoring data."""
        try:
            self.influxdb.write_point(
                measurement='energy_monitoring',
                tags={'sensor_type': 'energy'},
                fields={
                    'consumption_watts': float(data.get('consumption_watts', 0)),
                    'voltage_volts': float(data.get('voltage_volts', 0)),
                    'current_amps': float(data.get('current_amps', 0))
                }
            )
            logger.info(f'✓ Stored energy data: {data.get("consumption_watts")}W')
        except Exception as e:
            logger.error(f'Error processing energy data: {e}')
    
    def process_room_data(self, data):
        """Process and store room monitoring data."""
        try:
            self.influxdb.write_point(
                measurement='room_monitoring',
                tags={'sensor_type': 'room'},
                fields={
                    'temperature_celsius': float(data.get('temperature_celsius', 0)),
                    'humidity_percent': float(data.get('humidity_percent', 0)),
                    'air_quality_index': int(data.get('air_quality_index', 0))
                }
            )
            logger.info(f'✓ Stored room data: {data.get("temperature_celsius")}°C, {data.get("humidity_percent")}%')
        except Exception as e:
            logger.error(f'Error processing room data: {e}')
    
    def process_motor_data(self, data):
        """Process and store motor monitoring data."""
        try:
            # Convert status to numeric (1=ON, 0=OFF)
            status_numeric = 1 if data.get('status') == 'ON' else 0
            
            self.influxdb.write_point(
                measurement='motor_monitoring',
                tags={
                    'sensor_type': 'motor',
                    'status': data.get('status', 'UNKNOWN')
                },
                fields={
                    'status_numeric': status_numeric,
                    'rpm': int(data.get('rpm', 0)),
                    'temperature_celsius': float(data.get('temperature_celsius', 0)),
                    'vibration_level': float(data.get('vibration_level', 0))
                }
            )
            logger.info(f'✓ Stored motor data: {data.get("status")} ({data.get("rpm")} RPM)')
        except Exception as e:
            logger.error(f'Error processing motor data: {e}')
    
    def connect(self):
        """Connect to MQTT broker with retry logic."""
        while True:
            try:
                logger.info(f'Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...')
                self.client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
                self.client.loop_start()
                
                # Wait for connection
                timeout = 10
                while not self.connected and timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                
                if self.connected:
                    return
                else:
                    logger.error('Connection timeout')
                    raise Exception('Connection timeout')
                    
            except Exception as e:
                logger.error(f'Connection error: {e}. Retrying in 5 seconds...')
                time.sleep(5)
    
    def run(self):
        """Main subscriber loop."""
        self.connect()
        
        logger.info('🚀 Subscriber started. Listening for messages...')
        logger.info('Press Ctrl+C to stop...\n')
        
        try:
            while True:
                if not self.connected:
                    logger.warning('Not connected to MQTT broker. Waiting for reconnection...')
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info('\n\n👋 Stopping subscriber...')
            self.client.loop_stop()
            self.client.disconnect()
            self.influxdb.close()
            logger.info('✓ Subscriber stopped')


if __name__ == '__main__':
    subscriber = MQTTSubscriber()
    subscriber.run()
