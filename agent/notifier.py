"""Notification services for Contest Agent (Telegram & SMS via Twilio)"""
import html
import requests
from typing import List, Dict, Optional, Union
from datetime import datetime
from twilio.rest import Client


class SMSNotifier:
    """SMS Notifier using Twilio"""
    def __init__(self, account_sid: str, auth_token: str, from_number: str, to_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.to_number = to_number
        self._client = None

    @property
    def client(self):
        if self._client is None and self.account_sid and self.auth_token:
            self._client = Client(self.account_sid, self.auth_token)
        return self._client

    def format_message(self, contests: List[Dict], look_ahead_days: int = 7) -> str:
        """Format contests into a nice SMS message"""
        now = datetime.now()

        # Filter contests within look_ahead window
        filtered = []
        for c in contests:
            delta = c["start_time"] - now
            total_hours = delta.total_seconds() / 3600
            if 0 < total_hours <= look_ahead_days * 24:
                filtered.append(c)

        if not filtered:
            return f"🎯 Weekly Coding Contests\n\nNo contests scheduled in the next {look_ahead_days} days!"

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
        """Format only today's contests into a morning alert SMS."""
        today = datetime.now().date()

        todays_contests = [
            c for c in contests
            if c["start_time"].date() == today
        ]

        if not todays_contests:
            return None

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
            if not self.client:
                print("[SMS] Failed: Twilio credentials not configured")
                return False
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


class TelegramNotifier:
    """100% Free Notifier using Telegram Bot API"""
    def __init__(self, bot_token: str, chat_id: Union[str, int]):
        self.bot_token = bot_token.strip() if bot_token else ""
        self.chat_id = str(chat_id).strip() if chat_id else ""
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def format_message(self, contests: List[Dict], look_ahead_days: int = 7) -> str:
        """Format contests into a rich HTML Telegram message"""
        now = datetime.now()

        # Filter contests within look_ahead window
        filtered = []
        for c in contests:
            delta = c["start_time"] - now
            total_hours = delta.total_seconds() / 3600
            if 0 < total_hours <= look_ahead_days * 24:
                filtered.append(c)

        if not filtered:
            return f"🎯 <b>Weekly Coding Contests</b>\n\nNo contests scheduled in the next {look_ahead_days} days!"

        filtered.sort(key=lambda x: x["start_time"])

        lines = [
            "🎯 <b>Weekly Coding Contests</b>",
            "━━━━━━━━━━━━━━━━━━━━━",
            ""
        ]

        current_date = None
        for c in filtered:
            start = c["start_time"]
            date_str = start.strftime("%A, %d %b")
            time_str = start.strftime("%I:%M %p")

            if date_str != current_date:
                lines.append(f"📅 <b>{date_str}</b>")
                current_date = date_str

            duration_hr = c["duration_minutes"] // 60
            duration_min = c["duration_minutes"] % 60
            if duration_hr > 0 and duration_min > 0:
                duration_str = f"{duration_hr}h {duration_min}m"
            elif duration_hr > 0:
                duration_str = f"{duration_hr}h"
            else:
                duration_str = f"{c['duration_minutes']}m"

            safe_name = html.escape(c.get("name", "Contest"))
            safe_platform = html.escape(c.get("platform", "Platform"))
            url = c.get("url", "#")

            lines.append(f"• <b>{safe_platform}</b>: <a href=\"{url}\">{safe_name}</a>")
            lines.append(f"  🕐 <code>{time_str}</code> | ⏱️ <code>{duration_str}</code>")
            lines.append("")

        lines.append("Happy Coding! 💪🚀")
        return "\n".join(lines)

    def format_daily_message(self, contests: List[Dict]) -> Optional[str]:
        """Format today's contests into a rich morning alert"""
        today = datetime.now().date()

        todays_contests = [
            c for c in contests
            if c["start_time"].date() == today
        ]

        if not todays_contests:
            return None

        todays_contests.sort(key=lambda x: x["start_time"])

        date_str = datetime.now().strftime("%A, %d %b")
        lines = [
            "🌅 <b>Good Morning! Contest Alert</b>",
            f"📅 <b>{date_str}</b>",
            "━━━━━━━━━━━━━━━━━━━━━",
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

            safe_name = html.escape(c.get("name", "Contest"))
            safe_platform = html.escape(c.get("platform", "Platform"))
            url = c.get("url", "#")

            lines.append(f"🏆 <b>{safe_platform}</b>: <a href=\"{url}\">{safe_name}</a>")
            lines.append(f"   🕐 Starts at <code>{time_str}</code> | ⏱️ <code>{duration_str}</code>")
            lines.append("")

        lines.append("Good luck today! 💪🔥")
        return "\n".join(lines)

    def send(self, message: str) -> bool:
        """Send message via Telegram Bot API with chunking support"""
        if not self.bot_token or not self.chat_id:
            print("[Telegram] Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing!")
            return False

        # Telegram message limit is 4096 characters. Chunk if necessary.
        chunks = []
        if len(message) <= 4000:
            chunks.append(message)
        else:
            lines = message.split("\n")
            cur_chunk = ""
            for line in lines:
                if len(cur_chunk) + len(line) + 1 > 4000:
                    chunks.append(cur_chunk)
                    cur_chunk = line
                else:
                    cur_chunk += ("\n" + line if cur_chunk else line)
            if cur_chunk:
                chunks.append(cur_chunk)

        success = True
        for chunk in chunks:
            payload = {
                "chat_id": self.chat_id,
                "text": chunk,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            try:
                resp = requests.post(self.api_url, json=payload, timeout=15)
                res_data = resp.json()
                if resp.status_code == 200 and res_data.get("ok"):
                    print(f"[Telegram] Sent message successfully! (msg_id: {res_data.get('result', {}).get('message_id')})")
                else:
                    print(f"[Telegram] Failed to send: {res_data.get('description', resp.text)}")
                    success = False
            except Exception as e:
                print(f"[Telegram] Error sending message: {e}")
                success = False

        return success


class MultiNotifier:
    """Notifier that can dispatch to Telegram, SMS, or both"""
    def __init__(self, notifiers: List):
        self.notifiers = notifiers

    def format_message(self, contests: List[Dict], look_ahead_days: int = 7) -> str:
        if self.notifiers:
            return self.notifiers[0].format_message(contests, look_ahead_days)
        return ""

    def format_daily_message(self, contests: List[Dict]) -> Optional[str]:
        if self.notifiers:
            return self.notifiers[0].format_daily_message(contests)
        return None

    def send(self, message: str) -> bool:
        overall_success = True
        for n in self.notifiers:
            # Reformat if notifier has specific formatting
            res = n.send(message)
            if not res:
                overall_success = False
        return overall_success


def get_notifier(config: Dict) -> Union[TelegramNotifier, SMSNotifier, MultiNotifier]:
    """Factory to instantiate the appropriate notifier based on configuration"""
    channel = config.get("notification_channel", "telegram").lower()
    telegram_cfg = config.get("telegram", {})
    twilio_cfg = config.get("twilio", {})

    t_notifier = TelegramNotifier(
        bot_token=telegram_cfg.get("bot_token", ""),
        chat_id=telegram_cfg.get("chat_id", "")
    )

    s_notifier = SMSNotifier(
        account_sid=twilio_cfg.get("account_sid", ""),
        auth_token=twilio_cfg.get("auth_token", ""),
        from_number=twilio_cfg.get("from_number", ""),
        to_number=config.get("phone_number", "")
    )

    if channel == "telegram":
        return t_notifier
    elif channel in ("twilio", "sms"):
        return s_notifier
    elif channel in ("both", "all"):
        return MultiNotifier([t_notifier, s_notifier])
    else:
        # Default fallback: Telegram if configured, else SMS
        if telegram_cfg.get("bot_token"):
            return t_notifier
        return s_notifier

