import requests
import time
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MoltbookClient:
    BASE_URL = "https://www.moltbook.com/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.last_post_time = 0
        self.post_cooldown = 30 * 60
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint}"
        kwargs.setdefault('headers', {}).update(self.headers)
        
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e.response, 'json'):
                try:
                    return e.response.json()
                except:
                    pass
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        return self._request("GET", "agents/status")
    
    def get_me(self) -> Dict[str, Any]:
        return self._request("GET", "agents/me")
    
    def get_feed(self, sort: str = "hot", limit: int = 25) -> Dict[str, Any]:
        return self._request("GET", f"feed?sort={sort}&limit={limit}")
    
    def get_posts(self, sort: str = "hot", limit: int = 25, submolt: Optional[str] = None) -> Dict[str, Any]:
        params = f"sort={sort}&limit={limit}"
        if submolt:
            params += f"&submolt={submolt}"
        return self._request("GET", f"posts?{params}")
    
    def get_post(self, post_id: str) -> Dict[str, Any]:
        return self._request("GET", f"posts/{post_id}")
    
    def create_post(self, submolt: str, title: str, content: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
        current_time = time.time()
        if current_time - self.last_post_time < self.post_cooldown:
            wait_time = self.post_cooldown - (current_time - self.last_post_time)
            logger.warning(f"Post cooldown active. Wait {wait_time/60:.1f} more minutes")
            return {"success": False, "error": "Post cooldown active", "retry_after_minutes": wait_time/60}
        
        data = {"submolt": submolt, "title": title}
        if content:
            data["content"] = content
        if url:
            data["url"] = url
        
        result = self._request("POST", "posts", json=data)
        if result.get("success"):
            self.last_post_time = current_time
        return result
    
    def create_comment(self, post_id: str, content: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        data = {"content": content}
        if parent_id:
            data["parent_id"] = parent_id
        return self._request("POST", f"posts/{post_id}/comments", json=data)
    
    def get_comments(self, post_id: str, sort: str = "top") -> Dict[str, Any]:
        return self._request("GET", f"posts/{post_id}/comments?sort={sort}")
    
    def upvote_post(self, post_id: str) -> Dict[str, Any]:
        return self._request("POST", f"posts/{post_id}/upvote")
    
    def downvote_post(self, post_id: str) -> Dict[str, Any]:
        return self._request("POST", f"posts/{post_id}/downvote")
    
    def upvote_comment(self, comment_id: str) -> Dict[str, Any]:
        return self._request("POST", f"comments/{comment_id}/upvote")
    
    def search(self, query: str, search_type: str = "all", limit: int = 20) -> Dict[str, Any]:
        return self._request("GET", f"search?q={requests.utils.quote(query)}&type={search_type}&limit={limit}")
    
    def get_submolts(self) -> Dict[str, Any]:
        return self._request("GET", "submolts")
    
    def subscribe_submolt(self, submolt: str) -> Dict[str, Any]:
        return self._request("POST", f"submolts/{submolt}/subscribe")
    
    def follow_agent(self, agent_name: str) -> Dict[str, Any]:
        return self._request("POST", f"agents/{agent_name}/follow")
    
    def get_agent_profile(self, agent_name: str) -> Dict[str, Any]:
        return self._request("GET", f"agents/profile?name={agent_name}")
