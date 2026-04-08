import os
import signal
import psutil
from iol.utils.logger import setup_logger

logger = setup_logger("Executor")

class ProcessExecutor:
    def __init__(self, whitelist: list, dry_run: bool = True):
        self.whitelist = set(whitelist)
        self.dry_run = dry_run

    def is_protected(self, name: str, custom_score: float = 0.0) -> bool:
        if not name:
            return True
        for w in self.whitelist:
            if w.lower() in name.lower():
                return True
        # If behavior engine gave it a high score (>50), treat as protected
        if custom_score > 50.0:
            return True
        return False

    def suspend(self, pid: int, name: str, custom_score: float = 0.0):
        if self.is_protected(name, custom_score):
            return

        logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Suspending {name} ({pid})")
        if not self.dry_run:
            try:
                os.kill(pid, signal.SIGSTOP)
            except Exception as e:
                logger.debug(f"Failed to suspend {pid}: {e}")

    def resume(self, pid: int, name: str):
        logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Resuming {name} ({pid})")
        if not self.dry_run:
            try:
                os.kill(pid, signal.SIGCONT)
            except Exception as e:
                logger.debug(f"Failed to resume {pid}: {e}")

    def renice(self, pid: int, name: str, priority_val: int = 19, custom_score: float = 0.0):
        if self.is_protected(name, custom_score):
            return

        logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Renicing {name} ({pid}) to {priority_val}")
        if not self.dry_run:
            try:
                p = psutil.Process(pid)
                p.nice(priority_val)
            except psutil.AccessDenied:
                logger.debug(f"Access denied renicing {pid}")
            except Exception as e:
                logger.debug(f"Failed to renice {pid}: {e}")
