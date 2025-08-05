"""
Timezone utility functions for EHS Electronic Journal
Handles EST/UTC conversion and formatting
"""

from datetime import datetime, timezone, timedelta
import pytz

# EST timezone (UTC-5)
EST = pytz.timezone('US/Eastern')

def get_est_time() -> datetime:
    """Get current time in EST timezone"""
    utc_now = datetime.now(timezone.utc)
    return utc_now.astimezone(EST)

def utc_to_est(utc_time: datetime) -> datetime:
    """Convert UTC datetime to EST"""
    if utc_time.tzinfo is None:
        utc_time = utc_time.replace(tzinfo=timezone.utc)
    return utc_time.astimezone(EST)

def est_to_utc(est_time: datetime) -> datetime:
    """Convert EST datetime to UTC"""
    if est_time.tzinfo is None:
        est_time = EST.localize(est_time)
    return est_time.astimezone(timezone.utc)

def format_est_datetime(dt: datetime) -> str:
    """Format datetime in EST as MM/DD/YYYY H:MM AM/PM"""
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc)
    
    est_time = dt.astimezone(EST)
    return est_time.strftime("%m/%d/%Y %I:%M %p")

def parse_est_datetime(date_str: str) -> datetime:
    """Parse MM/DD/YYYY H:MM AM/PM format to EST datetime"""
    try:
        # Parse the string to naive datetime
        naive_dt = datetime.strptime(date_str, "%m/%d/%Y %I:%M %p")
        # Localize to EST
        est_dt = EST.localize(naive_dt)
        return est_dt
    except ValueError as e:
        raise ValueError(f"Invalid date format. Expected MM/DD/YYYY H:MM AM/PM, got: {date_str}") from e

def get_current_timestamp_utc() -> datetime:
    """Get current timestamp in UTC for database storage"""
    return datetime.now(timezone.utc)