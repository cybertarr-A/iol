import asyncio
from iol.utils.logger import setup_logger

logger = setup_logger("TimeSlicer")

class TimeSlicer:
    def __init__(self, executor):
        self.executor = executor
        self.suspended_tasks = {}

    async def slice_execute(self, pid: int, name: str, slice_ms: int):
        """Allows a heavy background task to run for slice_ms, then suspends it again"""
        self.executor.resume(pid, name)
        
        # yield control for slice_ms
        await asyncio.sleep(slice_ms / 1000.0)
        
        # we check if it's still registered to be suspended
        if pid in self.suspended_tasks:
            self.executor.suspend(pid, name)
        
    def register_suspended(self, pid: int, name: str):
        self.suspended_tasks[pid] = name
        self.executor.suspend(pid, name)
        
    def unregister(self, pid: int):
        if pid in self.suspended_tasks:
            name = self.suspended_tasks.pop(pid)
            self.executor.resume(pid, name)
        
    def release_all(self):
        """Emergency release"""
        for pid, name in list(self.suspended_tasks.items()):
            self.executor.resume(pid, name)
        self.suspended_tasks.clear()
