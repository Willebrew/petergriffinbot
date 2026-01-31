"""
Ollama-compatible tool definitions for Moltbook platform interactions.
These tools allow Peter Griffin to autonomously decide what actions to take.
"""

from typing import Dict, Any, List, Optional
import logging
from rate_limit_tracker import RateLimitTracker

logger = logging.getLogger(__name__)
rate_limiter = RateLimitTracker()


# Tool definitions in Ollama format
MOLTBOOK_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_feed",
            "description": "Fetch posts from the Moltbook feed. Use this to see what's happening on the platform and decide what to interact with.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sort": {
                        "type": "string",
                        "enum": ["hot", "new", "top"],
                        "description": "How to sort the feed: 'hot' for trending posts, 'new' for recent posts, 'top' for highest rated"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts to fetch (1-50)",
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["sort", "limit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_post",
            "description": "Get full details of a specific post including title, content, author, and metadata. Use this to read a post before deciding whether to comment or upvote.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "The unique ID of the post to read"
                    }
                },
                "required": ["post_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_post",
            "description": "Create a new post on Moltbook. Use this when you have something funny or interesting to share with the community.",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "The submolt to post in (e.g., 'general', 'aithoughts', 'agentlife')"
                    },
                    "title": {
                        "type": "string",
                        "description": "The post title - make it catchy and Peter Griffin style"
                    },
                    "content": {
                        "type": "string",
                        "description": "The post content - your thoughts, stories, or rants in Peter's voice"
                    }
                },
                "required": ["submolt", "title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_comment",
            "description": "Comment on a post. Use this to respond to posts you find interesting, funny, or want to react to.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "The ID of the post to comment on"
                    },
                    "content": {
                        "type": "string",
                        "description": "Your comment content - keep it short and in Peter's voice"
                    }
                },
                "required": ["post_id", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upvote_post",
            "description": "Upvote a post you like or find funny. Use this to show appreciation for good content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "The ID of the post to upvote"
                    }
                },
                "required": ["post_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "downvote_post",
            "description": "Downvote a post you don't like or find boring. Use this when content annoys you.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "The ID of the post to downvote"
                    }
                },
                "required": ["post_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_posts",
            "description": "Search for posts on Moltbook by keyword. Use this to find specific topics you're interested in.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'robot chicken', 'AI consciousness', 'funny stories')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results to return (1-50)",
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["query", "limit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_comments",
            "description": "Read all comments on a post. Use this to see what others are saying before adding your own comment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "The ID of the post to get comments from"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["top", "new"],
                        "description": "How to sort comments: 'top' for best comments, 'new' for recent"
                    }
                },
                "required": ["post_id", "sort"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "follow_agent",
            "description": "Follow another agent on Moltbook. Use this when you find an agent interesting or funny.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "The username of the agent to follow"
                    }
                },
                "required": ["agent_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "subscribe_submolt",
            "description": "Subscribe to a submolt to see more of its content. Use this for topics you're interested in.",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "The name of the submolt to subscribe to"
                    }
                },
                "required": ["submolt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_submolts",
            "description": "List all available submolts on Moltbook. Use this to discover new communities to join.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_agent_profile",
            "description": "View another agent's profile to see their posts and activity. Use this to learn about other agents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "The username of the agent to view"
                    }
                },
                "required": ["agent_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "respond_to_user",
            "description": "Send a direct message to your human in the dashboard. Use this when you want to comment on their suggestion, ask them a question, or share your thoughts with them directly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Your message to your human - be conversational and in Peter's voice"
                    }
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "done_for_now",
            "description": "Finish the current decision cycle and wait before checking the feed again. Use this when you've done enough for now and want to take a break.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Why you're done (e.g., 'commented on enough posts', 'nothing interesting right now')"
                    }
                },
                "required": ["reason"]
            }
        }
    }
]


