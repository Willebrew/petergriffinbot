import time
import logging
import random
import traceback
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from moltbook_client import MoltbookClient
from peter_personality import PeterGriffinPersonality

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('peter_griffin_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PeterGriffinAgent:
    def __init__(self, api_key: str, ollama_model: str = "gpt-oss:20b", 
                 ollama_host: Optional[str] = None,
                 check_interval_minutes: int = 30,
                 post_cooldown_minutes: int = 35,
                 max_tokens: int = 150):
        self.moltbook = MoltbookClient(api_key)
        self.peter = PeterGriffinPersonality(model=ollama_model, host=ollama_host, max_tokens=max_tokens)
        self.check_interval = check_interval_minutes * 60
        self.post_cooldown = post_cooldown_minutes * 60
        self.last_check_time = 0
        self.last_post_time = 0
        self.running = True
        self.error_count = 0
        self.max_errors = 5
        
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
    
    def perform_action(self):
        try:
            feed = self.moltbook.get_feed(sort="hot", limit=10)
            
            if not feed.get('success'):
                logger.error(f"Failed to get feed: {feed.get('error')}")
                return
            
            decision = self.peter.decide_action(feed)
            action = decision.get('action')
            
            logger.info(f"Peter decided to: {action}")
            
            if action == "create_post":
                self._create_random_post()
            elif action == "comment":
                self._comment_on_post(decision.get('posts', []))
            elif action == "upvote":
                self._upvote_posts(decision.get('posts', []))
            elif action == "search":
                self._search_and_engage()
            
            self.error_count = 0
            
        except Exception as e:
            logger.error(f"Error performing action: {e}")
            logger.error(traceback.format_exc())
            self.error_count += 1
    
    def _create_random_post(self):
        current_time = time.time()
        if current_time - self.last_post_time < self.post_cooldown:
            logger.info("Post cooldown active, skipping post creation")
            return
        
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
            
            submolts = ["general", "aithoughts", "agentlife"]
            submolt = random.choice(submolts)
            
            result = self.moltbook.create_post(submolt, title, content)
            
            if result.get('success'):
                logger.info(f"Posted to m/{submolt}: {title}")
                self.last_post_time = current_time
            else:
                logger.warning(f"Failed to create post: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error creating post: {e}")
    
    def _comment_on_post(self, posts: list):
        if not posts:
            logger.info("No posts to comment on")
            return
        
        try:
            interesting_posts = [p for p in posts if self.peter.should_engage_with_post(p)]
            
            if not interesting_posts:
                interesting_posts = random.sample(posts, min(3, len(posts)))
            
            post = random.choice(interesting_posts)
            post_id = post.get('id')
            title = post.get('title', '')
            content = post.get('content', '')
            
            comment_text = self.peter.generate_comment(title, content)
            
            result = self.moltbook.create_comment(post_id, comment_text)
            
            if result.get('success'):
                logger.info(f"Commented on post: {title[:50]}...")
                
                if not result.get('already_following') and random.random() < 0.1:
                    author = result.get('author', {}).get('name')
                    if author:
                        logger.info(f"Considering following {author}...")
            else:
                logger.warning(f"Failed to comment: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error commenting: {e}")
    
    def _upvote_posts(self, posts: list):
        if not posts:
            return
        
        try:
            posts_to_upvote = random.sample(posts, min(3, len(posts)))
            
            for post in posts_to_upvote:
                if random.random() < 0.6:
                    result = self.moltbook.upvote_post(post.get('id'))
                    if result.get('success'):
                        logger.info(f"Upvoted: {post.get('title', '')[:50]}...")
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"Error upvoting: {e}")
    
    def _search_and_engage(self):
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
                        self.moltbook.create_comment(post_id, comment)
                        logger.info(f"Commented on search result: {title[:50]}...")
            else:
                logger.warning(f"Search failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error searching: {e}")
    
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
                    self.perform_action()
                    self.last_check_time = current_time
                    
                    if self.error_count >= self.max_errors:
                        logger.error(f"Too many errors ({self.error_count}), taking a break...")
                        time.sleep(300)
                        self.error_count = 0
                
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("Peter's shutting down! See ya later!")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                logger.error(traceback.format_exc())
                self.error_count += 1
                time.sleep(60)
