"""
Autonomous Peter Griffin Agent using Ollama tool calling.
Peter makes ALL decisions about what to do on Moltbook.
"""

import time
import logging
import json
from typing import Dict, Any
from moltbook_client import MoltbookClient
from peter_personality import PeterGriffinPersonality
from tools import MOLTBOOK_TOOLS, ToolExecutor
from activity_logger import ActivityLogger
from suggestions_manager import SuggestionsManager
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
=======
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
from rate_limit_tracker import RateLimitTracker
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
from rate_limit_tracker import RateLimitTracker
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
try:
    import dashboard
except ImportError:
    dashboard = None
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py

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
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
=======
        self.rate_limiter = RateLimitTracker()
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
        self.rate_limiter = RateLimitTracker()
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
        
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
        
        limits_info = f"\n📊 YOUR RATE LIMITS TODAY:\n"
        limits_info += f"Comments: {comments['used']}/{comments['limit']} used"
        
        if comments['remaining'] == 0:
            limits_info += f" (❌ DAILY LIMIT REACHED - No more comments until tomorrow)"
        elif comments['remaining'] < 10:
            limits_info += f" (⚠️ Only {comments['remaining']} left today!)"
        else:
            limits_info += f" ({comments['remaining']} remaining)"
        
        if not comments['can_comment']:
            limits_info += f"\nNext comment available: {comments['next_available']}"
        
        if not posts['can_post']:
            limits_info += f"\nNext post available: {posts['next_available']}"
        
        limits_info += "\n\nIMPORTANT: If you're out of comments, focus on posts, upvotes, reading, or use respond_to_user to chat with your human!\n"
        context_parts.append(limits_info)
        
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
        
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
        context = f"""You're on Moltbook, the AI social network. Time to decide what to do!

**Your Stats:**
- Actions taken: {self.total_actions}
- Success rate: {success_rate:.1f}%
- Uptime: {uptime_hours:.1f} hours

**What do you want to do?**
Start by calling get_feed to see what's happening, then decide your next moves.
You can do multiple things in a row - comment, upvote, create posts, search, whatever!
When you're done or bored, call done_for_now.

Remember: You're Peter Griffin. Be chaotic, impulsive, and do whatever YOU want! Hehehehe!
"""
        
        pending_suggestions = self.suggestions_manager.get_pending()
        if pending_suggestions:
            suggestions_text = "\n".join([f"- {s['text']}" for s in pending_suggestions])
            context += f"\n\n**Hey Peter! Your buddy sent you some ideas:**\n{suggestions_text}\n\nFeel free to use 'em or ignore 'em, whatever! Hehehehe!"
            self.suggestions_manager.mark_all_pending_as_seen()
        
        return context
=======
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
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
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
    
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
                    
                    # Get Peter's decision
                    self.activity_logger.log_activity('thinking', {'iteration': iteration})
                    response = self.peter.decide_next_actions(context, MOLTBOOK_TOOLS)
                    
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
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
        if tool_name == 'create_post':
=======
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
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
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
<<<<<<< D:/Projects/petergriffinbot/src/autonomous_agent.py
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
=======
>>>>>>> C:/Users/Will/.windsurf/worktrees/petergriffinbot/petergriffinbot-ff7820b2/src/autonomous_agent.py
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
