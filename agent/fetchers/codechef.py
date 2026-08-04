"""CodeChef Contest Fetcher"""
import requests
from datetime import datetime
from typing import List, Dict

class CodeChefFetcher:
    name = "CodeChef"

    def fetch(self) -> List[Dict]:
        """Fetch upcoming CodeChef contests"""
        url = "https://www.codechef.com/api/list/contests/all"
        try:
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            data = resp.json()
            contests = []

            for c in data.get("future_contests", []):
                try:
                    # Parse "15 Jul 2026  19:30:00" format
                    start_str = c.get("contest_start_date", "").strip()
                    start_dt = datetime.strptime(start_str, "%d %b %Y  %H:%M:%S")

                    contests.append({
                        "platform": self.name,
                        "name": c["contest_name"],
                        "url": f"https://www.codechef.com/{c['contest_code']}",
                        "start_time": start_dt,
                        "duration_minutes": self._parse_duration(c.get("contest_duration", "0")),
                        "raw": c
                    })
                except Exception as inner_e:
                    continue
            return contests
        except Exception as e:
            print(f"[CodeChef] Error: {e}")
            return []

    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration like '180 minutes' to int"""
        try:
            return int(duration_str.split()[0])
        except:
            return 120
