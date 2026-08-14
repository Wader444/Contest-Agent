"""Config loader supporting both local config.json and environment variables."""
import os
import json
from typing import Dict, Any

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from local JSON file or fallback to environment variables."""
    # 1. If local config file exists, load it
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Config] Warning: Could not read {config_path}: {e}")

    # 2. Fallback to Environment Variables (for Render / Docker / Cloud)
    return {
        "phone_number": os.getenv("PHONE_NUMBER", "+919030240952"),
        "schedule": {
            "sunday": {
                "hour": int(os.getenv("SCHEDULE_SUNDAY_HOUR", "10")),
                "minute": int(os.getenv("SCHEDULE_SUNDAY_MINUTE", "0"))
            },
            "wednesday": {
                "hour": int(os.getenv("SCHEDULE_WEDNESDAY_HOUR", "6")),
                "minute": int(os.getenv("SCHEDULE_WEDNESDAY_MINUTE", "0"))
            }
        },
        "daily_alert": {
            "enabled": os.getenv("DAILY_ALERT_ENABLED", "true").lower() == "true",
            "hour": int(os.getenv("DAILY_ALERT_HOUR", "8")),
            "minute": int(os.getenv("DAILY_ALERT_MINUTE", "0"))
        },
        "twilio": {
            "account_sid": os.getenv("TWILIO_ACCOUNT_SID", ""),
            "auth_token": os.getenv("TWILIO_AUTH_TOKEN", ""),
            "from_number": os.getenv("TWILIO_FROM_NUMBER", "")
        },
        "platforms": {
            "leetcode": os.getenv("PLATFORM_LEETCODE", "true").lower() == "true",
            "codeforces": os.getenv("PLATFORM_CODEFORCES", "true").lower() == "true",
            "codechef": os.getenv("PLATFORM_CODECHEF", "true").lower() == "true",
            "hackerrank": os.getenv("PLATFORM_HACKERRANK", "true").lower() == "true",
            "geeksforgeeks": os.getenv("PLATFORM_GEEKSFORGEEKS", "true").lower() == "true"
        },
        "look_ahead_days": int(os.getenv("LOOK_AHEAD_DAYS", "7")),
        "timezone": os.getenv("TZ", os.getenv("TIMEZONE", "Asia/Kolkata"))
    }
