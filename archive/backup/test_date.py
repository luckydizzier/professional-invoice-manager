#!/usr/bin/env python3
import time
from datetime import datetime

def format_date(timestamp: int) -> str:
    """Convert UTC timestamp to formatted date string"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

# Test the function
current_time = int(time.time())
print(f"Current timestamp: {current_time}")
print(f"Formatted date: {format_date(current_time)}")

# Test with a specific date
test_timestamp = 1733788800  # This should be around Dec 10, 2024
print(f"Test timestamp: {test_timestamp}")
print(f"Test formatted date: {format_date(test_timestamp)}")
