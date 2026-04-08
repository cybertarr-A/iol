import collections
from iol.utils.logger import setup_logger

logger = setup_logger("Predictor")

class WorkloadPredictor:
    def __init__(self, window_size=5):
        # Keeps last N samples
        self.cpu_history = collections.deque(maxlen=window_size)
    
    def add_sample(self, cpu_val: float):
        self.cpu_history.append(cpu_val)

    def is_spike_imminent(self) -> bool:
        """
        Detects if a CPU spike is imminent. 
        True if the trend is accelerating sharply.
        """
        if len(self.cpu_history) < 3:
            return False
            
        history = list(self.cpu_history)
        
        # Calculate rates of change
        deltas = [history[i] - history[i-1] for i in range(1, len(history))]
        
        # If the last two deltas are highly positive, we are spiking
        if len(deltas) >= 2:
            if deltas[-1] > 15.0 and deltas[-2] > 10.0:
                logger.warning(f"Spike imminent! Recent CPU deltas: {deltas[-2:]}")
                return True
                
        # Or if average is already consistently high
        avg = sum(history) / len(history)
        if avg > 80.0:
            return True
            
        return False
