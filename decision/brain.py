from iol.utils.logger import setup_logger
import asyncio

logger = setup_logger("CoreBrain")

class DecisionBrain:
    def __init__(self, config, executor, timeslicer, thermal, predictor, behavior):
        self.config = config
        self.executor = executor
        self.timeslicer = timeslicer
        self.thermal = thermal
        self.predictor = predictor
        self.behavior = behavior

    async def evaluate_and_act(self, system_metrics: dict, heavy_procs: list):
        """
        IF user active: prioritize foreground apps (implicit by nice-ing background)
        IF spike predicted: pre-emptively optimize
        IF thermal risk: aggressive throttle
        """
        cpu_val = system_metrics.get('cpu_percent', 0.0)
        self.predictor.add_sample(cpu_val)
        
        spike_imminent = self.predictor.is_spike_imminent()
        thermal_risk = self.thermal.is_throttling_risk(self.config.get('monitor.thermal_threshold', 75.0))
        
        if spike_imminent:
            logger.warning("BRAIN: Short-term CPU spike predicted! Pre-throttling background processes.")
            
        if thermal_risk:
            logger.warning("BRAIN: Thermal risk detected! Enforcing aggressive moderation.")

        # For heavy procs, apply rules
        is_stressed = spike_imminent or thermal_risk or cpu_val > self.config.get('monitor.cpu_spike_threshold', 80.0)
        
        if is_stressed:
            for hp in heavy_procs:
                pid = hp['pid']
                name = hp['name']
                priority_score = self.behavior.get_priority(name)
                
                if self.executor.is_protected(name, custom_score=priority_score):
                    continue
                    
                # Action: Renice or Suspend/Timeslice
                if thermal_risk or spike_imminent:
                    self.timeslicer.register_suspended(pid, name)
                    # allow small slice
                    slice_ms = self.config.get('executor.max_timeslice_ms', 50)
                    asyncio.create_task(self.timeslicer.slice_execute(pid, name, slice_ms))
                else:
                    self.executor.renice(pid, name, priority_val=19, custom_score=priority_score)
        else:
            # Not stressed, release throttles
            self.timeslicer.release_all()
