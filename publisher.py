import json
import time
import paho.mqtt.client as mqtt

from sensors_data import (
    generate_gas_emission_data,
    generate_ground_temperature_data,
    generate_seismic_data,
    generate_sensor_network_data,
)

BROKER = "localhost"
PORT = 1883
LIMIT = 30
INTERVAL = 1

TOPICS = {
    "seismic": "sicily/seismic",
    "temperature": "sicily/ground_temperature",
    "gas": "sicily/gas_emissions",
    "network": "sicily/sensor_network",
}


def on_connect(client, userdata, flags, rc):
    print("Connected" if rc == 0 else f"Failed: {rc}")


def publish(client, topic, data):
    client.publish(topic, json.dumps(data), qos=1)


client = mqtt.Client(client_id="sicily-publisher")
client.on_connect = on_connect
client.connect(BROKER, PORT)
client.loop_start()

for i in range(LIMIT):
    time.sleep(INTERVAL)

    publish(client, TOPICS["seismic"], generate_seismic_data())
    publish(client, TOPICS["temperature"], generate_ground_temperature_data())
    publish(client, TOPICS["gas"], generate_gas_emission_data())
    publish(client, TOPICS["network"], generate_sensor_network_data())

client.loop_stop()
client.disconnect()
print("Publisher stopped")
