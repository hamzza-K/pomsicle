from datetime import datetime


def parse_poms_date(poms_date: str) -> str:
    """
    Converts /Date(1764245832000)/ to ISO string: 2025-11-27T04:17:12.000000
    """
    try:
        # Extract number inside /Date(...)/ 
        millis = int(poms_date.replace('/Date(', '').replace(')/', ''))
        dt = datetime.utcfromtimestamp(millis / 1000.0)
        return dt.isoformat()
    except Exception:
        return datetime.now().isoformat()
