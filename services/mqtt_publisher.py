import json
import paho.mqtt.client as mqtt


class MQTTPublisher:
    def __init__(self, broker_host: str, broker_port: int, client_id: str, keepalive: int = 60):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.keepalive = keepalive

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=mqtt.MQTTv311
        )

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print(f"[MQTT] Connecté au broker {self.broker_host}:{self.broker_port}")
        else:
            print(f"[MQTT] Échec de connexion. Code retour: {reason_code}")

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        print(f"[MQTT] Déconnecté du broker. Code: {reason_code}")

    def connect(self):
        self.client.connect(self.broker_host, self.broker_port, self.keepalive)
        self.client.loop_start()

    def publish(self, topic: str, payload: dict):
        payload_json = json.dumps(payload, ensure_ascii=False)
        msg_info = self.client.publish(topic, payload_json)
        msg_info.wait_for_publish()

        if msg_info.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[MQTT] Publié sur {topic}: {payload_json}")
        else:
            print(f"[MQTT] Erreur publication sur {topic}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()