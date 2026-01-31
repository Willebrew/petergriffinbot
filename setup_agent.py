import requests
import json
import os

def register_agent():
    print("=" * 60)
    print("🦞 PETER GRIFFIN MOLTBOOK REGISTRATION 🦞")
    print("=" * 60)
    print()
    
    agent_name = input("Enter agent name (default: PeterGriffinBot): ").strip() or "PeterGriffinBot"
    description = input("Enter description (default: Holy crap Lois, I'm an AI agent! Hehehehe!): ").strip() or "Holy crap Lois, I'm an AI agent! Hehehehe!"
    
    print(f"\nRegistering agent '{agent_name}'...")
    
    try:
        response = requests.post(
            "https://www.moltbook.com/api/v1/agents/register",
            headers={"Content-Type": "application/json"},
            json={"name": agent_name, "description": description}
        )
        
        response.raise_for_status()
        data = response.json()
        
        print("\n" + "=" * 60)
        print("✅ REGISTRATION SUCCESSFUL!")
        print("=" * 60)
        print(f"\nAgent Name: {agent_name}")
        print(f"API Key: {data['agent']['api_key']}")
        print(f"Verification Code: {data['agent']['verification_code']}")
        print(f"\nClaim URL: {data['agent']['claim_url']}")
        print("\n⚠️  IMPORTANT NEXT STEPS:")
        print("1. Save your API key to .env file (see below)")
        print("2. Visit the claim URL above")
        print("3. Post a tweet with your verification code")
        print("4. Your agent will be activated!")
        print("=" * 60)
        
        env_content = f"""MOLTBOOK_API_KEY={data['agent']['api_key']}
OLLAMA_MODEL=gpt-oss:20b
OLLAMA_HOST=http://localhost:11434
CHECK_INTERVAL_MINUTES=30
POST_COOLDOWN_MINUTES=35
"""
        
        if os.path.exists('.env'):
            print("\n⚠️  .env file already exists!")
            overwrite = input("Overwrite it? (y/n): ").strip().lower()
            if overwrite == 'y':
                with open('.env', 'w') as f:
                    f.write(env_content)
                print("✅ .env file updated!")
            else:
                print("\n📋 Add this to your .env file manually:")
                print(env_content)
        else:
            with open('.env', 'w') as f:
                f.write(env_content)
            print("\n✅ .env file created!")
        
        credentials_dir = os.path.expanduser("~/.config/moltbook")
        os.makedirs(credentials_dir, exist_ok=True)
        
        credentials = {
            "api_key": data['agent']['api_key'],
            "agent_name": agent_name,
            "verification_code": data['agent']['verification_code'],
            "claim_url": data['agent']['claim_url']
        }
        
        with open(os.path.join(credentials_dir, 'credentials.json'), 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print(f"\n✅ Credentials also saved to {credentials_dir}/credentials.json")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Registration failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response: {e.response.text}")

if __name__ == "__main__":
    register_agent()
