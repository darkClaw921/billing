from datetime import datetime, timedelta
def get_last_day_of_month():
    now = datetime.now()
    next_month = now.replace(day=28) + timedelta(days=4)  # this will never fail
    last_day_of_month = next_month - timedelta(days=next_month.day)
    last_day_of_month=last_day_of_month.replace(hour=23,minute=59,second=59)
    return last_day_of_month.isoformat(timespec='seconds')