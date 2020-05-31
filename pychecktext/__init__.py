import datetime
from dateutil import tz
import teamcity.messages as tc

try:
    from teamcity import is_running_under_teamcity
    if is_running_under_teamcity():
        teamcity = True
    else:
        teamcity = False
except ImportError:
    teamcity = False

teamcity_messages = tc.TeamcityServiceMessages()
