import json
import os
import time

import paho.mqtt.client as mqtt

from sensors_data import (
    generate_gas_emission_data,
    generate_ground_temperature_data,
    generate_seismic_data,
    generate_sensor_network_data,
)

BROKER = os.getenv("MQTT_BROKER", "vernemq")
PORT   = int(os.getenv("MQTT_PORT", 1883))
LIMIT  = int(os.getenv("MESSAGE_LIMIT", 30))
INTERVAL = float(os.getenv("PUBLISH_INTERVAL", 1))

TOPIC_SEISMIC           = "sicily/seismic"
TOPIC_GROUND_TEMPERATURE = "sicily/ground_temperature"
TOPIC_GAS_EMISSIONS     = "sicily/gas_emissions"
TOPIC_SENSOR_NETWORK    = "sicily/sensor_network"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")


def publish(client, topic, data):
    result = client.publish(topic, json.dumps(data), qos=1)
    if result[0] == 0:
        print(f"Sent {topic}: {data}")
    else:
        print(f"Failed to send to {topic}")


client = mqtt.Client(client_id="sicily-publisher")
client.on_connect = on_connect
client.connect(BROKER, PORT)
client.loop_start()

msg_count = 0
while True:
    time.sleep(INTERVAL)

    publish(client, TOPIC_SEISMIC,            generate_seismic_data())
    publish(client, TOPIC_GROUND_TEMPERATURE, generate_ground_temperature_data())
    publish(client, TOPIC_GAS_EMISSIONS,      generate_gas_emission_data())
    publish(client, TOPIC_SENSOR_NETWORK,     generate_sensor_network_data())

    msg_count += 1
    if LIMIT and msg_count >= LIMIT:
        break

client.loop_stop()
client.disconnect()
print("Publisher disconnected.")