import time, json, paho.mqtt.client as mqtt
import dht11_sensor, database, telemetry

BROKER = "172.20.10.3"
TOPIC  = "sensor/data"

database.init_db()
client = mqtt.Client("pi_zero_client")
client.connect(BROKER)

while True:
    data = dht11_sensor.read_dht11()
    telemetry_data = telemetry.get_telemetry()

    if data:
        # Save both sensor + telemetry locally
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
        print("Published:", payload)
    else:
        print("No reading, retrying...")

    time.sleep(5)
