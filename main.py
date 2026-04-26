import time
from datetime import datetime, timezone

from config import (
    SIMULATION_STEP_SECONDS,
    SIMULATION_TIME_STEP_HOURS,
    BATTERY_CAPACITY_KWH,
    BATTERY_SOC_INITIAL,
    BATTERY_MAX_CHARGE_KW,
    BATTERY_MAX_DISCHARGE_KW,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_KEEPALIVE,
    MQTT_CLIENT_ID,
    MQTT_TOPIC_PREFIX,
)

from simulators.pv import PVSimulator
from simulators.load import LoadSimulator
from simulators.battery import BatterySimulator
from services.mqtt_publisher import MQTTPublisher


def main():
    pv = PVSimulator(peak_power_kw=5.0)
    load = LoadSimulator(base_load_kw=2.2)
    battery = BatterySimulator(
        capacity_kwh=BATTERY_CAPACITY_KWH,
        soc_initial=BATTERY_SOC_INITIAL,
        max_charge_kw=BATTERY_MAX_CHARGE_KW,
        max_discharge_kw=BATTERY_MAX_DISCHARGE_KW,
    )

    mqtt_publisher = MQTTPublisher(
        broker_host=MQTT_BROKER_HOST,
        broker_port=MQTT_BROKER_PORT,
        client_id=MQTT_CLIENT_ID,
        keepalive=MQTT_KEEPALIVE,
    )

    simulated_hour = 0.0
    dt_hours = SIMULATION_TIME_STEP_HOURS

    print("Simulation du système renouvelable avec MQTT démarrée...\n")

    try:
        mqtt_publisher.connect()

        while True:
            timestamp = datetime.now(timezone.utc).isoformat()

            pv_power = pv.generate_power(simulated_hour)
            load_power = load.generate_load(simulated_hour)
            net_power = pv_power - load_power

            battery_data = battery.update(net_power_kw=net_power, dt_hours=dt_hours)

            pv_message = {
                "device_id": "pv_01",
                "timestamp": timestamp,
                "simulated_hour": round(simulated_hour, 2),
                "power_kw": pv_power,
            }

            load_message = {
                "device_id": "load_01",
                "timestamp": timestamp,
                "simulated_hour": round(simulated_hour, 2),
                "power_kw": load_power,
            }

            battery_message = {
                "device_id": "battery_01",
                "timestamp": timestamp,
                "simulated_hour": round(simulated_hour, 2),
                "soc": battery_data["soc"],
                "battery_power_kw": battery_data["battery_power_kw"],
                "mode": battery_data["mode"],
            }

            system_message = {
                "device_id": "system_01",
                "timestamp": timestamp,
                "simulated_hour": round(simulated_hour, 2),
                "pv_power_kw": pv_power,
                "load_power_kw": load_power,
                "net_power_kw": round(net_power, 3),
                "battery_soc": battery_data["soc"],
                "battery_mode": battery_data["mode"],
            }

            mqtt_publisher.publish(f"{MQTT_TOPIC_PREFIX}/pv", pv_message)
            mqtt_publisher.publish(f"{MQTT_TOPIC_PREFIX}/load", load_message)
            mqtt_publisher.publish(f"{MQTT_TOPIC_PREFIX}/battery", battery_message)
            mqtt_publisher.publish(f"{MQTT_TOPIC_PREFIX}/system", system_message)

            print(
                f"Heure: {simulated_hour:05.2f} h | "
                f"PV: {pv_power:>5.2f} kW | "
                f"Load: {load_power:>5.2f} kW | "
                f"Net: {net_power:>6.2f} kW | "
                f"Battery: {battery_data['mode']:<11} | "
                f"SOC: {battery_data['soc']:>6.2f} %"
            )

            simulated_hour += dt_hours
            if simulated_hour >= 24:
                simulated_hour = 0.0

            time.sleep(SIMULATION_STEP_SECONDS)

    except KeyboardInterrupt:
        print("\nSimulation arrêtée par l'utilisateur.")

    except Exception as e:
        print(f"\nErreur: {e}")

    finally:
        mqtt_publisher.disconnect()


if __name__ == "__main__":
    main()