import datetime
import calendar

one_day = datetime.timedelta(days=1)

def get_week_dates(date, length=7):
   """Would be much simpler in python 2.5 with the Calendar class
   """
   week = []
   date = date - datetime.timedelta(days=date.weekday())
   for x in range(0, length):
      week.append(date)
      date = date + one_day
   return week

def find_week_no(aday):
    month_cal = enumerate(calendar.monthcalendar(aday.year, aday.month))
    for week_no, week in month_cal:
        if aday.day in week:
            return week_no

def get_month_end(aday):
    return datetime.date(aday.year, aday.month, calendar.monthrange(aday.year, aday.month)[1])

def get_month_start(aday):
    return datetime.date(aday.year, aday.month, 1)

def get_next_month_start(aday):
    return get_month_end(aday) + datetime.timedelta(1)

def advance_one_month(aday):
    return get_month_end(aday) + datetime.timedelta(aday.day)

def find_by_weekday_for_week_no(aday, weekday, weekday_no):
    """
    aday: date/datetime object
    weekday: int 6:Sun, 0:Mon ..
    weekday_no: int
    ex. To find 3rd Friday in current month
    now = datetime.datetime.now()
    find_by_weekday_for_week_no(now, 4, 3)
    """
    month_cal = calendar.monthcalendar(aday.year, aday.month)
    weekday_no -= 1
    all_weekdays = list(week[weekday] for week in month_cal if week[weekday])
    if len(all_weekdays) >= weekday_no:
        return datetime.date(aday.year, aday.month, all_weekdays[weekday_no])

if __name__ == '__main__':
    import datetime
    now=datetime.datetime.now()
    print find_by_weekday_for_week_no(now, 4 ,3).ctime()
