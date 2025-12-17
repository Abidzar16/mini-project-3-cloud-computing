"""
IoT Publisher - Simulates sensor data and publishes to HiveMQ broker.
Monitors: Energy consumption, Room conditions (temperature/humidity), Motor status.
"""
import json
import logging
import random
import sys
import time
from datetime import datetime

import paho.mqtt.client as mqtt

# Add parent directory to path for config import
sys.path.append('..')
from config.config import (
    MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE,
    TOPIC_ENERGY, TOPIC_ROOM, TOPIC_MOTOR,
    PUBLISH_INTERVAL, LOG_LEVEL
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Publisher')


class SensorSimulator:
    """Simulates realistic IoT sensor data."""
    
    @staticmethod
    def get_energy_data():
        """Simulate energy consumption in Watts (0-1000W)."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'sensor_type': 'energy',
            'consumption_watts': round(random.uniform(0, 1000), 2),
            'voltage_volts': round(random.uniform(220, 240), 2),
            'current_amps': round(random.uniform(0, 5), 2)
        }
    
    @staticmethod
    def get_room_data():
        """Simulate room temperature and humidity."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'sensor_type': 'room',
            'temperature_celsius': round(random.uniform(18, 30), 2),
            'humidity_percent': round(random.uniform(30, 70), 2),
            'air_quality_index': random.randint(0, 100)
        }
    
    @staticmethod
    def get_motor_data():
        """Simulate motor status and metrics."""
        status = random.choice(['ON', 'OFF'])
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'sensor_type': 'motor',
            'status': status,
            'rpm': random.randint(0, 3000) if status == 'ON' else 0,
            'temperature_celsius': round(random.uniform(20, 80), 2) if status == 'ON' else round(random.uniform(20, 30), 2),
            'vibration_level': round(random.uniform(0, 10), 2) if status == 'ON' else 0
        }


class MQTTPublisher:
    """MQTT Publisher with reconnection logic."""
    
    def __init__(self):
        self.client = mqtt.Client(client_id='iot-publisher', clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        
        # Configure automatic reconnection
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        
        self.connected = False
        self.simulator = SensorSimulator()
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker."""
        if rc == 0:
            self.connected = True
            logger.info(f'✓ Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}')
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
    
    def on_publish(self, client, userdata, mid):
        """Callback when message is published."""
        logger.debug(f'Message {mid} published')
    
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
    
    def publish_sensor_data(self):
        """Publish data from all sensors."""
        try:
            # Energy monitoring
            energy_data = self.simulator.get_energy_data()
            self.client.publish(TOPIC_ENERGY, json.dumps(energy_data), qos=1)
            logger.info(f'📊 Energy: {energy_data["consumption_watts"]}W')
            
            # Room monitoring
            room_data = self.simulator.get_room_data()
            self.client.publish(TOPIC_ROOM, json.dumps(room_data), qos=1)
            logger.info(f'🌡️  Room: {room_data["temperature_celsius"]}°C, {room_data["humidity_percent"]}%')
            
            # Motor monitoring
            motor_data = self.simulator.get_motor_data()
            self.client.publish(TOPIC_MOTOR, json.dumps(motor_data), qos=1)
            logger.info(f'⚙️  Motor: {motor_data["status"]} ({motor_data["rpm"]} RPM)')
            
        except Exception as e:
            logger.error(f'Error publishing data: {e}')
    
    def run(self):
        """Main publishing loop."""
        self.connect()
        
        logger.info(f'🚀 Publisher started. Publishing every {PUBLISH_INTERVAL} seconds.')
        logger.info('Press Ctrl+C to stop...\n')
        
        try:
            while True:
                if self.connected:
                    self.publish_sensor_data()
                    logger.info('-' * 60)
                else:
                    logger.warning('Not connected. Waiting for reconnection...')
                
                time.sleep(PUBLISH_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info('\n\n👋 Stopping publisher...')
            self.client.loop_stop()
            self.client.disconnect()
            logger.info('✓ Publisher stopped')


if __name__ == '__main__':
    publisher = MQTTPublisher()
    publisher.run()
