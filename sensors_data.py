import random
from datetime import datetime


LOCATIONS = [
    "Catania",
    "Etna Nord",
    "Etna Sud",
    "Messina",
    "Palermo",
    "Siracusa",
]


def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sensor_id(prefix):
    return f"{prefix}-{random.randint(1, 6)}"


def risk_from_value(value, medium, high):
    if value >= high:
        return "high"
    elif value >= medium:
        return "medium"
    return "low"
    

def generate_seismic_data():
    magnitude = round(random.uniform(0.5, 5.5), 2)
    vibration_level = round(random.uniform(0.01, 1.8), 3)
    return {
        "sensor_id": sensor_id("SEIS"),
        "location": random.choice(LOCATIONS),
        "magnitude": magnitude,
        "vibration_level": vibration_level,
        "depth_km": round(random.uniform(1, 30), 2),
        "risk_level": risk_from_value(magnitude, 3.0, 4.5),
        "timestamp": current_timestamp(),
    }


def generate_ground_temperature_data():
    temperature = round(random.uniform(12, 95), 2)
    return {
        "sensor_id": sensor_id("TEMP"),
        "location": random.choice(LOCATIONS),
        "temperature_c": temperature,
        "risk_level": risk_from_value(temperature, 55, 75),
        "timestamp": current_timestamp(),
    }


def generate_gas_emission_data():
    co2_ppm = round(random.uniform(350, 2500), 2)
    so2_ppm = round(random.uniform(0.01, 12), 2)
    return {
        "sensor_id": sensor_id("GAS"),
        "location": random.choice(LOCATIONS),
        "co2_ppm": co2_ppm,
        "so2_ppm": so2_ppm,
        "risk_level": risk_from_value(so2_ppm, 4, 8),
        "timestamp": current_timestamp(),
    }


def generate_sensor_network_data():
    source = sensor_id("NODE")
    target = sensor_id("NODE")
    while target == source:
        target = sensor_id("NODE")

    return {
        "source_sensor": source,
        "target_sensor": target,
        "location": random.choice(LOCATIONS),
        "signal_strength": random.randint(45, 100),
        "latency_ms": random.randint(5, 250),
        "timestamp": current_timestamp(),
    }
