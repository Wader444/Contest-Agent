"""Config loader supporting local config.json, .env, and environment variables."""
import os
import json
from typing import Dict, Any

def _load_env_file():
    """Lightweight .env file parser if python-dotenv is not installed"""
    for env_path in [".env", "../.env", os.path.join(os.path.dirname(__file__), "..", ".env")]:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from local JSON file and merge with environment variables."""
    _load_env_file()

    file_cfg = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                file_cfg = json.load(f)
        except Exception as e:
            print(f"[Config] Warning: Could not read {config_path}: {e}")

    # Build final config merging file_cfg and env vars (env vars take precedence)
    notification_channel = os.getenv(
        "NOTIFICATION_CHANNEL", 
        file_cfg.get("notification_channel", "telegram")
    )

    telegram_cfg = file_cfg.get("telegram", {})
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", telegram_cfg.get("bot_token", ""))
    chat_id = os.getenv("TELEGRAM_CHAT_ID", telegram_cfg.get("chat_id", ""))

    twilio_cfg = file_cfg.get("twilio", {})
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", twilio_cfg.get("account_sid", ""))
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", twilio_cfg.get("auth_token", ""))
    from_number = os.getenv("TWILIO_FROM_NUMBER", twilio_cfg.get("from_number", ""))

    phone_number = os.getenv("PHONE_NUMBER", file_cfg.get("phone_number", "+919030240952"))

    schedule_cfg = file_cfg.get("schedule", {
        "sunday": {
            "hour": int(os.getenv("SCHEDULE_SUNDAY_HOUR", "10")),
            "minute": int(os.getenv("SCHEDULE_SUNDAY_MINUTE", "0"))
        },
        "wednesday": {
            "hour": int(os.getenv("SCHEDULE_WEDNESDAY_HOUR", "6")),
            "minute": int(os.getenv("SCHEDULE_WEDNESDAY_MINUTE", "0"))
        }
    })

    daily_cfg = file_cfg.get("daily_alert", {
        "enabled": os.getenv("DAILY_ALERT_ENABLED", "true").lower() == "true",
        "hour": int(os.getenv("DAILY_ALERT_HOUR", "8")),
        "minute": int(os.getenv("DAILY_ALERT_MINUTE", "0"))
    })

    platforms_cfg = file_cfg.get("platforms", {
        "leetcode": os.getenv("PLATFORM_LEETCODE", "true").lower() == "true",
        "codeforces": os.getenv("PLATFORM_CODEFORCES", "true").lower() == "true",
        "codechef": os.getenv("PLATFORM_CODECHEF", "true").lower() == "true",
        "hackerrank": os.getenv("PLATFORM_HACKERRANK", "true").lower() == "true",
        "geeksforgeeks": os.getenv("PLATFORM_GEEKSFORGEEKS", "true").lower() == "true"
    })

    return {
        "notification_channel": notification_channel,
        "phone_number": phone_number,
        "telegram": {
            "bot_token": bot_token,
            "chat_id": chat_id
        },
        "twilio": {
            "account_sid": account_sid,
            "auth_token": auth_token,
            "from_number": from_number
        },
        "schedule": schedule_cfg,
        "daily_alert": daily_cfg,
        "platforms": platforms_cfg,
        "look_ahead_days": int(os.getenv("LOOK_AHEAD_DAYS", file_cfg.get("look_ahead_days", 7))),
        "timezone": os.getenv("TZ", os.getenv("TIMEZONE", file_cfg.get("timezone", "Asia/Kolkata")))
    }

