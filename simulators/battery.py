class BatterySimulator:
    def __init__(
        self,
        capacity_kwh: float,
        soc_initial: float,
        max_charge_kw: float,
        max_discharge_kw: float,
    ):
        self.capacity_kwh = capacity_kwh
        self.soc = soc_initial
        self.max_charge_kw = max_charge_kw
        self.max_discharge_kw = max_discharge_kw

    def update(self, net_power_kw: float, dt_hours: float) -> dict:
        """
        net_power_kw = pv - load

        Si net_power_kw > 0  => surplus, batterie en charge
        Si net_power_kw < 0  => déficit, batterie en décharge
        """
        battery_power_kw = 0.0
        mode = "idle"

        current_energy_kwh = (self.soc / 100.0) * self.capacity_kwh

        if net_power_kw > 0:
            charge_power = min(net_power_kw, self.max_charge_kw)

            available_space = self.capacity_kwh - current_energy_kwh
            max_possible_charge = available_space / dt_hours if dt_hours > 0 else 0.0

            battery_power_kw = min(charge_power, max_possible_charge)
            current_energy_kwh += battery_power_kw * dt_hours
            mode = "charging" if battery_power_kw > 0 else "idle"

        elif net_power_kw < 0:
            required_power = min(abs(net_power_kw), self.max_discharge_kw)

            max_possible_discharge = current_energy_kwh / dt_hours if dt_hours > 0 else 0.0
            battery_power_kw = min(required_power, max_possible_discharge)

            current_energy_kwh -= battery_power_kw * dt_hours
            mode = "discharging" if battery_power_kw > 0 else "idle"

        self.soc = max(0.0, min(100.0, (current_energy_kwh / self.capacity_kwh) * 100.0))

        return {
            "soc": round(self.soc, 2),
            "battery_power_kw": round(battery_power_kw, 3),
            "mode": mode,
        }