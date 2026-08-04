"""HackerRank Contest Fetcher"""
import requests
from datetime import datetime
from typing import List, Dict

class HackerRankFetcher:
    name = "HackerRank"

    def fetch(self) -> List[Dict]:
        """Fetch upcoming HackerRank contests"""
        url = "https://www.hackerrank.com/rest/contests/upcoming"
        try:
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            data = resp.json()
            contests = []
            now = datetime.now()

            for c in data.get("models", []):
                try:
                    start_ts = c.get("epoch_starttime", 0)
                    start_dt = datetime.fromtimestamp(start_ts)
                    if start_dt > now:
                        duration_sec = c.get("epoch_endtime", 0) - start_ts
                        duration_min = duration_sec // 60
                        contests.append({
                            "platform": self.name,
                            "name": c.get("name", "Unnamed Contest"),
                            "url": f"https://www.hackerrank.com/contests/{c.get('slug', '')}",
                            "start_time": start_dt,
                            "duration_minutes": duration_min,
                            "raw": c
                        })
                except Exception:
                    continue
            return contests
        except Exception as e:
            print(f"[HackerRank] Error: {e}")
            return []
