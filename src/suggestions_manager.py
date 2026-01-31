import json
import os
import threading
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class SuggestionsManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, filepath: str = "suggestions.json"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, filepath: str = "suggestions.json"):
        if self._initialized:
            return
            
        self._initialized = True
        self.filepath = filepath
        self.file_lock = threading.Lock()
        self._ensure_file_exists()
        logger.info(f"[SUGGESTIONS] Initialized with file: {filepath}")
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump([], f)
    
    def _read_suggestions(self) -> List[Dict[str, Any]]:
        with self.file_lock:
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
    
    def _write_suggestions(self, suggestions: List[Dict[str, Any]]):
        with self.file_lock:
            with open(self.filepath, 'w') as f:
                json.dump(suggestions, f, indent=2)
    
    def add_suggestion(self, text: str) -> Dict[str, Any]:
        suggestions = self._read_suggestions()
        
        suggestion = {
            "id": int(time.time() * 1000),
            "text": text,
            "timestamp": time.time(),
            "status": "pending"
        }
        
        suggestions.append(suggestion)
        self._write_suggestions(suggestions)
        
        logger.info(f"[SUGGESTIONS] Added: {text[:50]}...")
        return suggestion
    
    def get_pending(self) -> List[Dict[str, Any]]:
        suggestions = self._read_suggestions()
        return [s for s in suggestions if s.get("status") == "pending"]
    
    def get_all(self) -> List[Dict[str, Any]]:
        return self._read_suggestions()
    
    def mark_seen(self, suggestion_id: int):
        suggestions = self._read_suggestions()
        
        for suggestion in suggestions:
            if suggestion.get("id") == suggestion_id:
                suggestion["status"] = "seen"
                suggestion["seen_at"] = time.time()
                break
        
        self._write_suggestions(suggestions)
        logger.info(f"[SUGGESTIONS] Marked as seen: {suggestion_id}")
    
    def mark_all_pending_as_seen(self):
        suggestions = self._read_suggestions()
        seen_count = 0
        
        remaining_suggestions = []
        for suggestion in suggestions:
            if suggestion.get("status") == "pending":
                seen_count += 1
            else:
                remaining_suggestions.append(suggestion)
        
        self._write_suggestions(remaining_suggestions)
        logger.info(f"[SUGGESTIONS] Removed {seen_count} seen suggestions")
        return seen_count
