from iol.storage.db import BehaviorDB
from iol.utils.logger import setup_logger

logger = setup_logger("BehaviorEngine")

class BehaviorEngine:
    def __init__(self, db_path="iol_behavior.db"):
        self.db = BehaviorDB(db_path=db_path)
        # Priority mapping is cached to reduce DB reads on hot path
        self.priority_map = self.db.get_priority_map()
        self.iteration = 0

    def update_snapshot(self, running_processes: list, poll_interval_sec: float):
        """
        Updates the learning engine with background interactions.
        We simulate active behavior tracking.
        """
        self.iteration += 1
        # DB writes are expensive, only do it periodically
        # (e.g. every 10 ticks)
        if self.iteration % 10 != 0:
            return

        for p in running_processes:
            name = p.get('name')
            if not name:
                continue
                
            # If process is running, calculate a mild priority bump.
            priority_delta = 0.001
            # We charge it as 10 * poll_interval_sec since we batch the updates
            self.db.upsert_process(name, poll_interval_sec * 10, priority_delta)

    def get_priority(self, process_name: str) -> float:
        """Fetch custom learned priority (higher = more protected)"""
        # Periodic refresh could go here
        if self.iteration % 100 == 0:
             self.priority_map = self.db.get_priority_map()
        return self.priority_map.get(process_name, 0.0)
