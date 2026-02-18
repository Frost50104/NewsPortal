import pytz

def all_timezones(request):
    return {'all_timezones': pytz.common_timezones}
