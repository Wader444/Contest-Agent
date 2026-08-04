"""SMS Notifier using Twilio"""
from twilio.rest import Client
from typing import List, Dict, Optional
from datetime import datetime

class SMSNotifier:
    def __init__(self, account_sid: str, auth_token: str, from_number: str, to_number: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
        self.to_number = to_number

    def format_message(self, contests: List[Dict], look_ahead_days: int = 7) -> str:
        """Format contests into a nice SMS message"""
        now = datetime.now()

        # Filter contests within look_ahead window
        filtered = []
        for c in contests:
            delta = c["start_time"] - now
            if 0 <= delta.days <= look_ahead_days:
                filtered.append(c)

        if not filtered:
            return f"🎯 Weekly Coding Contests\n\nNo contests scheduled in the next {look_ahead_days} days!"

        # Sort by start time
        filtered.sort(key=lambda x: x["start_time"])

        lines = ["🎯 Weekly Coding Contests", "=" * 25, ""]

        current_date = None
        for c in filtered:
            start = c["start_time"]
            date_str = start.strftime("%a, %d %b")
            time_str = start.strftime("%I:%M %p")

            if date_str != current_date:
                lines.append(f"📅 {date_str}")
                current_date = date_str

            duration_hr = c["duration_minutes"] // 60
            duration_str = f"{duration_hr}h" if duration_hr > 0 else f"{c['duration_minutes']}m"

            lines.append(f"  • {c['platform']}: {c['name']}")
            lines.append(f"    🕐 {time_str} | ⏱️ {duration_str}")
            lines.append(f"    🔗 {c['url']}")
            lines.append("")

        lines.append("Happy Coding! 💪")
        return "\n".join(lines)

    def format_daily_message(self, contests: List[Dict]) -> Optional[str]:
        """Format only today's contests into a morning alert SMS.
        Returns None if there are no contests today (so no SMS is sent)."""
        today = datetime.now().date()

        todays_contests = [
            c for c in contests
            if c["start_time"].date() == today
        ]

        if not todays_contests:
            return None  # No contests today — caller should skip sending

        todays_contests.sort(key=lambda x: x["start_time"])

        date_str = datetime.now().strftime("%A, %d %b")
        lines = [
            f"🌅 Good Morning! Contest Alert",
            f"📅 {date_str}",
            "=" * 25,
            ""
        ]

        for c in todays_contests:
            time_str = c["start_time"].strftime("%I:%M %p")
            duration_hr = c["duration_minutes"] // 60
            duration_min = c["duration_minutes"] % 60

            if duration_hr > 0 and duration_min > 0:
                duration_str = f"{duration_hr}h {duration_min}m"
            elif duration_hr > 0:
                duration_str = f"{duration_hr}h"
            else:
                duration_str = f"{c['duration_minutes']}m"

            lines.append(f"🏆 {c['platform']}: {c['name']}")
            lines.append(f"   🕐 Starts at {time_str} | ⏱️ {duration_str}")
            lines.append(f"   🔗 {c['url']}")
            lines.append("")

        lines.append("Good luck today! 💪🔥")
        return "\n".join(lines)

    def send(self, message: str) -> bool:
        """Send SMS via Twilio"""
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )
            print(f"[SMS] Sent! SID: {msg.sid}")
            return True
        except Exception as e:
            print(f"[SMS] Failed to send: {e}")
            return False
