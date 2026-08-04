"""GeeksForGeeks Contest Fetcher"""
import requests
from datetime import datetime
from typing import List, Dict

class GeeksForGeeksFetcher:
    name = "GeeksForGeeks"

    def fetch(self) -> List[Dict]:
        """Fetch upcoming GFG contests"""
        url = "https://practiceapi.geeksforgeeks.org/api/v1/events/?type=contest&page_number=1&page_size=10"
        try:
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            data = resp.json()
            contests = []
            now = datetime.now()

            for c in data.get("results", []):
                try:
                    start_str = c.get("start_time", "")
                    # Try ISO format first
                    start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00")).replace(tzinfo=None)
                    if start_dt > now:
                        duration_min = c.get("duration", 120)  # default 2 hours
                        contests.append({
                            "platform": self.name,
                            "name": c.get("name", "Unnamed Contest"),
                            "url": c.get("url", "https://practice.geeksforgeeks.org/events"),
                            "start_time": start_dt,
                            "duration_minutes": duration_min,
                            "raw": c
                        })
                except Exception:
                    continue
            return contests
        except Exception as e:
            print(f"[GeeksForGeeks] Error: {e}")
            return []
