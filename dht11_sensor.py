import board
import adafruit_dht

dhtDevice = adafruit_dht.DHT11(board.D4)

def read_dht11():
    """Return temperature and humidity from DHT11"""
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        if humidity is not None and temperature is not None:
            return {"temperature": temperature, "humidity": humidity}
        else:
            return None
    except Exception as e:
        if "A full buffer was not returned" in str(e):
            return None  # ignore this common timing error
        else:
            print("Error:", e)
            return None
