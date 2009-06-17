from datetime import timedelta

one_day = timedelta(days=1)

def get_week_dates(date, length=7):
   """Would be much simpler in python 2.5 with the Calendar class
   """
   week = []
   date = date - timedelta(days=date.weekday())
   for x in range(0, length):
      week.append(date)
      date = date + one_day
   return week
