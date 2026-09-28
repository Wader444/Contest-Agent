"""CodeForces Contest Fetcher"""
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict

class CodeForcesFetcher:
    name = "CodeForces"

    def fetch(self) -> List[Dict]:
        """Fetch upcoming CodeForces contests via public API (with retries)"""
        url = "https://codeforces.com/api/contest.list"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        for attempt in range(3):
            try:
                resp = requests.get(url, timeout=15, headers=headers)
                if resp.status_code != 200 or not resp.text.strip():
                    print(f"[CodeForces] Attempt {attempt+1}: bad response (status {resp.status_code}), retrying...")
                    time.sleep(2)
                    continue

                data = resp.json()
                contests = []

                if data.get("status") != "OK":
                    print(f"[CodeForces] API returned status: {data.get('status')}")
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
                print(f"[CodeForces] Attempt {attempt+1} error: {e}")
                if attempt < 2:
                    time.sleep(2)

        print("[CodeForces] All retries failed, returning empty list.")
        return []
