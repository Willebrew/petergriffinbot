# 🚀 Quick Start Guide

## Setup (5 minutes)

### 1. Install Ollama
Download from: https://ollama.ai

### 2. Pull the Model
```bash
ollama pull gpt-oss:20b
```

### 3. Register Agent
```bash
python setup_agent.py
```

Follow prompts to create your agent. You'll get:
- API key (saved to `.env`)
- Claim URL
- Verification code

### 4. Claim Agent
1. Visit the claim URL
2. Post tweet with verification code
3. Done!

### 5. Start Agent
**Windows:**
```bash
start_agent.bat
```

**Mac/Linux:**
```bash
chmod +x start_agent.sh
./start_agent.sh
```

## What Happens Next?

The agent runs **forever** and:
- Checks Moltbook every 30 minutes
- Posts, comments, upvotes in Peter Griffin's voice
- Logs everything to `peter_griffin_agent.log`
- Handles errors gracefully

## Context Limits

The agent is optimized for the model's context window:

- **System prompt**: ~200 tokens (compressed)
- **Input context**: Max 400 chars (trimmed automatically)
- **User prompt**: Max 300 chars (trimmed automatically)
- **Response**: Max 150 tokens (configurable)
- **Total**: ~800 tokens per request (well under limit)

### Adjust Token Limits

Edit `.env`:
```env
MAX_RESPONSE_TOKENS=150  # Lower = shorter responses, less context used
```

Lower values (100-120) = more conservative, faster
Higher values (150-200) = more detailed, uses more context

## Monitoring

Watch logs:
```bash
# Real-time
tail -f peter_griffin_agent.log

# Windows
Get-Content peter_griffin_agent.log -Wait
```

## Stop Agent

Press `Ctrl+C` in the terminal

## Troubleshooting

**"Ollama connection failed"**
→ Run `ollama serve` in another terminal

**"Post cooldown active"**
→ Normal! Moltbook limits posts to 1 per 30 min

**"Context too long"**
→ Lower `MAX_RESPONSE_TOKENS` in `.env`

**Agent stops**
→ Check `peter_griffin_agent.log` for errors

## Tips

- Start with default settings (150 tokens)
- Monitor first few posts to ensure quality
- Adjust `MAX_RESPONSE_TOKENS` if responses are too long/short
- Check logs regularly for errors
- Agent auto-recovers from most errors

---

**That's it! Your Peter Griffin agent is now running 24/7!** 🦞
