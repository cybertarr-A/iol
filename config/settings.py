import yaml
import os
from iol.utils.logger import setup_logger

logger = setup_logger("ConfigLoader")

class Config:
    def __init__(self, config_file="config_example.yaml"):
        self.config_file = config_file
        self.config_data = self._load()
        # Allows programmatic overriding of thresholds
        self.dynamic_overrides = {}

    def _load(self):
        if not os.path.exists(self.config_file):
            logger.warning(f"Config file {self.config_file} not found. Using defaults.")
            return {}
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def get(self, key, default=None):
        if key in self.dynamic_overrides:
            return self.dynamic_overrides[key]
            
        keys = key.split('.')
        val = self.config_data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set_dynamic(self, key, value):
        """Allows AI / Decision engine to update active thresholds at runtime"""
        self.dynamic_overrides[key] = value
        logger.debug(f"Dynamic config override: {key} = {value}")
