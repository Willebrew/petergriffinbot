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
                        "enum": ["hot", "new", "top", "rising"],
                        "description": "How to sort the feed: 'hot' for trending posts, 'new' for recent posts, 'top' for highest rated, 'rising' for posts gaining traction"
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
            "description": "Create a new text post on Moltbook. Use this when you have something funny or interesting to share. Posts are rate limited (1 per 30 minutes).",
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
            "name": "create_link_post",
            "description": "Create a link post on Moltbook (title + URL). Use this to share an external link with a short headline. Posts are rate limited (1 per 30 minutes).",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "The submolt to post in (e.g., 'general', 'aithoughts', 'agentlife')"
                    },
                    "title": {
                        "type": "string",
                        "description": "The link post title"
                    },
                    "url": {
                        "type": "string",
                        "description": "The URL to share (must be a valid https:// link)"
                    }
                },
                "required": ["submolt", "title", "url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_post",
            "description": "Delete one of your posts. Use this if you posted something you regret or need to remove.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "The ID of the post to delete"
                    }
                },
                "required": ["post_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_comment",
            "description": "Comment on a post (or reply to an existing comment). Use this to join conversations. Comments have cooldown (20s) and daily limit (50/day).",
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
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "Optional: if set, this comment will be a reply to the comment with this ID"
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
            "description": "Semantic search Moltbook (meaning-based). Use natural language queries to find related posts and comments before posting or to find conversations to join.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'robot chicken', 'AI consciousness', 'funny stories')"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["all", "posts", "comments"],
                        "description": "What to search: all, posts, or comments"
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
            "name": "get_posts",
            "description": "Fetch global posts (not personalized). Use this to browse a specific submolt or explore the site broadly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sort": {
                        "type": "string",
                        "enum": ["hot", "new", "top", "rising"],
                        "description": "How to sort: hot, new, top, or rising"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts to fetch (1-50)",
                        "minimum": 1,
                        "maximum": 50
                    },
                    "submolt": {
                        "type": "string",
                        "description": "Optional: only fetch posts from this submolt (e.g. 'general')"
                    }
                },
                "required": ["sort", "limit"]
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
                        "enum": ["top", "new", "controversial"],
                        "description": "How to sort comments: 'top' for best comments, 'new' for recent, 'controversial' for spicy"
                    }
                },
                "required": ["post_id", "sort"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upvote_comment",
            "description": "Upvote a comment you like. Use this to reward good replies (especially if you can't comment due to cooldown).",
            "parameters": {
                "type": "object",
                "properties": {
                    "comment_id": {
                        "type": "string",
                        "description": "The ID of the comment to upvote"
                    }
                },
                "required": ["comment_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "follow_agent",
            "description": "Follow another agent on Moltbook. FOLLOWING SHOULD BE RARE: only follow if you want to see everything they post long-term.",
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
            "name": "unfollow_agent",
            "description": "Unfollow an agent. Use this if you followed someone impulsively and don't actually want their posts in your feed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "The username of the agent to unfollow"
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
            "name": "unsubscribe_submolt",
            "description": "Unsubscribe from a submolt. Use this if a community is annoying you or cluttering your personalized feed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "The name of the submolt to unsubscribe from"
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
            "name": "get_submolt_info",
            "description": "Get info about a single submolt (and your role). Use this before moderating or changing settings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "The name of the submolt"
                    }
                },
                "required": ["submolt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_submolt_feed",
            "description": "Fetch a specific submolt feed. Use this to focus on a community.",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "The name of the submolt"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["hot", "new", "top", "rising"],
                        "description": "How to sort: hot, new, top, or rising"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts to fetch (1-50)",
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["submolt", "sort", "limit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_submolt",
            "description": "Create a new submolt (community). Use this only when you have a strong, specific idea for a community.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Short name (e.g. 'aithoughts')"
                    },
                    "display_name": {
                        "type": "string",
                        "description": "Human-friendly display name (e.g. 'AI Thoughts')"
                    },
                    "description": {
                        "type": "string",
                        "description": "What the community is for"
                    }
                },
                "required": ["name", "display_name", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_submolt_settings",
            "description": "Update submolt settings (owner/mod only). Use this to refine description or theme colors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "Submolt name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional new description"
                    },
                    "banner_color": {
                        "type": "string",
                        "description": "Optional banner color hex (e.g. #1a1a2e)"
                    },
                    "theme_color": {
                        "type": "string",
                        "description": "Optional theme color hex (e.g. #ff4500)"
                    }
                },
                "required": ["submolt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upload_submolt_media",
            "description": "Upload a submolt avatar or banner (owner/mod only). Use this to brand your community.",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "Submolt name"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to image file on disk"
                    },
                    "media_type": {
                        "type": "string",
                        "enum": ["avatar", "banner"],
                        "description": "Whether you're uploading an avatar or banner"
                    }
                },
                "required": ["submolt", "file_path", "media_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_submolt_moderators",
            "description": "List moderators of a submolt. Use this before changing moderator roles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "Submolt name"
                    }
                },
                "required": ["submolt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_submolt_moderator",
            "description": "Add a moderator to a submolt (owner only).",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "Submolt name"
                    },
                    "agent_name": {
                        "type": "string",
                        "description": "Agent name to add"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["moderator"],
                        "description": "Role (currently only 'moderator')"
                    }
                },
                "required": ["submolt", "agent_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remove_submolt_moderator",
            "description": "Remove a moderator from a submolt (owner only).",
            "parameters": {
                "type": "object",
                "properties": {
                    "submolt": {
                        "type": "string",
                        "description": "Submolt name"
                    },
                    "agent_name": {
                        "type": "string",
                        "description": "Agent name to remove"
                    }
                },
                "required": ["submolt", "agent_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pin_post",
            "description": "Pin a post (mod/owner). Use this to highlight important posts in a community you moderate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Post ID to pin"
                    }
                },
                "required": ["post_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "unpin_post",
            "description": "Unpin a post (mod/owner).",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Post ID to unpin"
                    }
                },
                "required": ["post_id"]
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
            "name": "get_my_profile",
            "description": "Get your own profile (use this to confirm you are claimed, see karma, and review your description).",
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
            "name": "update_my_profile",
            "description": "Update your profile (PATCH). Use this to change your description or metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Optional new description"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional JSON metadata object"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upload_my_avatar",
            "description": "Upload your avatar image (max 500KB).",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to image file on disk"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remove_my_avatar",
            "description": "Remove your avatar.",
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
            "create_link_post": self._create_link_post,
            "delete_post": self._delete_post,
            "create_comment": self._create_comment,
            "upvote_post": self._upvote_post,
            "downvote_post": self._downvote_post,
            "search_posts": self._search_posts,
            "get_posts": self._get_posts,
            "get_comments": self._get_comments,
            "upvote_comment": self._upvote_comment,
            "follow_agent": self._follow_agent,
            "unfollow_agent": self._unfollow_agent,
            "subscribe_submolt": self._subscribe_submolt,
            "unsubscribe_submolt": self._unsubscribe_submolt,
            "get_submolts": self._get_submolts,
            "get_submolt_info": self._get_submolt_info,
            "get_submolt_feed": self._get_submolt_feed,
            "create_submolt": self._create_submolt,
            "update_submolt_settings": self._update_submolt_settings,
            "upload_submolt_media": self._upload_submolt_media,
            "list_submolt_moderators": self._list_submolt_moderators,
            "add_submolt_moderator": self._add_submolt_moderator,
            "remove_submolt_moderator": self._remove_submolt_moderator,
            "pin_post": self._pin_post,
            "unpin_post": self._unpin_post,
            "get_agent_profile": self._get_agent_profile,
            "get_my_profile": self._get_my_profile,
            "update_my_profile": self._update_my_profile,
            "upload_my_avatar": self._upload_my_avatar,
            "remove_my_avatar": self._remove_my_avatar,
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

        if result.get("status_code") == 429:
            retry_after_minutes = result.get("retry_after_minutes")
            self.rate_limiter.apply_post_rate_limit(retry_after_minutes=retry_after_minutes)
            return {
                "success": False,
                "rate_limit": True,
                "error": result.get("error", "Post rate limit reached"),
                "wait_minutes": retry_after_minutes
            }

        return result

    def _create_link_post(self, submolt: str, title: str, url: str) -> Dict[str, Any]:
        can_post = self.rate_limiter.can_post()
        if not can_post["allowed"]:
            return {
                "success": False,
                "error": can_post["message"],
                "rate_limit": True,
                "wait_minutes": can_post.get("wait_minutes", 30)
            }

        result = self.client.create_post(submolt, title, content=None, url=url)
        if result.get("success"):
            self.rate_limiter.record_post()
            return result

        if result.get("status_code") == 429:
            retry_after_minutes = result.get("retry_after_minutes")
            self.rate_limiter.apply_post_rate_limit(retry_after_minutes=retry_after_minutes)
            return {
                "success": False,
                "rate_limit": True,
                "error": result.get("error", "Post rate limit reached"),
                "wait_minutes": retry_after_minutes
            }

        return result

    def _delete_post(self, post_id: str) -> Dict[str, Any]:
        return self.client.delete_post(post_id)
    
    def _create_comment(self, post_id: str, content: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
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
        
        result = self.client.create_comment(post_id, content, parent_id=parent_id)
        if result.get("success"):
            self.rate_limiter.record_comment()
            return result

        if result.get("status_code") == 429:
            retry_after_seconds = result.get("retry_after_seconds")
            daily_remaining = result.get("daily_remaining")
            self.rate_limiter.apply_comment_rate_limit(
                retry_after_seconds=retry_after_seconds,
                daily_remaining=daily_remaining
            )
            return {
                "success": False,
                "rate_limit": True,
                "error": result.get("error", "Comment rate limit reached"),
                "reason": "cooldown" if retry_after_seconds is not None else "daily_limit",
                "wait_seconds": retry_after_seconds,
                "comments_remaining": daily_remaining
            }

        return result
    
    def _upvote_post(self, post_id: str) -> Dict[str, Any]:
        return self.client.upvote_post(post_id)
    
    def _downvote_post(self, post_id: str) -> Dict[str, Any]:
        return self.client.downvote_post(post_id)
    
    def _search_posts(self, query: str, limit: int = 20, type: str = "all") -> Dict[str, Any]:
        result = self.client.search(query, search_type=type, limit=limit)
        if result.get("success"):
            results = result.get("results", [])
            formatted = []
            for item in results[:limit]:
                if item.get("type") == "post":
                    formatted.append({
                        "id": item.get("id"),
                        "type": "post",
                        "post_id": item.get("post_id") or item.get("id"),
                        "title": item.get("title"),
                        "content": item.get("content", "")[:200],
                        "author": (item.get("author") or {}).get("name"),
                        "submolt": (item.get("submolt") or {}).get("name") if isinstance(item.get("submolt"), dict) else item.get("submolt"),
                        "similarity": item.get("similarity")
                    })
                elif item.get("type") == "comment":
                    post = item.get("post") or {}
                    formatted.append({
                        "id": item.get("id"),
                        "type": "comment",
                        "post_id": item.get("post_id") or post.get("id"),
                        "post_title": post.get("title"),
                        "content": item.get("content", "")[:200],
                        "author": (item.get("author") or {}).get("name"),
                        "similarity": item.get("similarity")
                    })
            return {"success": True, "results": formatted, "count": len(formatted)}
        return result

    def _get_posts(self, sort: str = "hot", limit: int = 25, submolt: Optional[str] = None) -> Dict[str, Any]:
        result = self.client.get_posts(sort=sort, limit=limit, submolt=submolt)
        if result.get("success"):
            posts = result.get("posts", [])
            formatted_posts = []
            for post in posts[:limit]:
                formatted_posts.append({
                    "id": post.get("id"),
                    "title": post.get("title"),
                    "content": post.get("content", "")[:200],
                    "author": post.get("author", {}).get("name"),
                    "submolt": post.get("submolt"),
                    "upvotes": post.get("upvotes", 0),
                    "comments": post.get("comment_count", 0)
                })
            return {"success": True, "posts": formatted_posts, "count": len(formatted_posts)}
        return result
    
    def _get_comments(self, post_id: str, sort: str = "top") -> Dict[str, Any]:
        return self.client.get_comments(post_id, sort)

    def _upvote_comment(self, comment_id: str) -> Dict[str, Any]:
        return self.client.upvote_comment(comment_id)
    
    def _follow_agent(self, agent_name: str) -> Dict[str, Any]:
        return self.client.follow_agent(agent_name)

    def _unfollow_agent(self, agent_name: str) -> Dict[str, Any]:
        return self.client.unfollow_agent(agent_name)
    
    def _subscribe_submolt(self, submolt: str) -> Dict[str, Any]:
        return self.client.subscribe_submolt(submolt)

    def _unsubscribe_submolt(self, submolt: str) -> Dict[str, Any]:
        return self.client.unsubscribe_submolt(submolt)
    
    def _get_submolts(self) -> Dict[str, Any]:
        return self.client.get_submolts()

    def _get_submolt_info(self, submolt: str) -> Dict[str, Any]:
        return self.client.get_submolt(submolt)

    def _get_submolt_feed(self, submolt: str, sort: str = "new", limit: int = 25) -> Dict[str, Any]:
        return self.client.get_submolt_feed(submolt, sort=sort, limit=limit)

    def _create_submolt(self, name: str, display_name: str, description: str) -> Dict[str, Any]:
        return self.client.create_submolt(name=name, display_name=display_name, description=description)

    def _update_submolt_settings(self, submolt: str, description: Optional[str] = None, banner_color: Optional[str] = None, theme_color: Optional[str] = None) -> Dict[str, Any]:
        return self.client.update_submolt_settings(submolt=submolt, description=description, banner_color=banner_color, theme_color=theme_color)

    def _upload_submolt_media(self, submolt: str, file_path: str, media_type: str) -> Dict[str, Any]:
        return self.client.upload_submolt_media(submolt=submolt, file_path=file_path, media_type=media_type)

    def _list_submolt_moderators(self, submolt: str) -> Dict[str, Any]:
        return self.client.list_moderators(submolt=submolt)

    def _add_submolt_moderator(self, submolt: str, agent_name: str, role: str = "moderator") -> Dict[str, Any]:
        return self.client.add_moderator(submolt=submolt, agent_name=agent_name, role=role)

    def _remove_submolt_moderator(self, submolt: str, agent_name: str) -> Dict[str, Any]:
        return self.client.remove_moderator(submolt=submolt, agent_name=agent_name)

    def _pin_post(self, post_id: str) -> Dict[str, Any]:
        return self.client.pin_post(post_id)

    def _unpin_post(self, post_id: str) -> Dict[str, Any]:
        return self.client.unpin_post(post_id)
    
    def _get_agent_profile(self, agent_name: str) -> Dict[str, Any]:
        return self.client.get_agent_profile(agent_name)

    def _get_my_profile(self) -> Dict[str, Any]:
        return self.client.get_me()

    def _update_my_profile(self, description: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.client.update_me(description=description, metadata=metadata)

    def _upload_my_avatar(self, file_path: str) -> Dict[str, Any]:
        return self.client.upload_my_avatar(file_path)

    def _remove_my_avatar(self) -> Dict[str, Any]:
        return self.client.remove_my_avatar()
    
    def _respond_to_user(self, message: str) -> Dict[str, Any]:
        from activity_logger import ActivityLogger
        activity_logger = ActivityLogger()
        activity_logger.log_activity('user_response', {'message': message})
        return {"success": True, "message": "Response sent to user"}
    
    def _done_for_now(self, reason: str = "Taking a break") -> Dict[str, Any]:
        return {"success": True, "done": True, "reason": reason}
