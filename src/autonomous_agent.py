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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('peter_autonomous.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AutonomousPeterGriffinAgent:
    """Peter Griffin with full autonomy via Ollama tool calling"""
    
    def __init__(self, api_key: str, ollama_model: str = "gpt-oss:20b", ollama_host: str = None):
        self.moltbook = MoltbookClient(api_key)
        self.peter = PeterGriffinPersonality(model=ollama_model, host=ollama_host)
        self.tool_executor = ToolExecutor(self.moltbook)
        
        self.running = True
        self.total_actions = 0
        self.successful_actions = 0
        self.start_time = time.time()
        self.max_iterations_per_cycle = 10  # Prevent infinite loops
        
        logger.info("=" * 60)
        logger.info("🦞 AUTONOMOUS PETER GRIFFIN AGENT 🦞")
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
        """Build context for Peter's decision making"""
        uptime_hours = (time.time() - self.start_time) / 3600
        success_rate = (self.successful_actions / self.total_actions * 100) if self.total_actions > 0 else 0
        
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
        return context
    
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
                    response = self.peter.decide_next_actions(context, MOLTBOOK_TOOLS)
                    
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
                        self.total_actions += 1
                        
                        if result.get('success', False):
                            self.successful_actions += 1
                            logger.info(f"[SUCCESS] {tool_name} completed")
                        else:
                            logger.warning(f"[FAILED] {tool_name}: {result.get('error', 'Unknown error')}")
                        
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
                
            except KeyboardInterrupt:
                logger.info("\n[SHUTDOWN] Peter is shutting down! See ya later!")
                self.running = False
                break
                
            except Exception as e:
                logger.error(f"[ERROR] Unexpected error in autonomous loop: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Continue running despite errors
                time.sleep(2)
    
    def run(self):
        """Start the autonomous agent"""
        self.autonomous_loop()
