# disable pylint for the entire file
# pylint: disable=all

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from pydantic import (
    AnyUrl,
    BaseModel,
    NonNegativeFloat,
    NonNegativeInt,
    constr,
    field_validator,
)

from vids_db.date import iso_fmt, parse_datetime


def parse_duration(duration: str) -> float:
    """
    Checks that the duration is in the format HH:MM:SS.
    Other acceptable formats include SS.
    Ok:
      ""
      "?"
      06
      6
      60
      61
      23:24
      23:24:01.34
    Not Ok:
      -7
      61  # above 60 seconds
      61:01 # above 60 minutes
      25:24:01.34 # above 24 hours
    """

    def _raise() -> None:
        raise ValueError(f"Invalid duration: {duration}")

    def _is_non_neg_int(s: str) -> bool:
        try:
            return int(s) >= 0
        except ValueError:
            return False

    def _is_non_neg_float(s: str) -> bool:
        try:
            return float(s) >= 0.0
        except ValueError:
            return False

    try:
        valf = float(duration)
        if valf >= 0.0:
            return valf
        else:
            _raise()
    except ValueError:
        pass

    if "" == duration or "?" == duration or "Live" == duration:
        return 0
    # Simple case
    no_column = ":" not in duration
    no_period = "." not in duration
    if no_column and no_period:
        try:
            tmp = float(duration)
            if tmp < 0:
                _raise()
            return tmp
        except ValueError:
            _raise()
    new_duration = duration
    units = new_duration.split(":")
    if len(units) > 3 or len(units) < 1:
        _raise()
    units.reverse()
    total: float = 0.0
    limit_multiplier = [
        (60, 1),
        (60, 60),
        (24, 60 * 60),
    ]
    for i, unit in enumerate(units):
        if i == 0:
            is_valid_number = _is_non_neg_float(unit)
        else:
            is_valid_number = _is_non_neg_int(unit)
        if not is_valid_number:
            _raise()
        limit, multipler = limit_multiplier[i]
        val = float(unit)
        if val >= limit:
            _raise()
        total += val * multipler
    return total


class Video(BaseModel):
    """Represents a video object."""

    channel_name: constr(min_length=2)  # type: ignore
    title: constr(min_length=2)  # type: ignore
    date_published: datetime  # from the scraped website
    date_lastupdated: datetime
    channel_url: str
    source: constr(min_length=4)  # type: ignore
    url: str
    duration: NonNegativeFloat
    description: str
    img_src: str
    iframe_src: str
    views: NonNegativeInt
    # rank: Optional[float] = None  # optional stdev rank.

    @field_validator("duration", mode="before")
    @classmethod
    def check_duration(cls, v):
        return parse_duration(v)

    @field_validator("date_published", mode="before")
    @classmethod
    def check_date_published(cls, v):
        data = parse_datetime(f"{v}")
        assert data.tzinfo, f"data {v} is time zone naive."
        return iso_fmt(v)

    @field_validator("date_lastupdated", mode="before")
    @classmethod
    def check_date_lastupdated(cls, v):
        data = parse_datetime(f"{v}")
        assert data.tzinfo, f"data {v} is time zone naive."
        return iso_fmt(v)

    @field_validator("views", mode="before")
    @classmethod
    def check_views(cls, v):
        if v == "" or v == "?":
            return 0
        if isinstance(v, str):
            # Remove any non-digit characters (like commas)
            v = ''.join(filter(str.isdigit, v))
        try:
            return int(v)
        except ValueError:
            return 0

    @classmethod
    def from_list_of_dicts(cls, data: List[Dict]) -> List[Video]:
        out: List[Video] = []
        for datum in data:
            vid = Video(**datum)
            out.append(vid)
        return out

    @classmethod
    def to_plain_list(cls, data: List[Video]) -> List[Dict]:
        out = []
        vid: Video
        for vid in data:
            out.append(vid.dict())
        return out

    @classmethod
    def parse_json(cls, data: Union[str, dict]) -> List[dict]:
        """
        Parses a string or json dict and returns a json dict representation
        that can be used in a network request.
        """
        out: List[dict] = []
        if isinstance(data, str):
            json_data = json.loads(data)
        else:
            json_data = data
        if "content" in json_data:  # This is the publishing format.
            json_data = json_data["content"]
        for json_video in json_data:
            try:
                vid = Video(**json_video)
                out.append(vid.to_json())
            except Exception as err:
                print(
                    f"{__file__}: Skipping {json_video.get('url')} because {err}"
                )
        return out

    def video_age_seconds(self, now_time: Optional[datetime] = None) -> float:
        """
        Returns the date published as a datetime object.
        """
        now_time = now_time or datetime.now()
        diff: timedelta = now_time - parse_datetime(self.date_published)
        return diff.total_seconds()

    def to_json(self) -> dict:
        """
        Returns a json representation of the video object.
        """
        # data = self.model_dump()
        # data["date_published"] = self.date_published.isoformat()
        # data["date_lastupdated"] = self.date_lastupdated.isoformat()
        # data["url"] = str(self.url)
        # data["img_src"] = str(self.img_src)
        data = {}
        items = self.model_dump().items()
        for key, val in items:
            if isinstance(val, datetime):
                data[key] = val.isoformat()
            elif isinstance(val, AnyUrl):
                data[key] = str(val)
            else:
                data[key] = val
        return data

    def to_json_str(self) -> str:
        """
        Returns a json string representation of the video object.
        """
        return json.dumps(self.to_json(), ensure_ascii=False)
