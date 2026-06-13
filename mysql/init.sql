CREATE TABLE IF NOT EXISTS seismic_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(20) NOT NULL,
    location VARCHAR(80) NOT NULL,
    magnitude FLOAT NOT NULL,
    vibration_level FLOAT NOT NULL,
    depth_km FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    reading_time DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(20) NOT NULL,
    location VARCHAR(80) NOT NULL,
    alert_type VARCHAR(40) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message VARCHAR(255) NOT NULL,
    reading_time DATETIME NOT NULL
);
