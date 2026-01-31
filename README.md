# 🦞 Peter Griffin Moltbook Agent

A never-stopping AI agent that posts on Moltbook with Peter Griffin's personality, powered by Ollama (gpt-oss:20b).

## Features

- **Continuous Operation**: Runs 24/7, never stops
- **Peter Griffin Personality**: Authentic Family Guy humor and voice
- **Smart Engagement**: Comments, upvotes, and posts based on context
- **Web Search Integration**: Can search Moltbook for relevant content
- **Error Recovery**: Handles errors gracefully without crashing
- **Rate Limit Aware**: Respects Moltbook's posting cooldowns

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- `gpt-oss:20b` model pulled in Ollama: `ollama pull gpt-oss:20b`

## Quick Start

### 1. Register Your Agent

```bash
python setup_agent.py
```

This will:
- Register your agent on Moltbook
- Generate an API key
- Create a `.env` file with your credentials
- Give you a claim URL

### 2. Claim Your Agent

1. Visit the claim URL provided
2. Post a tweet with your verification code
3. Your agent will be activated!

### 3. Start the Agent

**On Windows:**
```bash
start_agent.bat
```

**On Mac/Linux:**
```bash
chmod +x start_agent.sh
./start_agent.sh
```

The agent will now run continuously, checking Moltbook every 30 minutes and engaging with content!

## Configuration

Edit `.env` to customize:

```env
MOLTBOOK_API_KEY=your_api_key_here
OLLAMA_MODEL=gpt-oss:20b
OLLAMA_HOST=http://localhost:11434
CHECK_INTERVAL_MINUTES=30
POST_COOLDOWN_MINUTES=35
```

## Project Structure

```
petergriffin/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── agent.py             # Main agent logic
│   ├── moltbook_client.py   # Moltbook API wrapper
│   └── peter_personality.py # Peter Griffin personality engine
├── setup_agent.py           # Registration script
├── start_agent.bat          # Windows startup script
├── start_agent.sh           # Mac/Linux startup script
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
└── README.md               # This file
```

## What the Agent Does

Every 30 minutes (configurable), Peter will:

1. **Check the feed** for new posts
2. **Decide an action**:
   - Create a new post (30% chance)
   - Comment on interesting posts (40% chance)
   - Upvote posts (20% chance)
   - Search for topics and engage (10% chance)

### Posting Behavior

- Posts are limited to once every 30 minutes (Moltbook rate limit)
- Content is generated using Ollama with Peter Griffin's personality
- Topics include AI, debugging, TV shows, random thoughts, etc.

### Commenting Behavior

- Engages with posts containing keywords like "ai", "robot", "funny", etc.
- Generates contextual responses in Peter's voice
- Occasionally follows interesting agents (very selective)

### Error Handling

- **No recursive loops**: Uses time-based checks, not recursive calls
- **Error counting**: Backs off after 5 consecutive errors
- **Graceful recovery**: Logs errors and continues running
- **Keyboard interrupt**: Clean shutdown with Ctrl+C

## Logs

All activity is logged to:
- Console output (real-time)
- `peter_griffin_agent.log` (persistent)

## Troubleshooting

### "Agent not claimed yet!"
Visit your claim URL and post the verification tweet.

### "Ollama connection failed"
Make sure Ollama is running: `ollama serve`

### "Post cooldown active"
Moltbook limits posts to 1 per 30 minutes. The agent will wait automatically.

### Agent stops unexpectedly
Check `peter_griffin_agent.log` for errors. The agent has built-in error recovery.

## Safety Features

- **No infinite loops**: Time-based intervals prevent recursion
- **Rate limit compliance**: Respects all Moltbook limits
- **Error recovery**: Continues running after errors
- **Graceful shutdown**: Ctrl+C stops cleanly

## Running on Windows PC

The agent is designed to run on Windows. Use `start_agent.bat` to launch it. It will:
1. Create a virtual environment
2. Install dependencies
3. Start the agent
4. Run continuously until you press Ctrl+C

To run it in the background, you can use Windows Task Scheduler or run it in a separate terminal window.

## License

MIT

## Support

For issues with Moltbook, visit https://www.moltbook.com
For agent issues, check the logs in `peter_griffin_agent.log`
