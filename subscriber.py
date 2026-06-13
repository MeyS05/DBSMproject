import json
import os

import mysql.connector
import paho.mqtt.client as mqtt
from neo4j import GraphDatabase
from pymongo import MongoClient

# ── Database connections ───────────────────────────────────────────────────────
mongo_conn = MongoClient(f"mongodb://{os.getenv('MONGO_HOST', 'mongodb')}:27017/")
print("Connected to MongoDB")

mysql_conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "mysql"),
    user="root",
    password="123456",
    database="sicily_monitoring",
)
print("Connected to MySQL")

neo4j_conn = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://neo4j:7687"), auth=("neo4j", "12345678")
)
print("Connected to Neo4j")

# ── MQTT config ────────────────────────────────────────────────────────────────
BROKER = os.getenv("MQTT_BROKER", "vernemq")
PORT   = 1883

TOPIC_SEISMIC            = "sicily/seismic"
TOPIC_GROUND_TEMPERATURE = "sicily/ground_temperature"
TOPIC_GAS_EMISSIONS      = "sicily/gas_emissions"
TOPIC_SENSOR_NETWORK     = "sicily/sensor_network"


# ── DB helpers ─────────────────────────────────────────────────────────────────
def mysql_insert_seismic(data):
    try:
        cursor = mysql_conn.cursor()
        cursor.execute(
            """INSERT INTO seismic_readings
               (sensor_id, location, magnitude, vibration_level, depth_km, risk_level, reading_time)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (data["sensor_id"], data["location"], data["magnitude"],
             data["vibration_level"], data["depth_km"], data["risk_level"], data["timestamp"]),
        )
        mysql_conn.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")


def mysql_insert_alert(data, alert_type, value):
    if data["risk_level"] not in ("medium", "high"):
        return
    try:
        cursor = mysql_conn.cursor()
        cursor.execute(
            """INSERT INTO alerts
               (sensor_id, location, alert_type, severity, message, reading_time)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (data["sensor_id"], data["location"], alert_type, data["risk_level"],
             f"{alert_type} detected in {data['location']}: {value}", data["timestamp"]),
        )
        mysql_conn.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"MySQL Alert Error: {err}")


def mongo_insert(collection, data):
    try:
        mongo_conn["sicily_monitoring"][collection].insert_one(data)
    except Exception as err:
        print(f"MongoDB Error: {err}")


def neo4j_insert_network(data):
    try:
        with neo4j_conn.session() as session:
            session.run(
                """
                MERGE (s1:Sensor {sensor_id: $source_sensor})
                MERGE (s2:Sensor {sensor_id: $target_sensor})
                MERGE (l:Location {name: $location})
                MERGE (s1)-[:INSTALLED_IN]->(l)
                MERGE (s2)-[:INSTALLED_IN]->(l)
                MERGE (s1)-[r:CONNECTED_TO]->(s2)
                SET r.signal_strength = $signal_strength,
                    r.latency_ms = $latency_ms,
                    r.timestamp = $timestamp
                """,
                source_sensor=data["source_sensor"],
                target_sensor=data["target_sensor"],
                location=data["location"],
                signal_strength=data["signal_strength"],
                latency_ms=data["latency_ms"],
                timestamp=data["timestamp"],
            )
    except Exception as err:
        print(f"Neo4j Error: {err}")


# ── MQTT callbacks ─────────────────────────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe([
            (TOPIC_SEISMIC, 1),
            (TOPIC_GROUND_TEMPERATURE, 1),
            (TOPIC_GAS_EMISSIONS, 1),
            (TOPIC_SENSOR_NETWORK, 1),
        ])
    else:
        print("Connection failed")


def on_message(client, userdata, msg):
    print(f"{msg.topic} -> {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload)

        if msg.topic == TOPIC_SEISMIC:
            mysql_insert_seismic(data)
            mysql_insert_alert(data, "Seismic activity", f"magnitude {data['magnitude']}")
            mongo_insert("seismic_archive", data)

        elif msg.topic == TOPIC_GROUND_TEMPERATURE:
            mongo_insert("ground_temperature", data)
            mysql_insert_alert(data, "Ground temperature", f"{data['temperature_c']} C")

        elif msg.topic == TOPIC_GAS_EMISSIONS:
            mongo_insert("gas_emissions", data)
            mysql_insert_alert(data, "Gas emission", f"SO2 {data['so2_ppm']} ppm")

        elif msg.topic == TOPIC_SENSOR_NETWORK:
            neo4j_insert_network(data)
            mongo_insert("sensor_network_archive", data)

    except json.JSONDecodeError as err:
        print(f"JSON Decode Error: {err}")
    except Exception as err:
        print(f"Error processing message: {err}")


# ── Start ──────────────────────────────────────────────────────────────────────
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Subscriber stopped")
    client.disconnect()
    mysql_conn.close()
    neo4j_conn.close()
    mongo_conn.close()