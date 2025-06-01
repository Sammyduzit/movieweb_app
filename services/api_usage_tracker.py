"""
API Usage Tracker - Tracks and enforces monthly API usage limits.
Provides persistent storage of API call counts with automatic monthly resets.
"""
import json
import os
from datetime import datetime
from pathlib import Path


class APIUsageTracker:
    """Track API usage and enforce monthly limits"""

    def __init__(self, limit=95):
        """
        Initialize API usage tracker.

        :param limit: Monthly API call limit
        """
        self.limit = limit
        self.usage_file = Path("instance/api_usage.json")
        self.usage_file.parent.mkdir(exist_ok=True)
        self._ensure_usage_file()

    def _ensure_usage_file(self):
        """
        Create usage file if it doesn't exist.

        :return: None
        """
        if not self.usage_file.exists():
            self._reset_usage()

    def _load_usage(self):
        """
        Load usage data from file with automatic monthly reset.

        :return: Dictionary containing usage data
        """
        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            last_reset = datetime.fromisoformat(data.get('last_reset', '2000-01-01'))
            current_date = datetime.now()

            if (current_date.year != last_reset.year or
                    current_date.month != last_reset.month):
                print(f"🔄 New month detected! Resetting API usage counter...")
                self._reset_usage()
                return self._load_usage()

            return data
        except (json.JSONDecodeError, FileNotFoundError):
            self._reset_usage()
            return self._load_usage()

    def _save_usage(self, data):
        """
        Save usage data to file.

        :param data: Dictionary containing usage data to save
        :return: None
        """
        """Save usage data to file"""
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _reset_usage(self):
        """
        Reset usage counter for new month.

        :return: None
        """
        current_time = datetime.now()
        data = {
            'calls_made': 0,
            'limit': self.limit,
            'last_reset': current_time.isoformat(),
            'month_year': current_time.strftime('%Y-%m')
        }
        self._save_usage(data)
        print(f"✅ API usage reset for {data['month_year']}")

    def can_make_call(self):
        """
        Check if we can make an API call without exceeding limit.

        :return: True if call can be made, False if limit reached
        """
        data = self._load_usage()
        remaining = self.limit - data['calls_made']

        if remaining <= 0:
            print(f"🚫 API limit reached ({data['calls_made']}/{self.limit})")
            print(f"📅 Resets on 1st of next month")
            return False

        print(f"✅ API calls remaining: {remaining}/{self.limit}")
        return True

    def record_call(self):
        """
        Record an API call and update usage statistics.

        :return: None
        """
        data = self._load_usage()
        data['calls_made'] += 1
        self._save_usage(data)

        remaining = self.limit - data['calls_made']
        print(f"📊 API call recorded: {data['calls_made']}/{self.limit} "
              f"({remaining} remaining)")

        if remaining <= 5:
            print(f"⚠️ WARNING: Only {remaining} API calls left this month!")

    def get_usage_stats(self):
        """
        Get current usage statistics.

        :return: Dictionary containing usage statistics
        """
        data = self._load_usage()
        return {
            'calls_made': data['calls_made'],
            'limit': self.limit,
            'remaining': self.limit - data['calls_made'],
            'month_year': data['month_year'],
            'last_reset': data['last_reset']
        }

    def force_reset(self):
        """
        Manually reset usage counter (for testing purposes).

        :return: None
        """
        self._reset_usage()
        print("🔧 API usage manually reset")