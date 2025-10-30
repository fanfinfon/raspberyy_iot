"""
Demo: Encrypt and decrypt real sensor-style data using PRESENT-80 CTR mode.
This simulates your Raspberry Pi Level 0–1 IoT encryption process.
"""

import json
import time
from encryption.encryption_layer import encrypt_payload, decrypt_payload
from config import PRESENT_KEY

# --- Simulate a single sensor + telemetry reading (like your Pi does) ---
def get_mock_sensor_data():
    # Instead of real DHT11 and psutil, we mock realistic values.
    return {
        "device": "pi_zero_demo",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "temperature": 24.3,   # °C
        "humidity": 47.8,      # %
    }

# --- Step 1: Create plaintext JSON payload ---
sensor_data = get_mock_sensor_data()
payload = json.dumps(sensor_data).encode('utf-8')

print("📦 Original JSON Payload:")
print(json.dumps(sensor_data, indent=4))

# --- Step 2: Encrypt the payload ---
ciphertext = encrypt_payload(payload, key=PRESENT_KEY)

print("\n🔐 Encrypted Payload (hex preview):")
print(ciphertext.hex()[:120] + "..." if len(ciphertext.hex()) > 120 else ciphertext.hex())
print(f"Total bytes: {len(ciphertext)}")

# --- Step 3: Decrypt the payload to verify correctness ---
plaintext = decrypt_payload(ciphertext, key=PRESENT_KEY)
decoded = json.loads(plaintext.decode())

print("\n🔓 Decrypted JSON Payload:")
print(json.dumps(decoded, indent=4))

# --- Step 4: Confirm match ---
if sensor_data == decoded:
    print("\n✅ SUCCESS: Encryption & decryption verified correctly!")
else:
    print("\n⚠️ WARNING: Decrypted data doesn’t match — check implementation.")
