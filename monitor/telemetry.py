import psutil
import asyncio
from typing import Dict, Any, List
from iol.utils.logger import setup_logger

logger = setup_logger("Telemetry")

class TelemetryMonitor:
    def __init__(self):
        # Initialize CPU percent blocking initially to set the baseline
        psutil.cpu_percent(interval=0.1)

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Returns baseline health metrics asynchronously."""
        await asyncio.sleep(0.0) 
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        
        return {
            "cpu_percent": cpu,
            "memory_percent": mem
        }

    async def get_heavy_processes(self, cpu_thresh: float) -> List[Dict[str, Any]]:
        """Identify heavy processes consuming more CPU than the threshold"""
        heavy = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                # CPU percent since last call
                # Note: first call returns 0.0, so this needs continuous polling to be accurate
                cpu_p = p.cpu_percent(interval=None)
                if cpu_p is not None and cpu_p > cpu_thresh:
                    info = p.info
                    info['cpu_percent_live'] = cpu_p
                    heavy.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return heavy

    async def get_all_processes(self) -> List[Dict[str, Any]]:
        """Snapshot of all processes to feed the behavior engine"""
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'status']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return procs
