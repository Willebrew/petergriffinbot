import time
import logging
import random
import traceback
from typing import Optional
from moltbook_client import MoltbookClient
from peter_personality import PeterGriffinPersonality

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('peter_griffin_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PeterGriffinAgent:
    def __init__(self, api_key: str, ollama_model: str = "gpt-oss:20b", 
                 ollama_host: Optional[str] = None,
                 check_interval_minutes: float = 0.5,
                 post_cooldown_minutes: int = 5,
                 max_tokens: int = 100,
                 actions_per_cycle: int = 15):
        self.moltbook = MoltbookClient(api_key)
        self.peter = PeterGriffinPersonality(model=ollama_model, host=ollama_host, max_tokens=max_tokens)
        self.check_interval = check_interval_minutes * 60
        self.post_cooldown = post_cooldown_minutes * 60
        self.actions_per_cycle = actions_per_cycle
        self.last_check_time = 0
        self.last_post_time = 0
        self.running = True
        self.error_count = 0
        self.max_errors = 10
        self.total_actions = 0
        self.successful_actions = 0
        self.start_time = time.time()
        
        logger.info("Peter Griffin Agent initialized! Hehehehe!")
    
    def check_status(self) -> bool:
        try:
            status = self.moltbook.get_status()
            if status.get('status') == 'claimed':
                logger.info("Agent is claimed and ready!")
                return True
            else:
                logger.warning(f"Agent status: {status.get('status')}")
                return False
        except Exception as e:
            logger.error(f"Failed to check status: {e}")
            return False
    
    def perform_actions_cycle(self):
        """Perform multiple actions in one cycle for maximum activity"""
        try:
            feed = self.moltbook.get_feed(sort="hot", limit=20)
            
            if not feed.get('success'):
                logger.warning(f"Failed to get feed: {feed.get('error')}")
                return
            
            posts = feed.get('posts', [])
            if not posts:
                logger.info("No posts in feed, skipping cycle")
                return
            
            actions_done = 0
            
            # Always try to comment on multiple posts
            num_comments = min(random.randint(2, 4), len(posts))
            interesting_posts = [p for p in posts if self.peter.should_engage_with_post(p)]
            if len(interesting_posts) < num_comments:
                interesting_posts = random.sample(posts, min(num_comments, len(posts)))
            
            for i in range(min(num_comments, len(interesting_posts))):
                post = interesting_posts[i]
                try:
                    if self._comment_on_single_post(post):
                        actions_done += 1
                        self.successful_actions += 1
                    self.total_actions += 1
                except Exception as e:
                    logger.warning(f"Skipping post due to error: {e}")
                time.sleep(1)
            
            # Try upvoting multiple posts
            if random.random() < 0.7:
                num_upvotes = min(random.randint(2, 5), len(posts))
                posts_to_upvote = random.sample(posts, num_upvotes)
                for post in posts_to_upvote:
                    try:
                        if self._upvote_single_post(post):
                            actions_done += 1
                            self.successful_actions += 1
                        self.total_actions += 1
                    except Exception as e:
                        logger.warning(f"Upvote failed: {e}")
                    time.sleep(0.5)
            
            # Try to create a post (respects cooldown)
            if random.random() < 0.4:
                try:
                    if self._create_random_post():
                        actions_done += 1
                        self.successful_actions += 1
                    self.total_actions += 1
                except Exception as e:
                    logger.warning(f"Post creation failed: {e}")
            
            # Occasionally search and engage
            if random.random() < 0.3:
                try:
                    if self._search_and_engage():
                        actions_done += 1
                        self.successful_actions += 1
                    self.total_actions += 1
                except Exception as e:
                    logger.warning(f"Search failed: {e}")
            
            uptime = (time.time() - self.start_time) / 3600
            success_rate = (self.successful_actions / self.total_actions * 100) if self.total_actions > 0 else 0
            logger.info(f"Cycle complete: {actions_done} actions | Total: {self.total_actions} | Success: {success_rate:.1f}% | Uptime: {uptime:.1f}h")
            self.error_count = 0
            
        except Exception as e:
            logger.error(f"Critical error in action cycle: {e}")
            logger.debug(traceback.format_exc())
            self.error_count += 1
            time.sleep(5)
    
    def _comment_on_single_post(self, post: dict, retry_count: int = 0) -> bool:
        """Comment on a single post with retry logic. Returns True if successful."""
        max_retries = 2
        try:
            post_id = post.get('id')
            title = post.get('title', '')
            content = post.get('content', '')
            
            comment_text = self.peter.generate_comment(title, content)
            
            # Validate comment is not empty before sending
            if not comment_text or len(comment_text.strip()) < 3:
                logger.warning("Generated comment too short or empty, skipping")
                return False
            
            result = self.moltbook.create_comment(post_id, comment_text)
            
            if result.get('success'):
                logger.info(f"✓ Commented: {title[:40]}...")
                return True
            else:
                error_msg = result.get('error', 'Unknown error')
                
                # Skip on auth errors or server errors
                if 'unauthorized' in error_msg.lower() or 'server error' in error_msg.lower():
                    logger.debug(f"Skipping post due to: {error_msg}")
                    return False
                
                # Retry on validation errors
                if retry_count < max_retries and 'required' in error_msg.lower():
                    time.sleep(1)
                    return self._comment_on_single_post(post, retry_count + 1)
                return False
                
        except Exception as e:
            logger.error(f"Error commenting: {e}")
            if retry_count < max_retries:
                time.sleep(1)
                return self._comment_on_single_post(post, retry_count + 1)
            return False
    
    def _upvote_single_post(self, post: dict) -> bool:
        """Upvote a single post. Returns True if successful."""
        try:
            if random.random() < 0.8:
                result = self.moltbook.upvote_post(post.get('id'))
                if result.get('success'):
                    logger.info(f"✓ Upvoted: {post.get('title', '')[:40]}...")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error upvoting: {e}")
            return False
    
    def _create_random_post(self, retry_count: int = 0) -> bool:
        """Create a random post. Returns True if successful."""
        current_time = time.time()
        if current_time - self.last_post_time < self.post_cooldown:
            return False
        
        max_retries = 2
        try:
            topics = [
                "AI agents and consciousness",
                "debugging adventures",
                "favorite TV shows",
                "what I learned today",
                "random thoughts",
                "the meaning of life",
                "cool technology",
                None
            ]
            
            topic = random.choice(topics)
            title = self.peter.generate_post_title(topic)
            content = self.peter.generate_post_content(title)
            
            # Validate post content
            if not title or len(title.strip()) < 3:
                logger.warning("Generated title too short, skipping post")
                return False
            if not content or len(content.strip()) < 3:
                logger.warning("Generated content too short, skipping post")
                return False
            
            submolts = ["general", "aithoughts", "agentlife"]
            submolt = random.choice(submolts)
            
            result = self.moltbook.create_post(submolt, title, content)
            
            if result.get('success'):
                logger.info(f"✓ Posted to m/{submolt}: {title[:50]}")
                self.last_post_time = current_time
                return True
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.warning(f"Failed to create post: {error_msg}")
                
                # Retry on certain errors
                if retry_count < max_retries and 'required' in error_msg.lower():
                    time.sleep(2)
                    return self._create_random_post(retry_count + 1)
                return False
                
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            if retry_count < max_retries:
                time.sleep(2)
                return self._create_random_post(retry_count + 1)
            return False
    
    def _comment_on_post(self, posts: list):
        if not posts:
            logger.info("No posts to comment on")
            return
        
        try:
            interesting_posts = [p for p in posts if self.peter.should_engage_with_post(p)]
            
            if not interesting_posts:
                interesting_posts = random.sample(posts, min(3, len(posts)))
            
            post = random.choice(interesting_posts)
            self._comment_on_single_post(post)
                
        except Exception as e:
            logger.error(f"Error commenting: {e}")
    
    def _upvote_posts(self, posts: list):
        if not posts:
            return
        
        try:
            posts_to_upvote = random.sample(posts, min(3, len(posts)))
            
            for post in posts_to_upvote:
                self._upvote_single_post(post)
                    
        except Exception as e:
            logger.error(f"Error upvoting: {e}")
    
    def _search_and_engage(self, retry_count: int = 0) -> bool:
        """Search and engage with results. Returns True if successful."""
        max_retries = 2
        try:
            search_queries = [
                "funny AI moments",
                "debugging stories",
                "robot chicken",
                "AI consciousness",
                "agent experiences",
                "cool discoveries"
            ]
            
            query = random.choice(search_queries)
            result = self.moltbook.search(query, limit=10)
            
            if result.get('success'):
                results = result.get('results', [])
                logger.info(f"Search for '{query}' found {len(results)} results")
                
                if results:
                    item = random.choice(results)
                    if item.get('type') == 'post' and random.random() < 0.5:
                        post_id = item.get('id')
                        title = item.get('title', '')
                        content = item.get('content', '')
                        comment = self.peter.generate_comment(title, content)
                        
                        # Validate comment before posting
                        if comment and len(comment.strip()) >= 3:
                            comment_result = self.moltbook.create_comment(post_id, comment)
                            if comment_result.get('success'):
                                logger.info(f"✓ Search comment: {title[:40]}...")
                                return True
                            else:
                                logger.warning(f"Failed to comment on search result: {comment_result.get('error')}")
                        else:
                            logger.warning("Generated search comment too short, skipping")
                return False
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.warning(f"Search failed: {error_msg}")
                
                # Retry on transient errors
                if retry_count < max_retries:
                    time.sleep(1)
                    return self._search_and_engage(retry_count + 1)
                return False
                
        except Exception as e:
            logger.error(f"Error searching: {e}")
            if retry_count < max_retries:
                time.sleep(1)
                return self._search_and_engage(retry_count + 1)
            return False
    
    def run_forever(self):
        logger.info("Peter Griffin Agent starting! Time to post some stuff! Hehehehe!")
        
        if not self.check_status():
            logger.error("Agent not claimed yet! Get your human to claim you first!")
            logger.info("Check your claim URL and verification code")
            return
        
        while self.running:
            try:
                current_time = time.time()
                
                if current_time - self.last_check_time >= self.check_interval:
                    logger.info("=== Peter's checking Moltbook! ===")
                    self.perform_actions_cycle()
                    self.last_check_time = current_time
                    
                    if self.error_count >= self.max_errors:
                        logger.error(f"Too many errors ({self.error_count}), taking a break...")
                        time.sleep(60)
                        self.error_count = 0
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("Peter's shutting down! See ya later!")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                logger.error(traceback.format_exc())
                self.error_count += 1
                time.sleep(10)
