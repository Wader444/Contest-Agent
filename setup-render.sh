#!/bin/bash
# Render Deployment Setup Script for Contest Agent
# Run this after pushing to GitHub

echo "🚀 Setting up Contest Agent for Render deployment..."

# 1. Create render.yaml for Infrastructure as Code
cat > render.yaml << 'YAML'
services:
  - type: web
    name: contest-agent-dashboard
    runtime: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main.py --mode web --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: TWILIO_ACCOUNT_SID
        sync: false
      - key: TWILIO_AUTH_TOKEN
        sync: false
      - key: TWILIO_FROM_NUMBER
        sync: false
      - key: PHONE_NUMBER
        value: +919030240952
      - key: TZ
        value: Asia/Kolkata

  - type: cron
    name: contest-agent-sunday
    runtime: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    schedule: "0 10 * * 0"
    startCommand: "python -c 'from agent.scheduler import ContestAgent; a=ContestAgent(); a.run_now()'"
    envVars:
      - key: TWILIO_ACCOUNT_SID
        sync: false
      - key: TWILIO_AUTH_TOKEN
        sync: false
      - key: TWILIO_FROM_NUMBER
        sync: false
      - key: PHONE_NUMBER
        value: +919030240952

  - type: cron
    name: contest-agent-wednesday
    runtime: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    schedule: "0 6 * * 3"
    startCommand: "python -c 'from agent.scheduler import ContestAgent; a=ContestAgent(); a.run_now()'"
    envVars:
      - key: TWILIO_ACCOUNT_SID
        sync: false
      - key: TWILIO_AUTH_TOKEN
        sync: false
      - key: TWILIO_FROM_NUMBER
        sync: false
      - key: PHONE_NUMBER
        value: +919030240952
YAML

echo "✅ render.yaml created!"

# 2. Create a cloud-compatible config loader
cat > agent/config_loader.py << 'PY'
"""Config loader that supports both local JSON and environment variables (for cloud deploy)"""
import os
import json
from typing import Dict, Any

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load config from JSON file or environment variables"""

    # Try JSON file first (local dev)
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)

    # Fallback to environment variables (cloud deploy)
    return {
        "phone_number": os.getenv("PHONE_NUMBER", "+919030240952"),
        "schedule": {
            "sunday": {"hour": 10, "minute": 0},
            "wednesday": {"hour": 6, "minute": 0}
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
        "timezone": os.getenv("TZ", "Asia/Kolkata")
    }
PY

echo "✅ agent/config_loader.py created!"

# 3. Update scheduler.py to use config_loader
sed -i 's/import json/import json
from .config_loader import load_config/' agent/scheduler.py
sed -i 's/with open(config_path, "r") as f:/config = load_config(config_path)/' agent/scheduler.py
sed -i '/config = json.load(f)/d' agent/scheduler.py
sed -i '/with open(config_path, "r") as f:/d' agent/scheduler.py

echo "✅ scheduler.py updated for cloud compatibility!"

echo ""
echo "📋 Next steps:"
echo "1. git add render.yaml agent/config_loader.py"
echo "2. git commit -m 'chore: add Render deployment config'"
echo "3. git push origin main"
echo "4. Go to https://dashboard.render.com and create new Web Service from your GitHub repo"
echo "5. Add your Twilio secrets as Environment Variables in Render dashboard"
