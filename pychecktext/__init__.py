import datetime
from dateutil import tz

try:
    from teamcity import is_running_under_teamcity
    if is_running_under_teamcity():
        teamcity = True
    else:
        teamcity = False
except ImportError:
    teamcity = False


def get_timestamp():
    timestamp = datetime.datetime.now(tz=tz.tzlocal()).strftime('%Y-%M-%dT%X.%f%z')
    return timestamp
