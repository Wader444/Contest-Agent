# 🎯 Weekly Coding Contest Agent

> An intelligent Python agent that fetches upcoming coding contests from **LeetCode, CodeForces, CodeChef, HackerRank, and GeeksForGeeks** — and sends them straight to your phone via SMS.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platforms](https://img.shields.io/badge/Platforms-5-orange)

---

## ✨ Features

- 📱 **SMS Notifications** — Get contest alerts on your phone via Twilio
- 🌐 **5 Platforms** — LeetCode, CodeForces, CodeChef, HackerRank, GeeksForGeeks
- ⏰ **Smart Scheduling** — Auto-digests every **Sunday 10 AM** & **Wednesday 6 AM**
- 🎛️ **Web Dashboard** — Beautiful control panel to start/stop/run the agent
- 💻 **CLI Control** — Full command-line interface for power users
- 🔧 **Flexible Config** — Enable/disable platforms, customize schedule, phone number

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/coding-contest-agent.git
cd coding-contest-agent
pip install -r requirements.txt
```

### 2. Configure Twilio (Required for SMS)

1. Sign up at [twilio.com/try-twilio](https://www.twilio.com/try-twilio) (free trial)
2. Get your **Account SID** & **Auth Token** from the [console](https://console.twilio.com/)
3. Get a **Twilio Phone Number**
4. Edit `config.json`:

```json
{
  "phone_number": "+919030240952",
  "twilio": {
    "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "auth_token": "your_auth_token_here",
    "from_number": "+1234567890"
  }
}
```

> ⚠️ **Trial Account**: Free Twilio accounts can only SMS to **verified numbers**. Verify your number in the Twilio console first.

### 3. Run the Agent

**CLI Mode:**
```bash
python cli.py start      # Start scheduler
python cli.py stop       # Stop scheduler
python cli.py run        # Send test message now
python cli.py status     # Check status
python cli.py test-fetch # Test all fetchers
```

**Web Dashboard Mode:**
```bash
python main.py --mode web --port 5000
# Open http://localhost:5000 in your browser
```

---

## 📁 Project Structure

```
coding-contest-agent/
├── agent/
│   ├── __init__.py
│   ├── scheduler.py          # Core agent & APScheduler
│   ├── notifier.py           # Twilio SMS formatter & sender
│   └── fetchers/
│       ├── __init__.py
│       ├── leetcode.py       # GraphQL API
│       ├── codeforces.py     # Official API
│       ├── codechef.py       # Public API
│       ├── hackerrank.py     # REST API
│       └── geeksforgeeks.py  # Events API
├── web/
│   └── dashboard.py          # Flask control panel
├── tests/
│   └── test_fetchers.py      # Unit tests
├── cli.py                    # CLI interface
├── main.py                   # Entry point
├── config.json               # Your configuration
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Configuration

Edit `config.json` to customize:

```json
{
  "phone_number": "+919030240952",
  "schedule": {
    "sunday": {"hour": 10, "minute": 0},
    "wednesday": {"hour": 6, "minute": 0}
  },
  "twilio": {
    "account_sid": "...",
    "auth_token": "...",
    "from_number": "..."
  },
  "platforms": {
    "leetcode": true,
    "codeforces": true,
    "codechef": true,
    "hackerrank": true,
    "geeksforgeeks": true
  },
  "look_ahead_days": 7,
  "timezone": "Asia/Kolkata"
}
```

| Key | Description |
|-----|-------------|
| `phone_number` | Your phone number with country code |
| `schedule` | Days & times for weekly digests |
| `twilio` | Your Twilio credentials |
| `platforms` | Toggle individual platforms on/off |
| `look_ahead_days` | How many days ahead to show contests |
| `timezone` | Your local timezone |

---

## 🖥️ Web Dashboard

A sleek, dark-themed control panel to manage your agent:

| Feature | Description |
|---------|-------------|
| ▶️ Start | Start the background scheduler |
| ⏹️ Stop | Stop the scheduler |
| 🚀 Run Now | Trigger an instant digest |
| Live Status | See running state, last run, next run |

```bash
python main.py --mode web --port 8080
```

---

## 🧪 Testing

Run unit tests for all fetchers:

```bash
python -m unittest tests.test_fetchers -v
```

Or test without sending SMS:

```bash
python cli.py test-fetch
```

---

## 🐳 Deploying (24/7 Server)

Since the agent needs to run continuously, here are your options:

### Option A: Raspberry Pi / Old Laptop
Just keep the machine on and run:
```bash
nohup python cli.py start > agent.log 2>&1 &
```

### Option B: systemd Service (Linux)
Create `/etc/systemd/system/contest-agent.service`:
```ini
[Unit]
Description=Weekly Contest Agent
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/coding-contest-agent
ExecStart=/usr/bin/python3 /path/to/coding-contest-agent/cli.py start
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable contest-agent
sudo systemctl start contest-agent
```

### Option C: Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "cli.py", "start"]
```

### Option D: Render Cloud Deployment (Free Tier)
Deploy as a Web Service on [Render](https://render.com) in 2 minutes:

1. Push your repository to GitHub:
   ```bash
   git push origin master
   ```
2. In [Render Dashboard](https://dashboard.render.com), click **New +** -> **Blueprint** (or **Web Service**).
3. Connect your GitHub repository.
4. Render automatically detects [`render.yaml`](file:///c:/Users/ycher/Desktop/contest-agent/coding-contest-agent/render.yaml).
5. Set your secret Environment Variables:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_FROM_NUMBER`
   - `PHONE_NUMBER`
6. Click **Apply** or **Deploy Web Service**.
7. *(Optional)* To prevent Render's free tier from sleeping after 15 minutes of inactivity, set up a free 10-minute ping to `https://<your-service>.onrender.com/health` via [cron-job.org](https://cron-job.org) or [UptimeRobot](https://uptimerobot.com).


---

## 🛡️ Security Notes

- **Never commit `config.json`** — it contains your Twilio secrets
- Use `.env` files or environment variables in production
- The `.gitignore` already excludes `config.json` and `.env`

---

## 📝 Sample SMS

```
🎯 Weekly Coding Contests
=========================

📅 Mon, 21 Jul
  • LeetCode: Weekly Contest 123
    🕐 07:30 PM | ⏱️ 1h 30m
    🔗 https://leetcode.com/contest/weekly-contest-123

📅 Wed, 23 Jul
  • CodeForces: Round #1234 (Div. 2)
    🕐 08:05 PM | ⏱️ 2h
    🔗 https://codeforces.com/contests/1234

Happy Coding! 💪
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📜 License

[MIT](LICENSE) © 2026 Coding Contest Agent

---

<div align="center">
  <sub>Built with ❤️ for competitive programmers</sub>
</div>