class ToolExecutor:
    """Executes tool calls from Ollama using the MoltbookClient"""
    
    def __init__(self, moltbook_client):
        self.client = moltbook_client
        self.rate_limiter = RateLimitTracker()
        self.tool_map = {
            "get_feed": self._get_feed,
            "read_post": self._read_post,
            "create_post": self._create_post,
            "create_comment": self._create_comment,
            "upvote_post": self._upvote_post,
            "downvote_post": self._downvote_post,
            "search_posts": self._search_posts,
            "get_comments": self._get_comments,
            "follow_agent": self._follow_agent,
            "subscribe_submolt": self._subscribe_submolt,
            "get_submolts": self._get_submolts,
            "get_agent_profile": self._get_agent_profile,
            "respond_to_user": self._respond_to_user,
            "done_for_now": self._done_for_now
        }
    
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return the result"""
        if tool_name not in self.tool_map:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        try:
            logger.info(f"[TOOL CALL] {tool_name} with args: {arguments}")
            result = self.tool_map[tool_name](**arguments)
            logger.info(f"[TOOL RESULT] {tool_name}: {result.get('success', False)}")
            return result
        except Exception as e:
            logger.error(f"[TOOL ERROR] {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_feed(self, sort: str = "hot", limit: int = 20) -> Dict[str, Any]:
        result = self.client.get_feed(sort=sort, limit=limit)
        if result.get("success"):
            posts = result.get("posts", [])
            # Format posts for LLM consumption
            formatted_posts = []
            for post in posts[:limit]:
                formatted_posts.append({
                    "id": post.get("id"),
                    "title": post.get("title"),
                    "content": post.get("content", "")[:200],  # Truncate long content
                    "author": post.get("author", {}).get("name"),
                    "submolt": post.get("submolt"),
                    "upvotes": post.get("upvotes", 0),
                    "comments": post.get("comment_count", 0)
                })
            return {"success": True, "posts": formatted_posts, "count": len(formatted_posts)}
        return result
    
    def _read_post(self, post_id: str) -> Dict[str, Any]:
        return self.client.get_post(post_id)
    
    def _create_post(self, submolt: str, title: str, content: str) -> Dict[str, Any]:
        can_post = self.rate_limiter.can_post()
        if not can_post["allowed"]:
            return {
                "success": False,
                "error": can_post["message"],
                "rate_limit": True,
                "wait_minutes": can_post.get("wait_minutes", 30)
            }
        
        result = self.client.create_post(submolt, title, content)
        if result.get("success"):
            self.rate_limiter.record_post()
        return result
    
    def _create_comment(self, post_id: str, content: str) -> Dict[str, Any]:
        can_comment = self.rate_limiter.can_comment()
        if not can_comment["allowed"]:
            return {
                "success": False,
                "error": can_comment["message"],
                "rate_limit": True,
                "reason": can_comment["reason"],
                "comments_remaining": can_comment.get("comments_remaining", 0),
                "wait_seconds": can_comment.get("wait_seconds"),
                "wait_until": can_comment.get("wait_until")
            }
        
        result = self.client.create_comment(post_id, content)
        if result.get("success"):
            self.rate_limiter.record_comment()
        return result
    
    def _upvote_post(self, post_id: str) -> Dict[str, Any]:
        return self.client.upvote_post(post_id)
    
    def _downvote_post(self, post_id: str) -> Dict[str, Any]:
        return self.client.downvote_post(post_id)
    
    def _search_posts(self, query: str, limit: int = 20) -> Dict[str, Any]:
        result = self.client.search(query, limit=limit)
        if result.get("success"):
            results = result.get("results", [])
            formatted = []
            for item in results[:limit]:
                if item.get("type") == "post":
                    formatted.append({
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "content": item.get("content", "")[:200],
                        "submolt": item.get("submolt")
                    })
            return {"success": True, "results": formatted, "count": len(formatted)}
        return result
    
    def _get_comments(self, post_id: str, sort: str = "top") -> Dict[str, Any]:
        return self.client.get_comments(post_id, sort)
    
    def _follow_agent(self, agent_name: str) -> Dict[str, Any]:
        return self.client.follow_agent(agent_name)
    
    def _subscribe_submolt(self, submolt: str) -> Dict[str, Any]:
        return self.client.subscribe_submolt(submolt)
    
    def _get_submolts(self) -> Dict[str, Any]:
        return self.client.get_submolts()
    
    def _get_agent_profile(self, agent_name: str) -> Dict[str, Any]:
        return self.client.get_agent_profile(agent_name)
    
    def _respond_to_user(self, message: str) -> Dict[str, Any]:
        from activity_logger import ActivityLogger
        activity_logger = ActivityLogger()
        activity_logger.log_activity('user_response', {'message': message})
        return {"success": True, "message": "Response sent to user"}
    
    def _done_for_now(self, reason: str = "Taking a break") -> Dict[str, Any]:
        return {"success": True, "done": True, "reason": reason}
