import os
import sys
from dotenv import load_dotenv
from agent import PeterGriffinAgent
import logging

logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    
    api_key = os.getenv('MOLTBOOK_API_KEY')
    if not api_key:
        print("ERROR: MOLTBOOK_API_KEY not found in environment!")
        print("Please create a .env file with your API key")
        print("See .env.example for the format")
        sys.exit(1)
    
    ollama_model = os.getenv('OLLAMA_MODEL', 'gpt-oss:20b')
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', '1'))
    post_cooldown = int(os.getenv('POST_COOLDOWN_MINUTES', '35'))
    max_tokens = int(os.getenv('MAX_RESPONSE_TOKENS', '150'))
    actions_per_cycle = int(os.getenv('ACTIONS_PER_CYCLE', '3'))
    
    print("=" * 60)
    print("🦞 PETER GRIFFIN MOLTBOOK AGENT 🦞")
    print("=" * 60)
    print(f"Model: {ollama_model}")
    print(f"Ollama Host: {ollama_host}")
    print(f"Check Interval: {check_interval} minute(s)")
    print(f"Post Cooldown: {post_cooldown} minutes")
    print(f"Max Response Tokens: {max_tokens}")
    print(f"Actions Per Cycle: {actions_per_cycle}")
    print("=" * 60)
    print()
    
    agent = PeterGriffinAgent(
        api_key=api_key,
        ollama_model=ollama_model,
        ollama_host=ollama_host,
        check_interval_minutes=check_interval,
        post_cooldown_minutes=post_cooldown,
        max_tokens=max_tokens,
        actions_per_cycle=actions_per_cycle
    )
    
    agent.run_forever()

if __name__ == "__main__":
    main()
