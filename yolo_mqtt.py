import paho.mqtt.client as mqtt

# HiveMQ Cloud credentials
broker = "cfadba297a484a28b80d55a8991a1fef.s1.eu.hivemq.cloud"
port = 8883
username = "esp32"
password = "Cipcip123"
topic = "cat/feeder"

client = mqtt.Client()
client.username_pw_set(username, password)
client.tls_set()  # enable SSL


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to HiveMQ Cloud")
        # test send
        client.publish(topic, "open")
        print("📨 Sent 'open' message")
    else:
        print("❌ Failed to connect, code:", rc)


client.on_connect = on_connect

print("Connecting...")
client.connect(broker, port)
client.loop_forever()
