import asyncio
import sys
import signal
import os

# Ensure the parent directory is in the Python path so 'iol' module can be resolved
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from iol.config.settings import Config
from iol.utils.logger import setup_logger
from iol.cli.parser import get_parser
from iol.monitor.telemetry import TelemetryMonitor
from iol.prediction.trends import WorkloadPredictor
from iol.learning.behavior import BehaviorEngine
from iol.thermal.sensors import ThermalMonitor
from iol.executor.controller import ProcessExecutor
from iol.scheduler.timeslicer import TimeSlicer
from iol.decision.brain import DecisionBrain

# Setup early logging
main_logger = setup_logger("IOL_Main")

class IOLDaemon:
    def __init__(self, config_path: str, dry_run: bool, debug: bool):
        self.config = Config(config_path)
        if debug:
             main_logger.setLevel("DEBUG")
        
        self.dry_run = dry_run or self.config.get('system.dry_run', True)
        self.poll_interval = self.config.get('system.update_interval_sec', 1.0)
        
        self.monitor = TelemetryMonitor()
        self.predictor = WorkloadPredictor(window_size=5)
        self.behavior = BehaviorEngine(db_path=self.config.get('system.db_path', 'iol_behavior.db'))
        self.thermal = ThermalMonitor()
        
        whitelist = self.config.get('executor.whitelist', [])
        self.executor = ProcessExecutor(whitelist=whitelist, dry_run=self.dry_run)
        self.timeslicer = TimeSlicer(self.executor)
        
        self.brain = DecisionBrain(
            config=self.config,
            executor=self.executor,
            timeslicer=self.timeslicer,
            thermal=self.thermal,
            predictor=self.predictor,
            behavior=self.behavior
        )
        self.running = True

    def _signal_handler(self, sig, frame):
        main_logger.info("Termination signal received. Shutting down IOL safely...")
        self.running = False
        self.timeslicer.release_all()
        sys.exit(0)

    async def _loop(self):
        main_logger.info(f"IOL Daemon started. Dry run={self.dry_run}, Interval={self.poll_interval}s")
        cpu_threshold = self.config.get('monitor.cpu_spike_threshold', 80.0)
        
        while self.running:
            try:
                # 1. Gather Telemetry
                metrics = await self.monitor.get_system_metrics()
                all_procs = await self.monitor.get_all_processes()
                
                # 2. Update Behavior Learning
                self.behavior.update_snapshot(all_procs, self.poll_interval)
                
                # 3. Decision Brain handles Heavy processes and thermal/prediction
                heavy_procs = await self.monitor.get_heavy_processes(cpu_threshold)
                await self.brain.evaluate_and_act(metrics, heavy_procs)
                
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                main_logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(self.poll_interval)

    def start(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            asyncio.run(self._loop())
        except KeyboardInterrupt:
            self._signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    
    daemon = IOLDaemon(
        config_path=args.config,
        dry_run=args.dry_run,
        debug=args.debug
    )
    daemon.start()
