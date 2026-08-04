"""LeetCode Contest Fetcher"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict

class LeetCodeFetcher:
    name = "LeetCode"

    def fetch(self) -> List[Dict]:
        """Fetch upcoming LeetCode contests via GraphQL API"""
        url = "https://leetcode.com/graphql"
        query = """
        query {
            allContests {
                title
                titleSlug
                startTime
                duration
                __typename
            }
        }
        """
        try:
            resp = requests.post(url, json={"query": query}, timeout=15)
            data = resp.json()
            contests = []
            now = datetime.now().timestamp()

            for c in data.get("data", {}).get("allContests", []):
                start_ts = c.get("startTime", 0)
                if start_ts > now:
                    start_dt = datetime.fromtimestamp(start_ts)
                    duration_min = c.get("duration", 0) // 60
                    contests.append({
                        "platform": self.name,
                        "name": c["title"],
                        "url": f"https://leetcode.com/contest/{c['titleSlug']}",
                        "start_time": start_dt,
                        "duration_minutes": duration_min,
                        "raw": c
                    })
            return contests
        except Exception as e:
            print(f"[LeetCode] Error: {e}")
            return []
