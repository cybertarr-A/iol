import os
import glob
from iol.utils.logger import setup_logger

logger = setup_logger("ThermalSensor")

class ThermalMonitor:
    def __init__(self):
        self.thermal_zones = glob.glob('/sys/class/thermal/thermal_zone*/temp')
        if not self.thermal_zones:
            logger.warning("No Linux thermal zones found in /sys/class/thermal. Falling back to safe defaults.")

    def get_max_temperature(self) -> float:
        """Returns max systemic temperature across all found sensors in Celsius."""
        max_temp = 0.0
        for zone in self.thermal_zones:
            try:
                with open(zone, 'r') as f:
                    # typical thermal zones store temperature in millidegrees Celsius
                    temp_str = f.read().strip()
                    if temp_str.isdigit():
                        temp_celsius = int(temp_str) / 1000.0
                        if temp_celsius > max_temp:
                            max_temp = temp_celsius
            except Exception:
                pass
        return max_temp

    def is_throttling_risk(self, threshold: float) -> bool:
        t = self.get_max_temperature()
        if t >= threshold:
            logger.warning(f"Thermal risk detected! Temp: {t:.1f}C (Allowed: {threshold}C)")
            return True
        return False
