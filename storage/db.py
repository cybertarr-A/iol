import sqlite3
import time
import os
from iol.utils.logger import setup_logger

logger = setup_logger("StorageDB")

class BehaviorDB:
    def __init__(self, db_path="iol_behavior.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS app_behavior (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        process_name TEXT UNIQUE NOT NULL,
                        total_foreground_time_sec REAL DEFAULT 0.0,
                        run_frequency INTEGER DEFAULT 1,
                        last_seen_epoch REAL,
                        priority_score REAL DEFAULT 0.0
                    )
                ''')
                conn.commit()
                logger.debug(f"Initialized DB at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize DB: {e}")

    def upsert_process(self, process_name: str, foreground_time_delta: float, priority_score_delta: float = 0.0):
        try:
            now = time.time()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO app_behavior 
                    (process_name, total_foreground_time_sec, run_frequency, last_seen_epoch, priority_score)
                    VALUES (?, ?, 1, ?, ?)
                    ON CONFLICT(process_name) DO UPDATE SET
                        total_foreground_time_sec = total_foreground_time_sec + ?,
                        run_frequency = run_frequency + 1,
                        last_seen_epoch = ?,
                        priority_score = priority_score + ?
                ''', (
                    process_name, foreground_time_delta, now, priority_score_delta,
                    foreground_time_delta, now, priority_score_delta
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to upsert process {process_name}: {e}")

    def get_priority_map(self) -> dict:
        priority_map = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT process_name, priority_score FROM app_behavior')
                for row in cursor.fetchall():
                    priority_map[row[0]] = row[1]
        except Exception as e:
            logger.error(f"Failed to get priority map: {e}")
        return priority_map
