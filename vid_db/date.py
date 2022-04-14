# pylint: disable=all
# types: disable=all

import time
from datetime import datetime, tzinfo
from re import findall
from typing import Optional, Union

import pytz  # type: ignore
from dateutil.parser import parse

CURRENT_TIME_ZONE_STR = "America/New_York"


def _my_date_parse(date_string: str) -> datetime:
    try:
        return datetime.fromisoformat(date_string)
    except ValueError as verr:
        if "Invalid isoformat" in str(verr):
            return parse(date_string, fuzzy=True)
        else:
            raise


def get_current_tzinfo() -> tzinfo:
    tz = pytz.timezone(CURRENT_TIME_ZONE_STR)
    return tz


def utc_timestamp_to_utc_datetime(ts: Union[str, int, float]) -> datetime:
    ts = float(ts)
    dt = datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc)
    return dt


def utc_timestamp_to_local_timestring(ts):
    dt = utc_timestamp_to_utc_datetime(ts)
    tz = pytz.timezone(CURRENT_TIME_ZONE_STR)
    dt = dt.astimezone(tz)
    out = str(dt)
    return out


def parse_date_to_unix_utc(date_string: str) -> float:
    dt = parse_datetime(date_string, tzinfo=pytz.utc)
    return dt.timestamp()


def parse_datetime(s, tzinfo=None) -> datetime:  # type: ignore
    date: datetime = _my_date_parse(s)
    if tzinfo:
        if isinstance(tzinfo, str):
            tzinfo = pytz.timezone(tzinfo)
        if date.tzinfo is None:
            date = date.replace(tzinfo=tzinfo)
        else:
            date = date.astimezone(tzinfo)
    return date


def iso_fmt(date_obj: Union[datetime, str]) -> str:
    if isinstance(date_obj, datetime):
        return date_obj.isoformat()
    elif isinstance(date_obj, str):
        return parse_datetime(date_obj).isoformat()
    else:
        raise ValueError(f"{__file__} Unexpected type: {type(date_obj)}")


def now_local(tz_str: Optional[str] = None) -> datetime:
    """Returns timezone aware now, which allows subtractions"""
    tz_str = tz_str or CURRENT_TIME_ZONE_STR
    ts = datetime.now()
    tz = pytz.timezone(tz_str)
    ts = ts.astimezone(tz)
    return ts


def now_utc() -> datetime:
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def now_utc_timestamp() -> int:
    return int(now_utc().timestamp())


def time_utc() -> float:
    return time.time()


# Example:
#   assert iso8601_duration_as_seconds('PT25M0S') == 1500


def iso8601_duration_as_seconds(d: str) -> int:
    if d[0] != "P":
        raise ValueError("Not an ISO 8601 Duration string")
    seconds = 0
    # split by the 'T'
    for i, item in enumerate(d.split("T")):
        for number, unit in findall(r"(?P<number>\d+)(?P<period>S|M|H|D|W|Y)", item):
            # print '%s -> %s %s' % (d, number, unit )
            number = int(number)
            this = 0
            if unit == "Y":
                this = number * 31557600  # 365.25
            elif unit == "W":
                this = number * 604800
            elif unit == "D":
                this = number * 86400
            elif unit == "H":
                this = number * 3600
            elif unit == "M":
                # ambiguity ellivated with index i
                if i == 0:
                    this = number * 2678400  # assume 30 days
                    # print "MONTH!"
                else:
                    this = number * 60
            elif unit == "S":
                this = number
            seconds = seconds + this
    return seconds
