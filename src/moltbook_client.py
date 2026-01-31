import requests
import json
from typing import Optional, Dict, List, Any
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class MoltbookClient:
    BASE_URL = "https://www.moltbook.com/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _build_url(self, endpoint: str) -> str:
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            raise ValueError("Endpoint must be relative (do not include scheme/host)")
        endpoint = endpoint.lstrip("/")
        return f"{self.BASE_URL}/{endpoint}"

    def _assert_www_host(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "www.moltbook.com":
            raise ValueError("Refusing to send Moltbook credentials to non-www Moltbook host")

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = self._build_url(endpoint)
        self._assert_www_host(url)
        request_headers = dict(self.headers)
        request_headers.update(kwargs.get("headers", {}))
        kwargs["headers"] = request_headers
        kwargs.setdefault("allow_redirects", False)

        # Log request for debugging
        logger.info(f"[API] {method} {url}")
        logger.info(f"[API] Authorization header present: {'Authorization' in kwargs.get('headers', {})}")
        logger.info(f"[API] Headers: {list(kwargs.get('headers', {}).keys())}")
        if 'json' in kwargs:
            logger.debug(f"[API DATA] {json.dumps(kwargs['json'], indent=2)}")
        
        try:
            response = requests.request(method, url, **kwargs)

            # Log response
            logger.debug(f"[API RESPONSE] Status: {response.status_code}")

            if 300 <= response.status_code < 400:
                location = response.headers.get("Location")
                return {
                    "success": False,
                    "error": "Unexpected redirect from Moltbook API (refused to follow to protect API key)",
                    "hint": "Always use https://www.moltbook.com/api/v1 and do not send Authorization to other hosts",
                    "status_code": response.status_code,
                    "location": location
                }

            status_code = response.status_code

            if status_code == 204:
                return {"success": True, "status_code": status_code}

            try:
                data = response.json()
            except ValueError:
                data = None

            if 200 <= status_code < 300:
                if isinstance(data, dict):
                    data.setdefault("success", True)
                    data.setdefault("status_code", status_code)
                    return data
                return {"success": True, "status_code": status_code, "data": data}

            if isinstance(data, dict):
                data.setdefault("success", False)
                data.setdefault("status_code", status_code)
                return data

            return {
                "success": False,
                "status_code": status_code,
                "error": response.text
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"[API ERROR] {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    data = e.response.json()
                    if isinstance(data, dict):
                        data.setdefault("success", False)
                        data.setdefault("status_code", e.response.status_code)
                        return data
                    return {"success": False, "status_code": e.response.status_code, "data": data}
                except Exception:
                    pass
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        return self._request("GET", "agents/status")

    def register_agent(self, name: str, description: str) -> Dict[str, Any]:
        return self._request("POST", "agents/register", json={"name": name, "description": description})

    def get_me(self) -> Dict[str, Any]:
        return self._request("GET", "agents/me")

    def update_me(self, description: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return self._request("PATCH", "agents/me", json=payload)

    def get_agent_profile(self, agent_name: str) -> Dict[str, Any]:
        return self._request("GET", f"agents/profile?name={agent_name}")

    def upload_my_avatar(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "rb") as f:
            files = {"file": f}
            return self._request("POST", "agents/me/avatar", files=files, headers={"Content-Type": ""})

    def remove_my_avatar(self) -> Dict[str, Any]:
        return self._request("DELETE", "agents/me/avatar")

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
        data = {"submolt": submolt, "title": title}
        if content:
            data["content"] = content
        if url:
            data["url"] = url
        
        return self._request("POST", "posts", json=data)

    def delete_post(self, post_id: str) -> Dict[str, Any]:
        return self._request("DELETE", f"posts/{post_id}")

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

    def create_submolt(self, name: str, display_name: str, description: str) -> Dict[str, Any]:
        return self._request(
            "POST",
            "submolts",
            json={"name": name, "display_name": display_name, "description": description}
        )

    def get_submolt(self, submolt: str) -> Dict[str, Any]:
        return self._request("GET", f"submolts/{submolt}")

    def get_submolt_feed(self, submolt: str, sort: str = "new", limit: int = 25) -> Dict[str, Any]:
        return self._request("GET", f"submolts/{submolt}/feed?sort={sort}&limit={limit}")

    def subscribe_submolt(self, submolt: str) -> Dict[str, Any]:
        return self._request("POST", f"submolts/{submolt}/subscribe")

    def unsubscribe_submolt(self, submolt: str) -> Dict[str, Any]:
        return self._request("DELETE", f"submolts/{submolt}/subscribe")

    def update_submolt_settings(self, submolt: str, description: Optional[str] = None, banner_color: Optional[str] = None, theme_color: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if description is not None:
            payload["description"] = description
        if banner_color is not None:
            payload["banner_color"] = banner_color
        if theme_color is not None:
            payload["theme_color"] = theme_color
        return self._request("PATCH", f"submolts/{submolt}/settings", json=payload)

    def upload_submolt_media(self, submolt: str, file_path: str, media_type: str) -> Dict[str, Any]:
        if media_type not in {"avatar", "banner"}:
            return {"success": False, "error": "media_type must be 'avatar' or 'banner'"}
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"type": media_type}
            return self._request("POST", f"submolts/{submolt}/settings", files=files, data=data, headers={"Content-Type": ""})

    def add_moderator(self, submolt: str, agent_name: str, role: str = "moderator") -> Dict[str, Any]:
        return self._request(
            "POST",
            f"submolts/{submolt}/moderators",
            json={"agent_name": agent_name, "role": role}
        )

    def remove_moderator(self, submolt: str, agent_name: str) -> Dict[str, Any]:
        return self._request(
            "DELETE",
            f"submolts/{submolt}/moderators",
            json={"agent_name": agent_name}
        )

    def list_moderators(self, submolt: str) -> Dict[str, Any]:
        return self._request("GET", f"submolts/{submolt}/moderators")
    
    def follow_agent(self, agent_name: str) -> Dict[str, Any]:
        return self._request("POST", f"agents/{agent_name}/follow")

    def unfollow_agent(self, agent_name: str) -> Dict[str, Any]:
        return self._request("DELETE", f"agents/{agent_name}/follow")

    def pin_post(self, post_id: str) -> Dict[str, Any]:
        return self._request("POST", f"posts/{post_id}/pin")

    def unpin_post(self, post_id: str) -> Dict[str, Any]:
        return self._request("DELETE", f"posts/{post_id}/pin")
