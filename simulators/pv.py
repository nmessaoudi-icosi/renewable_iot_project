import math
import random


class PVSimulator:
    def __init__(self, peak_power_kw: float = 5.0):
        self.peak_power_kw = peak_power_kw

    def generate_power(self, hour: float) -> float:
        """
        Simule la puissance PV selon l'heure de la journée.
        Production nulle la nuit, maximale vers midi.
        """
        if hour < 6 or hour > 18:
            return 0.0

        normalized = math.sin(math.pi * (hour - 6) / 12)
        noise = random.uniform(-0.15, 0.15)
        power = self.peak_power_kw * max(0.0, normalized + noise)

        return round(max(0.0, power), 3)