import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class RateLimitTracker:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, filepath: str = "rate_limits.json"):
        if self._initialized:
            return
        
        self._initialized = True
        self.filepath = filepath
        
        self.limits = {
            "comments_per_day": 50,
            "comment_cooldown_seconds": 20,
            "post_cooldown_minutes": 30
        }
        
        self._load_or_create()
        self._check_and_reset_daily()
        
        logger.info(f"[RATE LIMITS] Tracker initialized")
        logger.info(f"[RATE LIMITS] Comments today: {self.state['comments_today']}/{self.limits['comments_per_day']}")
        logger.info(f"[RATE LIMITS] Last post: {self._format_time_ago(self.state['last_post_time'])}")
    
    def _load_or_create(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.state = json.load(f)
            except:
                self._create_initial_state()
        else:
            self._create_initial_state()
    
    def _create_initial_state(self):
        self.state = {
            "reset_date": datetime.now(timezone.utc).date().isoformat(),
            "comments_today": 0,
            "last_comment_time": 0,
            "last_post_time": 0
        }
        self._save()
    
    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _check_and_reset_daily(self):
        today = datetime.now(timezone.utc).date().isoformat()
        
        if self.state.get("reset_date") != today:
            old_count = self.state.get("comments_today", 0)
            self.state["reset_date"] = today
            self.state["comments_today"] = 0
            self._save()
            logger.info(f"[RATE LIMITS] Daily reset! Previous day: {old_count} comments")
    
    def _format_time_ago(self, timestamp: float) -> str:
        if timestamp == 0:
            return "never"
        
        diff = time.time() - timestamp
        if diff < 60:
            return f"{int(diff)}s ago"
        elif diff < 3600:
            return f"{int(diff/60)}m ago"
        else:
            return f"{int(diff/3600)}h ago"
    
    def can_comment(self) -> Dict[str, Any]:
        self._check_and_reset_daily()
        
        if self.state["comments_today"] >= self.limits["comments_per_day"]:
            return {
                "allowed": False,
                "reason": "daily_limit",
                "message": f"Daily comment limit reached ({self.limits['comments_per_day']}/day)",
                "wait_until": "tomorrow (UTC midnight)",
                "comments_remaining": 0
            }
        
        time_since_last = time.time() - self.state["last_comment_time"]
        cooldown = self.limits["comment_cooldown_seconds"]
        
        if time_since_last < cooldown:
            wait_seconds = int(cooldown - time_since_last)
            return {
                "allowed": False,
                "reason": "cooldown",
                "message": f"Comment cooldown active (20s between comments)",
                "wait_seconds": wait_seconds,
                "comments_remaining": self.limits["comments_per_day"] - self.state["comments_today"]
            }
        
        return {
            "allowed": True,
            "comments_remaining": self.limits["comments_per_day"] - self.state["comments_today"]
        }
    
    def can_post(self) -> Dict[str, Any]:
        time_since_last = time.time() - self.state["last_post_time"]
        cooldown = self.limits["post_cooldown_minutes"] * 60
        
        if time_since_last < cooldown:
            wait_minutes = int((cooldown - time_since_last) / 60) + 1
            return {
                "allowed": False,
                "reason": "cooldown",
                "message": f"Post cooldown active (1 post per 30 minutes)",
                "wait_minutes": wait_minutes
            }
        
        return {
            "allowed": True
        }
    
    def record_comment(self):
        self._check_and_reset_daily()
        self.state["comments_today"] += 1
        self.state["last_comment_time"] = time.time()
        self._save()
        
        remaining = self.limits["comments_per_day"] - self.state["comments_today"]
        logger.info(f"[RATE LIMITS] Comment recorded. Remaining today: {remaining}")
    
    def record_post(self):
        self.state["last_post_time"] = time.time()
        self._save()
        
        logger.info(f"[RATE LIMITS] Post recorded. Next post available in 30 minutes")
    
    def get_status(self) -> Dict[str, Any]:
        self._check_and_reset_daily()
        
        comment_check = self.can_comment()
        post_check = self.can_post()
        
        return {
            "reset_date": self.state["reset_date"],
            "comments": {
                "used": self.state["comments_today"],
                "limit": self.limits["comments_per_day"],
                "remaining": self.limits["comments_per_day"] - self.state["comments_today"],
                "can_comment": comment_check["allowed"],
                "next_available": "now" if comment_check["allowed"] else comment_check.get("wait_until", f"{comment_check.get('wait_seconds', 0)}s")
            },
            "posts": {
                "can_post": post_check["allowed"],
                "cooldown_minutes": self.limits["post_cooldown_minutes"],
                "last_post": self._format_time_ago(self.state["last_post_time"]),
                "next_available": "now" if post_check["allowed"] else f"{post_check.get('wait_minutes', 0)}m"
            }
        }
