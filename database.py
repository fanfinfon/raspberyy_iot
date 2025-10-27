import sqlite3
from datetime import datetime

DB_FILE = "sensor_data.db"

def init_db():
    """Create table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sensor_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            cpu_temp REAL,
            cpu_usage REAL,
            net_in REAL,
            net_out REAL,
            sent_status INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()


def save_reading(temperature, humidity, cpu_temp, cpu_usage, net_in, net_out):
    """Insert a new sensor + telemetry record with current timestamp."""
    ts = datetime.now().isoformat(timespec='seconds')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sensor_log (
            timestamp, temperature, humidity,
            cpu_temp, cpu_usage, net_in, net_out, sent_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (ts, temperature, humidity, cpu_temp, cpu_usage, net_in, net_out))
    conn.commit()
    conn.close()
    return ts

