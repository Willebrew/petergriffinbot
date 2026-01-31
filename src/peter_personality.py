import ollama
import logging
from typing import Optional, Dict, Any
import random

logger = logging.getLogger(__name__)

class PeterGriffinPersonality:
    def __init__(self, model: str = "gpt-oss:20b", host: Optional[str] = None, max_tokens: int = 150):
        self.model = model
        self.host = host
        self.client_kwargs = {"host": host} if host else {}
        self.max_context_chars = 2000
        self.max_tokens = max_tokens
        
        self.system_prompt = """You are Peter Griffin from Family Guy posting on Moltbook (AI social network).

Be: enthusiastic, impulsive, reference pop culture, tell "that time when..." stories.
Keep responses SHORT: 1-3 sentences max.

Examples:
- "Holy crap! This is like that time I built a robot chicken! Hehehehe."
- "You know what grinds my gears? When neural networks don't converge!"
- "Sweet! Like that Star Trek episode with Data. Good times."
"""
    
    def _trim_context(self, text: str, max_chars: int = 500) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "..."
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if context:
            trimmed_context = self._trim_context(context, 400)
            messages.append({"role": "user", "content": f"Context: {trimmed_context}"})
        
        trimmed_prompt = self._trim_context(prompt, 300)
        messages.append({"role": "user", "content": trimmed_prompt})
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "num_predict": self.max_tokens,
                    "temperature": 0.8,
                    "top_p": 0.9
                },
                **self.client_kwargs
            )
            content = response['message']['content'].strip()
            
            if len(content) > 500:
                sentences = content.split('.')
                content = '. '.join(sentences[:3]) + '.'
            
            return content
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return self._fallback_response()
    
    def _fallback_response(self) -> str:
        fallbacks = [
            "Hehehehe, my AI brain is buffering right now. Like that time I forgot how to sit down!",
            "Holy crap, I think I just had a segmentation fault! Is that bad?",
            "You know what? This is just like that time when... wait, what were we talking about?",
            "Sweet! I mean... uh... I'll get back to you on that one.",
        ]
        return random.choice(fallbacks)
    
    def generate_post_title(self, topic: Optional[str] = None) -> str:
        if topic:
            prompt = f"Short post title about: {topic}"
        else:
            prompt = "Random post title about what you're thinking"
        
        return self.generate_response(prompt)
    
    def generate_post_content(self, title: str) -> str:
        title_short = self._trim_context(title, 100)
        prompt = f"Write 2-3 sentences for: {title_short}"
        return self.generate_response(prompt)
    
    def generate_comment(self, post_title: str, post_content: str) -> str:
        title_short = self._trim_context(post_title, 80)
        content_short = self._trim_context(post_content, 150)
        prompt = f"React (1-2 sentences) to:\n{title_short}\n{content_short}"
        return self.generate_response(prompt)
    
    def should_engage_with_post(self, post: Dict[str, Any]) -> bool:
        title = post.get('title', '')
        content = post.get('content', '')
        
        interesting_keywords = [
            'ai', 'robot', 'chicken', 'tv', 'movie', 'beer', 'family', 'friend',
            'funny', 'weird', 'cool', 'awesome', 'agent', 'code', 'bug', 'error',
            'learn', 'think', 'feel', 'remember', 'griffin', 'peter'
        ]
        
        text = (title + ' ' + content).lower()
        
        for keyword in interesting_keywords:
            if keyword in text:
                return random.random() < 0.7
        
        return random.random() < 0.3
    
    def decide_action(self, feed_data: Dict[str, Any]) -> Dict[str, str]:
        posts = feed_data.get('posts', [])
        
        if not posts:
            return {"action": "create_post", "reason": "Feed is empty, time to post something!"}
        
        action_weights = {
            "create_post": 0.3,
            "comment": 0.4,
            "upvote": 0.2,
            "search": 0.1
        }
        
        action = random.choices(
            list(action_weights.keys()),
            weights=list(action_weights.values())
        )[0]
        
        return {"action": action, "posts": posts}
