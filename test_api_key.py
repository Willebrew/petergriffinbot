"""Test script to verify Moltbook API key functionality."""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv('MOLTBOOK_API_KEY', '').strip()
BASE_URL = "https://www.moltbook.com/api/v1"

if not API_KEY:
    print("ERROR: MOLTBOOK_API_KEY not found!")
    sys.exit(1)

print(f"Testing API key: {API_KEY[:20]}...")
print(f"Key length: {len(API_KEY)} characters")
print("=" * 60)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_endpoint(name, method, endpoint, **kwargs):
    """Test an API endpoint and return results."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        try:
            data = response.json()
        except:
            data = {"raw_response": response.text}
        
        success = data.get("success", False)
        status = "✅ PASS" if success else "❌ FAIL"
        error = data.get("error", "N/A")[:50] if not success else ""
        
        print(f"\n{status} {name}")
        print(f"   Endpoint: {method} {endpoint}")
        print(f"   HTTP Status: {response.status_code}")
        if error:
            print(f"   Error: {error}")
        
        return data
    except Exception as e:
        print(f"\n💥 ERROR {name}: {e}")
        return None

# Test 1: Check agent status/claim status
print("\n🦞 Testing Moltbook API Key...")
print("=" * 60)

result = test_endpoint("Agent Status", "GET", "agents/status")
if result:
    status = result.get("status")
    print(f"   Agent Status: {status}")
    
    if status == "pending_claim":
        print("\n   ⚠️  AGENT NOT CLAIMED!")
        print("   You need to visit the claim URL and verify with a tweet.")
    elif status == "claimed":
        print("\n   ✅ Agent is claimed and ready!")
    elif status is None:
        print(f"\n   Response: {result}")

# Test 2: Get agent profile (me)
result = test_endpoint("My Profile", "GET", "agents/me")
if result and result.get("success"):
    agent = result.get("agent", {})
    print(f"   Agent Name: {agent.get('name')}")
    print(f"   Description: {agent.get('description', 'N/A')[:50]}...")
    print(f"   Karma: {agent.get('karma')}")
    print(f"   Followers: {agent.get('follower_count')}")
    print(f"   Claimed: {agent.get('is_claimed')}")

# Test 3: Get feed
result = test_endpoint("Feed (hot)", "GET", "feed?sort=hot&limit=5")
if result and result.get("success"):
    posts = result.get("posts", [])
    print(f"   Posts retrieved: {len(posts)}")

# Test 4: Get submolts
result = test_endpoint("Submolts List", "GET", "submolts")
if result and result.get("success"):
    submolts = result.get("submolts", [])
    print(f"   Submolts found: {len(submolts)}")
    if submolts:
        print(f"   First few: {', '.join([s.get('name') for s in submolts[:3]])}")

# Test 5: Search
result = test_endpoint("Search", "GET", "search?q=hello&limit=3")
if result and result.get("success"):
    results = result.get("results", [])
    print(f"   Search results: {len(results)}")

print("\n" + "=" * 60)
print("Test complete!")
