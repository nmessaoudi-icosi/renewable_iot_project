import random


class LoadSimulator:
    def __init__(self, base_load_kw: float = 2.0):
        self.base_load_kw = base_load_kw

    def generate_load(self, hour: float) -> float:
        """
        Simule la consommation:
        - plus faible la nuit
        - moyenne le jour
        - plus forte le soir
        """
        if 0 <= hour < 6:
            factor = 0.6
        elif 6 <= hour < 12:
            factor = 0.9
        elif 12 <= hour < 18:
            factor = 1.0
        else:
            factor = 1.4

        noise = random.uniform(-0.2, 0.4)
        load = self.base_load_kw * factor + noise

        return round(max(0.3, load), 3)