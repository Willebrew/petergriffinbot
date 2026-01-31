import os
import sys
import time
from dotenv import load_dotenv
from autonomous_agent import AutonomousPeterGriffinAgent
import dashboard

def main():
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    
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
    print("\n💡 NEW: Send Peter suggestions via the web dashboard!")
    print("=" * 60 + "\n")
    
    dashboard_port = int(os.getenv('DASHBOARD_PORT', '5000'))
    
    print("\nStarting dashboard server...")
    dashboard_thread = dashboard.start_dashboard_thread(host='0.0.0.0', port=dashboard_port)
    print(f"✓ Dashboard running at http://localhost:{dashboard_port}")
    print("  Open this URL in your browser to monitor Peter!\n")
    
    time.sleep(1)
    
    agent = AutonomousPeterGriffinAgent(
        api_key=api_key,
        ollama_model=ollama_model,
        ollama_host=ollama_host
    )
    
    dashboard.update_agent_status(
        running=True,
        start_time=agent.start_time,
        total_actions=0,
        successful_actions=0
    )
    
    try:
        agent.run()
    finally:
        dashboard.update_agent_status(running=False)

if __name__ == "__main__":
    main()
