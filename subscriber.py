import os
import json
import mysql.connector
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from neo4j import GraphDatabase

mongo_conn = MongoClient(f"mongodb://{os.getenv('MONGO_HOST', 'mongodb')}:27017/")

mysql_conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "mysql"),
    user="root",
    password="123456",
    database="sicily_monitoring",
)

neo4j_conn = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
    auth=("neo4j", "12345678")
)

BROKER = os.getenv("MQTT_BROKER", "vernemq")
PORT = 1883

TOPICS = {
    "seismic": "sicily/seismic",
    "temp": "sicily/ground_temperature",
    "gas": "sicily/gas_emissions",
    "network": "sicily/sensor_network",
}

def mysql_insert_seismic(data):
    cursor = mysql_conn.cursor()
    cursor.execute("""
        INSERT INTO seismic_readings
        (sensor_id, location, magnitude, vibration_level, depth_km, risk_level, reading_time)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["sensor_id"],
        data["location"],
        data["magnitude"],
        data["vibration_level"],
        data["depth_km"],
        data["risk_level"],
        data["timestamp"],
    ))
    mysql_conn.commit()
    cursor.close()


def mysql_insert_alert(data, alert_type, message):
    if data["risk_level"] == "low":
        return

    cursor = mysql_conn.cursor()
    cursor.execute("""
        INSERT INTO alerts
        (sensor_id, location, alert_type, severity, message, reading_time)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        data["sensor_id"],
        data["location"],
        alert_type,
        data["risk_level"],
        message,
        data["timestamp"],
    ))
    mysql_conn.commit()
    cursor.close()

def mongo_insert(collection, data):
    mongo_conn["sicily_monitoring"][collection].insert_one(data)

def neo4j_insert(data):
    with neo4j_conn.session() as session:
        session.run("""
            MERGE (s1:Sensor {sensor_id: $source})
            MERGE (s2:Sensor {sensor_id: $target})
            MERGE (s1)-[:CONNECTED_TO]->(s2)
            SET s1.location = $location,
                s2.location = $location,
                s1.timestamp = $timestamp
        """, data)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT")
        client.subscribe([
            (TOPICS["seismic"], 1),
            (TOPICS["temp"], 1),
            (TOPICS["gas"], 1),
            (TOPICS["network"], 1),
        ])

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        if msg.topic == TOPICS["seismic"]:
            mysql_insert_seismic(data)
            mysql_insert_alert(data, "seismic",
                f"Magnitude {data['magnitude']}")
            mongo_insert("seismic_archive", data)

        elif msg.topic == TOPICS["temp"]:
            mongo_insert("temperature", data)
            mysql_insert_alert(data, "temperature",
                f"{data['temperature_c']} C")

        elif msg.topic == TOPICS["gas"]:
            mongo_insert("gas", data)
            mysql_insert_alert(data, "gas",
                f"SO2 {data['so2_ppm']} ppm")

        elif msg.topic == TOPICS["network"]:
            neo4j_insert(data)
            mongo_insert("network", data)

    except Exception as e:
        print("Error:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopping...")
    mysql_conn.close()
    neo4j_conn.close()
    mongo_conn.close()