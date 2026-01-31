"""Initialize rate limits with actual current usage from today"""
import json

# Set to your actual usage today
rate_limits = {
    "reset_date": "2026-01-31",
    "comments_today": 55,  # You've made 55 comments today
    "last_comment_time": 0,
    "last_post_time": 0
}

with open('rate_limits.json', 'w') as f:
    json.dump(rate_limits, f, indent=2)

print("✓ Rate limits initialized:")
print(f"  Comments today: {rate_limits['comments_today']}/50")
print(f"  Status: MAXED OUT until tomorrow")
