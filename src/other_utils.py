import datetime

import src.settings as settings

def is_off_hours() -> bool:
    """Return true if now is out of hours."""
    return settings.off_hours[0] <= datetime.datetime.now().time() < settings.off_hours[1]