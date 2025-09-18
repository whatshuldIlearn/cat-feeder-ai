import os
import subprocess
import sys
import time

import paho.mqtt.client as mqtt

# 🔹 Use your HiveMQ Cloud broker, not the free public one
MQTT_BROKER = "cfadba297a484a28b80d55a8991a1fef.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "esp32"
MQTT_PASS = "Cipcip123"
MQTT_TOPIC = "cat/feeder"

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set()  # HiveMQ Cloud requires TLS
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Folder where new images arrive
WATCH_FOLDER = "images_in"
# Folder to save detection results
OUTPUT_FOLDER = "runs/detect/results"

# Keep track of processed files
processed = set()

while True:
    # List all image files in WATCH_FOLDER
    files = [f for f in os.listdir(WATCH_FOLDER) if f.lower().endswith((".jpg", ".png", ".jpeg"))]

    for file in files:
        if file not in processed:
            filepath = os.path.join(WATCH_FOLDER, file)

            print(f"[INFO] New file detected: {filepath}")

            # Run YOLO detect.py on this file
            result = subprocess.run(
                [
                    sys.executable,
                    "detect_cat.py",
                    "--source",
                    filepath,
                    "--weights",
                    "yolov5s.pt",
                    "--device",
                    "cpu",
                    "--project",
                    "runs/detect",
                    "--name",
                    "results",
                    "--exist-ok",
                ],
                capture_output=True,
                text=True,
            )

            lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
            last_line = lines[-1] if lines else ""

            if last_line == "Cat Detected":
                print("✅ Cat detected → Publishing 'open' to MQTT")
                client.publish(MQTT_TOPIC, "open")
            elif last_line == "No Cat Detected":
                print("❌ No cat detected → Publishing 'idle' to MQTT")
                client.publish(MQTT_TOPIC, "idle")
            else:
                print("⚠️ YOLO did not return a clean result")

            # Mark as processed
            processed.add(file)

    time.sleep(10)  # wait 10 seconds before scanning again
