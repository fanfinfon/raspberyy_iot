import time, json, paho.mqtt.client as mqtt
import dht11_sensor, database, telemetry, prevent_auto_discovery

# --- Basic settings ---
BROKER = "172.20.10.3"
TOPIC = "sensor/data"
TRUSTED_IPS = ["172.20.10.3", "172.20.10.10"]
NEW_HOSTNAME = "node5a1"
OLD_HOSTNAME = "raspberrypiw"

# --- Secure network before doing anything ---
prevent_auto_discovery.harden_network(TRUSTED_IPS, NEW_HOSTNAME)

# --- Initialize database and MQTT ---
database.init_db()
client = mqtt.Client("pi_zero_client")
client.connect(BROKER)

print(" System started. Press Ctrl+C to stop.\n")

# --- Main data collection loop ---
try:
    while True:
        data = dht11_sensor.read_dht11()
        telemetry_data = telemetry.get_telemetry()

        if data:
            # Save both sensor and telemetry data locally
            ts = database.save_reading(
                data["temperature"],
                data["humidity"],
                telemetry_data["cpu_temp"],
                telemetry_data["cpu_usage"],
                telemetry_data["net_in"],
                telemetry_data["net_out"]
            )

            # Send only the sensor data
            payload = json.dumps({
                "device": "pi_zero",
                "timestamp": ts,
                "temperature": data["temperature"],
                "humidity": data["humidity"]
            })
            client.publish(TOPIC, payload)
            print("✅ Published:", payload)
        else:
            print("⚠️ No reading, retrying...")

        time.sleep(5)

# --- Handle interruption or error gracefully ---
except KeyboardInterrupt:
    print("\nScript stopped by user.")
except Exception as e:
    print(f" Error occurred: {e}")
finally:
    # --- Always restore network when script ends ---
    prevent_auto_discovery.restore_network(OLD_HOSTNAME)
    print(" Network restored to normal.")
