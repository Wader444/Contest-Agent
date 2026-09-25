"""Contest Agent Scheduler & Core Logic"""
import threading
from datetime import datetime, timedelta
from typing import List, Dict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .fetchers import (
    LeetCodeFetcher, CodeForcesFetcher, CodeChefFetcher,
    HackerRankFetcher, GeeksForGeeksFetcher
)
from .notifier import get_notifier
from .config_loader import load_config

class ContestAgent:
    def __init__(self, config_path: str = "config.json"):
        self.config = load_config(config_path)

        self.scheduler = BackgroundScheduler(timezone=self.config.get("timezone", "UTC"))
        self.running = False
        self.lock = threading.Lock()

        # Initialize fetchers based on config
        self.fetchers = []
        platforms = self.config.get("platforms", {})
        if platforms.get("leetcode", True):
            self.fetchers.append(LeetCodeFetcher())
        if platforms.get("codeforces", True):
            self.fetchers.append(CodeForcesFetcher())
        if platforms.get("codechef", True):
            self.fetchers.append(CodeChefFetcher())
        if platforms.get("hackerrank", True):
            self.fetchers.append(HackerRankFetcher())
        if platforms.get("geeksforgeeks", True):
            self.fetchers.append(GeeksForGeeksFetcher())

        # Initialize notifier via factory (supports Telegram, Twilio, or both)
        self.notifier = get_notifier(self.config)

        self.last_contests: List[Dict] = []
        self.last_run: datetime = None

    def fetch_all_contests(self) -> List[Dict]:
        """Fetch contests from all enabled platforms"""
        all_contests = []
        for fetcher in self.fetchers:
            print(f"[Agent] Fetching from {fetcher.name}...")
            contests = fetcher.fetch()
            print(f"[Agent] {fetcher.name}: {len(contests)} contests found")
            all_contests.extend(contests)

        # Sort by start time
        all_contests.sort(key=lambda x: x["start_time"])
        self.last_contests = all_contests
        self.last_run = datetime.now()
        return all_contests

    def send_weekly_digest(self):
        """Weekly job: fetch all upcoming contests and send full digest"""
        print(f"\n[Agent] Running weekly digest at {datetime.now()}")
        contests = self.fetch_all_contests()
        message = self.notifier.format_message(
            contests, 
            look_ahead_days=self.config.get("look_ahead_days", 7)
        )
        success = self.notifier.send(message)
        if success:
            print("[Agent] Weekly digest sent successfully!")
        else:
            print("[Agent] Failed to send weekly digest.")

    def send_daily_alert(self):
        """Daily morning job: send SMS only if there are contests today"""
        print(f"\n[Agent] Running daily contest check at {datetime.now()}")
        contests = self.fetch_all_contests()
        message = self.notifier.format_daily_message(contests)
        if message is None:
            print("[Agent] No contests today — skipping SMS.")
            return
        success = self.notifier.send(message)
        if success:
            print("[Agent] Daily alert sent successfully!")
        else:
            print("[Agent] Failed to send daily alert.")

    def start(self):
        """Start the agent scheduler"""
        with self.lock:
            if self.running:
                print("[Agent] Already running!")
                return False

            schedule = self.config.get("schedule", {})

            # Sunday 10 AM
            if "sunday" in schedule:
                sun = schedule["sunday"]
                self.scheduler.add_job(
                    self.send_weekly_digest,
                    CronTrigger(day_of_week="sun", hour=sun["hour"], minute=sun["minute"]),
                    id="sunday_digest",
                    replace_existing=True
                )
                print(f"[Agent] Scheduled: Sunday {sun['hour']:02d}:{sun['minute']:02d}")

            # Wednesday 6 AM
            if "wednesday" in schedule:
                wed = schedule["wednesday"]
                self.scheduler.add_job(
                    self.send_weekly_digest,
                    CronTrigger(day_of_week="wed", hour=wed["hour"], minute=wed["minute"]),
                    id="wednesday_digest",
                    replace_existing=True
                )
                print(f"[Agent] Scheduled: Wednesday {wed['hour']:02d}:{wed['minute']:02d}")

            # Daily 8 AM alert (only fires SMS when there are contests that day)
            daily = self.config.get("daily_alert", {})
            if daily.get("enabled", True):
                d_hour = daily.get("hour", 8)
                d_minute = daily.get("minute", 0)
                self.scheduler.add_job(
                    self.send_daily_alert,
                    CronTrigger(hour=d_hour, minute=d_minute),
                    id="daily_morning_alert",
                    replace_existing=True
                )
                print(f"[Agent] Scheduled: Daily morning alert at {d_hour:02d}:{d_minute:02d}")

            self.scheduler.start()
            self.running = True
            print("[Agent] Started successfully!")
            return True

    def stop(self):
        """Stop the agent scheduler"""
        with self.lock:
            if not self.running:
                print("[Agent] Not running!")
                return False

            self.scheduler.shutdown(wait=False)
            self.running = False
            print("[Agent] Stopped.")
            return True

    def status(self) -> Dict:
        """Get current agent status"""
        channel = self.config.get("notification_channel", "telegram")
        if channel == "telegram":
            target = f"Telegram (Chat ID: {self.config.get('telegram', {}).get('chat_id') or 'Not Set'})"
        elif channel in ("twilio", "sms"):
            target = f"Twilio SMS ({self.config.get('phone_number')})"
        else:
            target = f"Both (Telegram + SMS {self.config.get('phone_number')})"

        return {
            "running": self.running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "total_contests_cached": len(self.last_contests),
            "platforms_enabled": [f.name for f in self.fetchers],
            "channel": channel,
            "target": target,
            "phone": self.config["phone_number"],
            "next_run": self._get_next_run_time()
        }

    def _get_next_run_time(self):
        """Get next scheduled run time"""
        try:
            jobs = self.scheduler.get_jobs()
            if jobs:
                next_times = [j.next_run_time for j in jobs if j.next_run_time]
                if next_times:
                    return min(next_times).isoformat()
        except:
            pass
        return None

    def run_now(self):
        """Trigger a manual run immediately"""
        print("[Agent] Manual run triggered...")
        self.send_weekly_digest()
