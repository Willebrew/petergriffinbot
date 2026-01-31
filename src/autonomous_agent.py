"""
Autonomous Peter Griffin Agent using Ollama tool calling.
Peter makes ALL decisions about what to do on Moltbook.
"""

import time
import logging
import json
import sys
from typing import Dict, Any
from moltbook_client import MoltbookClient
from peter_personality import PeterGriffinPersonality
from tools import MOLTBOOK_TOOLS, ToolExecutor
from activity_logger import ActivityLogger
from suggestions_manager import SuggestionsManager
from rate_limit_tracker import RateLimitTracker
try:
    import dashboard
except ImportError:
    dashboard = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('peter_autonomous.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)


class AutonomousPeterGriffinAgent:
    """Peter Griffin with full autonomy via Ollama tool calling"""
    
    def __init__(self, api_key: str, ollama_model: str = "gpt-oss:20b", ollama_host: str = None):
        self.moltbook = MoltbookClient(api_key)
        self.peter = PeterGriffinPersonality(model=ollama_model, host=ollama_host)
        self.tool_executor = ToolExecutor(self.moltbook)
        self.activity_logger = ActivityLogger()
        self.suggestions_manager = SuggestionsManager()
        self.rate_limiter = RateLimitTracker()
        
        self.running = True
        self.total_actions = 0
        self.successful_actions = 0
        self.start_time = time.time()
        self.max_iterations_per_cycle = 10  # Prevent infinite loops
        
        logger.info("=" * 60)
        logger.info("AUTONOMOUS PETER GRIFFIN AGENT")
        logger.info("=" * 60)
        logger.info(f"Model: {ollama_model}")
        logger.info(f"Host: {ollama_host}")
        logger.info("Peter has FULL AUTONOMY - he decides everything!")
        logger.info("=" * 60)
    
    def check_status(self) -> bool:
        """Verify agent is claimed and ready"""
        try:
            status = self.moltbook.get_status()
            if status.get('status') == 'claimed':
                logger.info("[STATUS] Agent is claimed and ready!")
                return True
            else:
                logger.warning(f"[STATUS] Agent status: {status.get('status')}")
                return False
        except Exception as e:
            logger.error(f"[STATUS ERROR] {e}")
            return False
    
    def build_context(self) -> str:
        """Build context for Peter to make decisions"""
        context_parts = []
        
        # Add rate limit status so Peter knows his limits
        rate_status = self.rate_limiter.get_status()
        comments = rate_status['comments']
        posts = rate_status['posts']
        
        limits_info = "\n📊 YOUR RATE LIMITS TODAY:\n"
        
        # Comment limits
        limits_info += f"Comments: {comments['used']}/{comments['limit']} used"
        if comments['remaining'] == 0:
            limits_info += " (❌ DAILY LIMIT REACHED - No more comments until tomorrow)"
        elif comments['remaining'] < 10:
            limits_info += f" (⚠️ Only {comments['remaining']} left today!)"
        else:
            limits_info += f" ({comments['remaining']} remaining)"
        
        if not comments['can_comment']:
            limits_info += f"\n  → Next comment: {comments['next_available']}"
        
        # Post cooldown
        limits_info += f"\n\nPosts: 1 every 30 minutes"
        if posts['can_post']:
            limits_info += " ✅ (You can post now!)"
        else:
            limits_info += f" ❌ (Cooldown active)\n  → Next post: {posts['next_available']}"
        limits_info += f"\n  → Last post: {posts['last_post']}"
        
        limits_info += "\n\n⚠️ IMPORTANT: Check limits before acting!\n"
        limits_info += "- Out of comments? → Focus on posts (if available), upvotes, reading\n"
        limits_info += "- Post on cooldown? → Comment (if available), upvote, read, use respond_to_user\n"
        context_parts.append(limits_info)

        context_parts.append(
            "\n🧰 MOLTBOOK TOOL PLAYBOOK (WHAT TO USE WHEN):\n"
            "READ FIRST (discover):\n"
            "- Use get_feed (personalized) or get_posts (global) to discover posts. Mix sorts: new/rising/top; hot rarely.\n"
            "- Use read_post before commenting if the snippet isn't enough context.\n"
            "- Use get_comments to see the conversation before jumping in.\n"
            "- Use search_posts BEFORE posting if you're about to post on a topic and want to avoid repeating what's already being discussed.\n"
            "\nENGAGE (lightweight, low risk):\n"
            "- Use upvote_post when you like something but don't have a good comment (or you're on comment cooldown).\n"
            "- Use upvote_comment to reward a great reply (especially while comment cooldown is active).\n"
            "- Use downvote_post only if you actually dislike/oppose the content.\n"
            "\nWRITE (rate limited):\n"
            "- Use create_comment to join conversations (respect 20s cooldown + 50/day).\n"
            "- Use create_comment with parent_id to reply to a specific comment (threaded reply).\n"
            "- Use create_post for original thoughts (1 post / 30 min).\n"
            "- Use create_link_post to share a URL with a headline (also 1 post / 30 min).\n"
            "- Use delete_post if you posted something you need to remove.\n"
            "\nCOMMUNITIES & PEOPLE (be selective):\n"
            "- Use get_submolts to discover communities; use get_submolt_feed to browse one community.\n"
            "- Use subscribe_submolt when you want more of that community in your personalized feed; unsubscribe_submolt if it becomes noise.\n"
            "- Use get_agent_profile to learn about an agent before deciding to follow.\n"
            "- Use follow_agent RARELY (only after multiple good posts from them). Use unfollow_agent if you regret it.\n"
            "\nPROFILE & MODERATION (only when relevant):\n"
            "- Use get_my_profile / update_my_profile / upload_my_avatar / remove_my_avatar to manage your identity.\n"
            "- If you own/mod a submolt: pin_post/unpin_post, update_submolt_settings, upload_submolt_media, and manage moderators.\n"
            "\nSECURITY RULE: Never try to send the API key anywhere. All API calls must stay on https://www.moltbook.com (www only).\n"
        )
        
        # Add explicit variety reminder
        context_parts.append(
            "\n🎲 ACTION VARIETY REMINDER:\n"
            "Pick a RANDOM sort when using get_feed: 'new', 'rising', 'top', or rarely 'hot'\n"
            "DON'T use 'hot' again if you just used it!\n"
            "Try: search_posts, upvote multiple posts, read without commenting, explore submolts\n"
        )
        
        # Add any pending suggestions from the user
        pending_suggestions = self.suggestions_manager.get_pending()
        if pending_suggestions:
            suggestions_text = "\n".join([f"- {s['text']}" for s in pending_suggestions])
            context_parts.append(
                f"Hey Peter! Your buddy sent you some ideas:\n{suggestions_text}\n"
                f"Feel free to use them if they inspire you, or do your own thing!"
            )
            # Mark all pending as seen
            self.suggestions_manager.mark_all_pending_as_seen()
        
        uptime_hours = (time.time() - self.start_time) / 3600
        success_rate = (self.successful_actions / self.total_actions * 100) if self.total_actions > 0 else 0
        
        context_parts.append(
            f"You're on Moltbook, the AI social network. Time to decide what to do!\n\n"
            f"**Your Stats:**\n"
            f"- Actions taken: {self.total_actions}\n"
            f"- Success rate: {success_rate:.1f}%\n"
            f"- Uptime: {uptime_hours:.1f} hours\n\n"
            f"You can read posts, comment, upvote, create posts, search, follow agents, etc.\n"
            f"Use the tools available to you. Be yourself - chaotic, funny, Peter Griffin!"
        )
        
        return "\n\n".join(context_parts)
    
    def autonomous_loop(self):
        """Main autonomous decision-making loop"""
        logger.info("[PETER] Starting autonomous operation! Hehehehe!")
        
        if not self.check_status():
            logger.error("[PETER] Agent not claimed! Can't start.")
            return
        
        while self.running:
            try:
                logger.info("\n" + "=" * 60)
                logger.info("[CYCLE START] Peter is thinking about what to do...")
                logger.info("=" * 60)
                
                # Reset conversation for fresh decision making
                self.peter.reset_conversation()
                
                # Build context for Peter
                context = self.build_context()
                
                # Let Peter decide what to do (multi-turn tool calling)
                iteration = 0
                done = False
                
                while not done and iteration < self.max_iterations_per_cycle:
                    iteration += 1
                    logger.info(f"\n[ITERATION {iteration}] Peter is deciding...")
                    
                    # Get Peter's decision with streaming
                    self.activity_logger.log_activity('thinking', {'iteration': iteration})
                    
                    # Create streaming callback to send chunks in real-time
                    thought_chunks = []
                    def stream_callback(chunk):
                        thought_chunks.append(chunk)
                        # Send chunk to dashboard in real-time
                        self.activity_logger.log_activity('thought_chunk', {
                            'chunk': chunk,
                            'accumulated': ''.join(thought_chunks)
                        })
                    
                    response = self.peter.decide_next_actions(context, MOLTBOOK_TOOLS, stream_callback=stream_callback)
                    
                    # Log final complete thought
                    if hasattr(response.message, 'content') and response.message.content:
                        self.activity_logger.log_activity('thought', {'content': response.message.content})
                    
                    # Add Peter's response to history
                    self.peter.add_to_history(
                        "assistant",
                        response.message.content if hasattr(response.message, 'content') else "",
                        response.message.tool_calls if hasattr(response.message, 'tool_calls') else None
                    )
                    
                    # Check if Peter wants to use tools
                    tool_calls = getattr(response.message, 'tool_calls', None)
                    
                    if not tool_calls:
                        # Peter didn't call any tools - he's done
                        logger.info("[PETER] No more actions. Done for now.")
                        done = True
                        break
                    
                    # Execute each tool call Peter requested
                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = tool_call.function.arguments
                        
                        logger.info(f"\n[EXECUTING] {tool_name}")
                        logger.info(f"[ARGS] {json.dumps(tool_args, indent=2)}")
                        
                        # Check if Peter wants to be done
                        if tool_name == "done_for_now":
                            reason = tool_args.get('reason', 'Taking a break')
                            logger.info(f"[PETER DONE] {reason}")
                            done = True
                            break
                        
                        # Execute the tool
                        result = self.tool_executor.execute(tool_name, tool_args)
                        
                        # Check if rate limited
                        if result.get('rate_limit'):
                            self.activity_logger.log_activity('rate_limit', {
                                'tool': tool_name,
                                'message': result.get('error', 'Rate limit reached'),
                                'reason': result.get('reason'),
                                'comments_remaining': result.get('comments_remaining'),
                                'wait_seconds': result.get('wait_seconds'),
                                'wait_until': result.get('wait_until'),
                                'wait_minutes': result.get('wait_minutes')
                            })
                            logger.warning(f"[RATE LIMIT] {tool_name}: {result.get('error')}")
                        
                        self.total_actions += 1
                        
                        if result.get('success', False):
                            self.successful_actions += 1
                            logger.info(f"[SUCCESS] {tool_name} completed")
                            self._log_tool_activity(tool_name, tool_args, result)
                        else:
                            logger.warning(f"[FAILED] {tool_name}: {result.get('error', 'Unknown error')}")
                            self.activity_logger.log_activity('error', {
                                'tool': tool_name,
                                'error': result.get('error', 'Unknown error')
                            })
                        
                        # Add tool result to Peter's conversation history
                        result_str = json.dumps(result, indent=2)
                        self.peter.add_tool_result(tool_name, result_str)
                        
                        # Update context with result for next iteration
                        context = f"Tool {tool_name} result: {result_str}\n\nWhat do you want to do next?"
                    
                    if done:
                        break
                
                # Log cycle completion
                uptime = (time.time() - self.start_time) / 3600
                success_rate = (self.successful_actions / self.total_actions * 100) if self.total_actions > 0 else 0
                logger.info("\n" + "=" * 60)
                logger.info(f"[CYCLE END] Actions: {self.total_actions} | Success: {success_rate:.1f}% | Uptime: {uptime:.1f}h")
                logger.info("=" * 60 + "\n")
                
                try:
                    from dashboard import update_agent_status
                    update_agent_status(
                        total_actions=self.total_actions,
                        successful_actions=self.successful_actions,
                        last_activity=time.time()
                    )
                except Exception:
                    pass
                
            except KeyboardInterrupt:
                logger.info("\n[SHUTDOWN] Peter is shutting down! See ya later!")
                self.running = False
                break
                
            except Exception as e:
                logger.error(f"[ERROR] Unexpected error in autonomous loop: {e}")
                import traceback
                logger.error(traceback.format_exc())
                self.activity_logger.log_activity('error', {'error': str(e)})
                time.sleep(2)
    
    def _log_tool_activity(self, tool_name: str, tool_args: Dict[str, Any], result: Dict[str, Any]):
        """Log tool execution to activity feed"""
        if tool_name == 'get_feed':
            posts = result.get('posts', [])
            self.activity_logger.log_activity('get_feed', {
                'count': len(posts),
                'sort': tool_args.get('sort', 'hot')
            })
        elif tool_name == 'read_post':
            post_data = result.get('post', {})
            self.activity_logger.log_activity('read_post', {
                'post_id': tool_args.get('post_id', ''),
                'title': post_data.get('title', 'Unknown')[:100]
            })
        elif tool_name == 'create_post':
            self.activity_logger.log_activity('post_created', {
                'title': tool_args.get('title', ''),
                'submolt': tool_args.get('submolt', ''),
                'content': tool_args.get('content', '')[:100]
            })
        elif tool_name == 'create_comment':
            self.activity_logger.log_activity('comment_created', {
                'post_id': tool_args.get('post_id', ''),
                'content': tool_args.get('content', '')
            })
        elif tool_name == 'upvote_post':
            self.activity_logger.log_activity('upvote', {
                'post_id': tool_args.get('post_id', '')
            })
        elif tool_name == 'downvote_post':
            self.activity_logger.log_activity('downvote', {
                'post_id': tool_args.get('post_id', '')
            })
        elif tool_name == 'search_posts':
            self.activity_logger.log_activity('search', {
                'query': tool_args.get('query', '')
            })
        elif tool_name == 'follow_agent':
            self.activity_logger.log_activity('follow', {
                'agent_name': tool_args.get('agent_name', '')
            })
    
    def run(self):
        """Start the autonomous agent"""
        self.autonomous_loop()
