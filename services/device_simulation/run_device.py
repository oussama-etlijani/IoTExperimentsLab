import paho.mqtt.client as mqtt
import time
import os
import json
import random
import logging
from datetime import datetime, timezone
import argparse

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

def get_env_variable(var_name, default_value=None):
    value = os.getenv(var_name, default_value)
    if value is None:
        logging.error(f"Environment variable {var_name} is not set.")
        raise ValueError(f"Environment variable {var_name} is not set.")
    logging.debug(f"Environment variable {var_name} is set to {value}.")
    return value

def load_sensor_config(config_file):
    with open(config_file, 'r') as file:
        sensor_config = json.load(file)
    logging.debug(f"Sensor configuration loaded: {sensor_config}")
    return sensor_config

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to broker")
        client.subscribe(subscribe_topic)  # Subscribe to the topic when connected
    else:
        logging.error(f"Connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    logging.warning(f"Disconnected from broker with return code {rc}")

def on_publish(client, userdata, mid):
    logging.debug(f"Message {mid} published.")

def publish_message(sensor_config):
    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    connected = False
    retry_interval = 1  # Start with 1 second

    while not connected:
        try:
            client.connect(broker, port)
            connected = True
        except Exception as e:
            logging.error(f"Connection error: {e}")
            logging.info(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
            retry_interval = min(retry_interval * 2, 60)  # Exponential backoff with a cap at 60 seconds

    client.loop_start()

    while True:
        try:
            sensor_data = {}
            for sensor in sensor_config:
                sensor_value = random.uniform(sensor["min_value"], sensor["max_value"])
                sensor_data[sensor["name"]] = sensor_value
            
            message = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "device_id": device_id,
                "sensor_data": sensor_data
            }
            result = client.publish(publish_topic, json.dumps(message))
            result.wait_for_publish()
            logging.info(f"Published: {message} to topic: {publish_topic}")
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error publishing message: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MQTT device simulation script')
    parser.add_argument('--broker', default=get_env_variable('MQTT_BROKER', 'mosquitto'))
    parser.add_argument('--port', type=int, default=int(get_env_variable('MQTT_PORT', 1883)))
    parser.add_argument('--publish_topic', default=get_env_variable('MQTT_PUBLISH_TOPIC', 'device/data'))
    parser.add_argument('--subscribe_topic', default=get_env_variable('MQTT_SUBSCRIBE_TOPIC', 'device/#'))
    parser.add_argument('--username', default=get_env_variable('MQTT_USERNAME'))
    parser.add_argument('--password', default=get_env_variable('MQTT_PASSWORD'))
    parser.add_argument('--device_id', default=get_env_variable('DEVICE_ID', 'device_001'))
    parser.add_argument('--sensor_config', default=os.path.join('config', 'device', 'device_config.json'))

    args = parser.parse_args()

    broker = args.broker
    port = args.port
    publish_topic = args.publish_topic
    subscribe_topic = args.subscribe_topic
    username = args.username
    password = args.password
    device_id = args.device_id
    sensor_config_file = args.sensor_config

    sensor_config = load_sensor_config(sensor_config_file)
    publish_message(sensor_config)
