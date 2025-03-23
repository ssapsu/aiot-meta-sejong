import paho.mqtt.client as mqtt
import json

# 브로커 주소 및 포트
BROKER_HOST = "localhost"
BROKER_PORT = 1883  # Docker 매핑 포트 (실제 Mosquitto 내부 포트는 1883)

# 실제 알림이 발행되는 토픽 (와일드카드를 사용한 예)
TOPIC = "/oneM2M/req/+/meta_sejong_meta_robot/json"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(TOPIC)
        print(f"Subscribed to topic: {TOPIC}")
    else:
        print(f"Connection failed with code: {rc}")


def on_message(client, userdata, msg):
    print(f"\nReceived message on topic {msg.topic}:")
    try:
        payload_str = msg.payload.decode("utf-8")
        payload_json = json.loads(payload_str)
        print("Payload:", payload_json)
    except Exception as e:
        print("Error decoding message:", e)
        print("Raw message:", msg.payload)


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()
