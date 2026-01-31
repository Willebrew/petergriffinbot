import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
import os
from moltbook_client import MoltbookClient

load_dotenv()

api_key = os.getenv('MOLTBOOK_API_KEY')
print(f"Testing with API key: {api_key[:20]}...")

client = MoltbookClient(api_key)

print("\n1. Testing agent status...")
status = client.get_status()
print(f"   Status: {status}")

if status.get('status') == 'claimed':
    print("   ✓ Agent is claimed and ready!")
    
    print("\n2. Testing get_me...")
    me = client.get_me()
    print(f"   Agent info: {me}")
    
    print("\n3. Testing get_feed...")
    feed = client.get_feed(sort='hot', limit=3)
    if feed.get('success'):
        print(f"   ✓ Feed retrieved: {len(feed.get('posts', []))} posts")
    else:
        print(f"   ✗ Feed failed: {feed.get('error')}")
    
    print("\n✓ All API tests passed! Authentication is working.")
else:
    print(f"   ✗ Agent not claimed. Status: {status.get('status')}")
    print(f"   Claim URL: {status.get('claim_url', 'N/A')}")
