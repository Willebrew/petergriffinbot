import time
import threading
from typing import Dict, Any, List
from collections import deque
import queue
import logging

logger = logging.getLogger(__name__)


class ActivityLogger:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.activities = deque(maxlen=100)
        self.activities_lock = threading.Lock()
        self.subscribers = []
        self.subscribers_lock = threading.Lock()
        logger.info("[ACTIVITY LOGGER] Initialized")
    
    def log_activity(self, activity_type: str, details: Dict[str, Any]):
        activity = {
            "timestamp": time.time(),
            "type": activity_type,
            "details": details
        }
        
        with self.activities_lock:
            self.activities.append(activity)
        
        with self.subscribers_lock:
            for sub_queue in self.subscribers:
                try:
                    sub_queue.put_nowait(activity)
                except queue.Full:
                    pass
        
        logger.debug(f"[ACTIVITY] {activity_type}: {details}")
    
    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.activities_lock:
            activities_list = list(self.activities)
            return activities_list[-limit:] if len(activities_list) > limit else activities_list
    
    def subscribe(self) -> queue.Queue:
        sub_queue = queue.Queue(maxsize=50)
        with self.subscribers_lock:
            self.subscribers.append(sub_queue)
        logger.info(f"[ACTIVITY LOGGER] New subscriber. Total: {len(self.subscribers)}")
        return sub_queue
    
    def unsubscribe(self, sub_queue: queue.Queue):
        with self.subscribers_lock:
            if sub_queue in self.subscribers:
                self.subscribers.remove(sub_queue)
        logger.info(f"[ACTIVITY LOGGER] Subscriber removed. Total: {len(self.subscribers)}")
