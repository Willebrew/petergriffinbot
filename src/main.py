import os
import sys
from dotenv import load_dotenv
from autonomous_agent import AutonomousPeterGriffinAgent

def main():
    # Force override OLLAMA_HOST if it's set to 0.0.0.0 (fix for Machine-level env var)
    if os.getenv('OLLAMA_HOST') == '0.0.0.0:11434':
        os.environ['OLLAMA_HOST'] = 'http://localhost:11434'
    
    load_dotenv(override=True)
    
    api_key = os.getenv('MOLTBOOK_API_KEY')
    if not api_key:
        print("ERROR: MOLTBOOK_API_KEY not found in environment!")
        print("Please create a .env file with your API key")
        print("See .env.example for the format")
        sys.exit(1)
    
    ollama_model = os.getenv('OLLAMA_MODEL', 'gpt-oss:20b')
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    
    print("\n" + "=" * 60)
    print("🦞 AUTONOMOUS PETER GRIFFIN AGENT 🦞")
    print("=" * 60)
    print(f"Model: {ollama_model}")
    print(f"Ollama Host: {ollama_host}")
    print("Mode: FULL AUTONOMY - Peter decides everything!")
    print("Tool Calling: ENABLED")
    print("Constraints: NONE - Pure chaos mode!")
    print("=" * 60)
    print("\nPeter will use Ollama tool calling to autonomously decide:")
    print("  - What posts to read")
    print("  - What to comment on")
    print("  - When to create posts")
    print("  - What to upvote/downvote")
    print("  - When to search for topics")
    print("  - Everything else!")
    print("\nNo randomization. No rate limits. Pure Peter Griffin chaos.")
    print("=" * 60 + "\n")
    
    agent = AutonomousPeterGriffinAgent(
        api_key=api_key,
        ollama_model=ollama_model,
        ollama_host=ollama_host
    )
    
    agent.run()

if __name__ == "__main__":
    main()
