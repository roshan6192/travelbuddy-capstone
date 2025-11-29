from datetime import datetime, timedelta
import dateparser
from dateparser.search import search_dates

def _next_occurrence_month(month: int, base_year: int):
    """
    Returns a datetime for the 1st of the next occurrence of `month`
    on or after base_year (choose nearest future year).
    """
    # try base_year, otherwise base_year+1
    try_dt = datetime(base_year, month, 1)
    if try_dt.date() >= datetime.utcnow().date():
        return try_dt
    return datetime(base_year + 1, month, 1)

def _ensure_future(dt: datetime):
    """If dt is in the past, push it to the next reasonable future date."""
    now = datetime.utcnow()
    if dt < now:
        # push to next year (rough heuristic)
        try:
            return dt.replace(year=now.year if dt.month >= now.month else now.year + 1)
        except Exception:
            return dt + timedelta(days=365)
    return dt

def extract_dates_from_text(text: str):
    """
    Return (depart_date_str, return_date_str) in 'YYYY-MM-DD'.
    Heuristics:
      - Try to parse explicit dates (e.g., 'Feb 5 to Feb 12').
      - If single month like 'in February', pick the next feasible day (1st of month).
      - If parsing gives a date with a weird year (< 1900), fix to nearest future year.
      - Ensure return_date >= depart_date (if not, set return = depart + 7 days).
      - Defaults: depart = today+14, return = depart+7
    """
    if not text:
        today = datetime.utcnow().date()
        depart = datetime.combine(today + timedelta(days=14), datetime.min.time())
        ret = depart + timedelta(days=7)
        return depart.strftime("%Y-%m-%d"), ret.strftime("%Y-%m-%d")

    found = search_dates(text, settings={"PREFER_DATES_FROM": "future"})
    dates = []
    if found:
        for _, dt in found:
            dates.append(dt)

    depart = None
    ret = None

    if len(dates) >= 2:
        depart, ret = dates[0], dates[1]
    elif len(dates) == 1:
        # single explicit date -> depart that date, return = +7 days
        depart = dates[0]
        ret = depart + timedelta(days=7)
    else:
        # Try simple parse (handles 'in February', 'February 2026', etc.)
        parsed = dateparser.parse(text, settings={"PREFER_DATES_FROM": "future"})
        if parsed:
            # If parsed only a month (year may be tiny/odd), normalize:
            depart = parsed
            ret = depart + timedelta(days=7)
        else:
            # Nothing found: default to depart in 14 days
            today = datetime.utcnow().date()
            depart = datetime.combine(today + timedelta(days=14), datetime.min.time())
            ret = depart + timedelta(days=7)

    # Defensive fixes: fix weird years, ensure future
    now = datetime.utcnow()
    if depart.year < 1900 or depart.year < now.year - 1:
        # if depart year is absurd (like 1200), set to nearest future year for same month/day
        depart = depart.replace(year=now.year)
        if depart < now:
            depart = depart.replace(year=now.year + 1)

    if ret:
        if ret.year < 1900 or ret.year < now.year - 1:
            ret = ret.replace(year=now.year)
            if ret < now:
                ret = ret.replace(year=now.year + 1)

    # ensure both are future and return >= depart
    depart = _ensure_future(depart)
    if not ret:
        ret = depart + timedelta(days=7)
    else:
        if ret < depart:
            ret = depart + timedelta(days=7)

    return depart.strftime("%Y-%m-%d"), ret.strftime("%Y-%m-%d")
