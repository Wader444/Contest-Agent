"""CodeForces Contest Fetcher"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict

class CodeForcesFetcher:
    name = "CodeForces"

    def fetch(self) -> List[Dict]:
        """Fetch upcoming CodeForces contests via public API"""
        url = "https://codeforces.com/api/contest.list"
        try:
            resp = requests.get(url, timeout=15)
            data = resp.json()
            contests = []

            if data.get("status") != "OK":
                return []

            for c in data.get("result", []):
                if c.get("phase") == "BEFORE":
                    start_ts = c.get("startTimeSeconds", 0)
                    start_dt = datetime.fromtimestamp(start_ts)
                    duration_min = c.get("durationSeconds", 0) // 60
                    contests.append({
                        "platform": self.name,
                        "name": c["name"],
                        "url": f"https://codeforces.com/contests/{c['id']}",
                        "start_time": start_dt,
                        "duration_minutes": duration_min,
                        "raw": c
                    })
            return contests
        except Exception as e:
            print(f"[CodeForces] Error: {e}")
            return []
