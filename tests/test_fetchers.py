"""Unit tests for contest fetchers"""
import unittest
from datetime import datetime
from agent.fetchers import (
    LeetCodeFetcher, CodeForcesFetcher, CodeChefFetcher,
    HackerRankFetcher, GeeksForGeeksFetcher
)

class TestFetchers(unittest.TestCase):
    def test_leetcode_fetch(self):
        f = LeetCodeFetcher()
        contests = f.fetch()
        self.assertIsInstance(contests, list)
        print(f"LeetCode: {len(contests)} contests")

    def test_codeforces_fetch(self):
        f = CodeForcesFetcher()
        contests = f.fetch()
        self.assertIsInstance(contests, list)
        print(f"CodeForces: {len(contests)} contests")

    def test_codechef_fetch(self):
        f = CodeChefFetcher()
        contests = f.fetch()
        self.assertIsInstance(contests, list)
        print(f"CodeChef: {len(contests)} contests")

    def test_hackerrank_fetch(self):
        f = HackerRankFetcher()
        contests = f.fetch()
        self.assertIsInstance(contests, list)
        print(f"HackerRank: {len(contests)} contests")

    def test_geeksforgeeks_fetch(self):
        f = GeeksForGeeksFetcher()
        contests = f.fetch()
        self.assertIsInstance(contests, list)
        print(f"GeeksForGeeks: {len(contests)} contests")

if __name__ == "__main__":
    unittest.main()
