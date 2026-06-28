# Sicily Tectonic and Environmental Monitoring

This project simulates an IoT monitoring system for Sicily. It uses Python and MQTT to send simulated sensor data, then stores the received data in different database platforms depending on the MQTT topic.

## Project Idea

The system monitors possible tectonic and environmental risk indicators:

- Seismic vibrations and earthquake magnitude
- Ground temperature
- Gas emission levels
- Sensor network connections

The data is simulated, so no physical sensors are required.

## Architecture

1. `publisher.py` generates simulated sensor readings.
2. The readings are sent to the VerneMQ MQTT broker.
3. `subscriber.py` receives messages from MQTT topics.
4. The subscriber processes each message and stores it in the correct database.

The databases, broker, and admin dashboards run in Docker. `publisher.py` and `subscriber.py` run locally with Python, connecting to the Dockerized services through their published ports on `localhost`.

## MQTT Topics and Storage

| MQTT topic | Example data | Main database |
| --- | --- | --- |
| `sicily/seismic` | magnitude, vibration, depth | MySQL |
| `sicily/ground_temperature` | ground temperature | MongoDB |
| `sicily/gas_emissions` | CO2 and SO2 levels | MongoDB |
| `sicily/sensor_network` | connection between sensor nodes | Neo4j |

Medium and high-risk seismic, temperature, and gas events are also saved in the MySQL `alerts` table.

## Technologies

- Python
- Paho MQTT
- VerneMQ MQTT broker
- MySQL
- MongoDB
- Neo4j
- Docker and Docker Compose
- phpMyAdmin
- Mongo Express

## How to Run

1. Start the databases, broker, and dashboards:

```bash
docker compose up -d
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Start the subscriber (keeps running, storing messages):

```bash
python subscriber.py
```

4. In a separate terminal, start the publisher:

```bash
python publisher.py
```

The publisher sends 30 cycles of simulated data across all four topics, then stops automatically. The subscriber keeps running and storing messages until stopped manually.

To stop the system:

```bash
docker compose down
```

To delete all stored database data and start again:

```bash
docker compose down -v
```

## Database Interfaces

- phpMyAdmin: http://localhost:8081
  - Server: `mysql`
  - User: `root`
  - Password: `123456`
  - Database: `sicily_monitoring`

- Mongo Express: http://localhost:8082
  - Database: `sicily_monitoring`

- Neo4j Browser: http://localhost:7474
  - User: `neo4j`
  - Password: `12345678`

## Example Neo4j Query

```cypher
MATCH (s:Sensor)-[r:CONNECTED_TO]->(t:Sensor)
RETURN s, r, t
LIMIT 25;
```

## Example MySQL Queries

```sql
SELECT * FROM seismic_readings ORDER BY id DESC LIMIT 10;
SELECT * FROM alerts ORDER BY id DESC LIMIT 10;
```

## Files

- `docker-compose.yaml`: defines the database, broker, and dashboard containers
- `requirements.txt`: Python libraries
- `sensors_data.py`: simulated Sicily sensor data
- `publisher.py`: publishes data to MQTT
- `subscriber.py`: subscribes, processes, and stores data
- `mysql/init.sql`: creates MySQL tables

## Conclusion

This project demonstrates a simple big-data style pipeline for IoT monitoring. MQTT handles lightweight data transmission, Python performs processing and routing, and the databases store different forms of data: relational events in MySQL, flexible sensor documents in MongoDB, and network relationships in Neo4j.
