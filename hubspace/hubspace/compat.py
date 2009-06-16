import datetime
from calendar import *

class Calendar(object):
    """
    Base calendar class. This class doesn't do any formatting. It simply
    provides data to subclasses.
    """

    def __init__(self, firstweekday=0):
        self.firstweekday = firstweekday # 0 = Monday, 6 = Sunday

    def getfirstweekday(self):
        return self._firstweekday % 7

    def setfirstweekday(self, firstweekday):
        self._firstweekday = firstweekday

    firstweekday = property(getfirstweekday, setfirstweekday)

    def iterweekdays(self):
        """
        Return a iterator for one week of weekday numbers starting with the
        configured first one.
        """
        for i in xrange(self.firstweekday, self.firstweekday + 7):
            yield i%7

    def itermonthdates(self, year, month):
        """
        Return an iterator for one month. The iterator will yield datetime.date
        values and will always iterate through complete weeks, so it will yield
        dates outside the specified month.
        """
        date = datetime.date(year, month, 1)
        # Go back to the beginning of the week
        days = (date.weekday() - self.firstweekday) % 7
        date -= datetime.timedelta(days=days)
        oneday = datetime.timedelta(days=1)
        while True:
            yield date
            date += oneday
            if date.month != month and date.weekday() == self.firstweekday:
                break

    def itermonthdays2(self, year, month):
        """
        Like itermonthdates(), but will yield (day number, weekday number)
        tuples. For days outside the specified month the day number is 0.
        """
        for date in self.itermonthdates(year, month):
            if date.month != month:
                yield (0, date.weekday())
            else:
                yield (date.day, date.weekday())

    def itermonthdays(self, year, month):
        """
        Like itermonthdates(), but will yield day numbers tuples. For days
        outside the specified month the day number is 0.
        """
        for date in self.itermonthdates(year, month):
            if date.month != month:
                yield 0
            else:
                yield date.day

    def monthdatescalendar(self, year, month):
        """
        Return a matrix (list of lists) representing a month's calendar.
        Each row represents a week; week entries are datetime.date values.
        """
        dates = list(self.itermonthdates(year, month))
        return [ dates[i:i+7] for i in xrange(0, len(dates), 7) ]

    def monthdays2calendar(self, year, month):
        """
        Return a matrix representing a month's calendar.
        Each row represents a week; week entries are
        (day number, weekday number) tuples. Day numbers outside this month
        are zero.
        """
        days = list(self.itermonthdays2(year, month))
        return [ days[i:i+7] for i in xrange(0, len(days), 7) ]

    def monthdayscalendar(self, year, month):
        """
        Return a matrix representing a month's calendar.
        Each row represents a week; days outside this month are zero.
        """
        days = list(self.itermonthdays(year, month))
        return [ days[i:i+7] for i in xrange(0, len(days), 7) ]

    def yeardatescalendar(self, year, width=3):
        """
        Return the data for the specified year ready for formatting. The return
        value is a list of month rows. Each month row contains upto width months.
        Each month contains between 4 and 6 weeks and each week contains 1-7
        days. Days are datetime.date objects.
        """
        months = [
            self.monthdatescalendar(year, i)
            for i in xrange(January, January+12)
        ]
        return [months[i:i+width] for i in xrange(0, len(months), width) ]

    def yeardays2calendar(self, year, width=3):
        """
        Return the data for the specified year ready for formatting (similar to
        yeardatescalendar()). Entries in the week lists are
        (day number, weekday number) tuples. Day numbers outside this month are
        zero.
        """
        months = [
            self.monthdays2calendar(year, i)
            for i in xrange(January, January+12)
        ]
        return [months[i:i+width] for i in xrange(0, len(months), width) ]

    def yeardayscalendar(self, year, width=3):
        """
        Return the data for the specified year ready for formatting (similar to
        yeardatescalendar()). Entries in the week lists are day numbers.
        Day numbers outside this month are zero.
        """
        months = [
            self.monthdayscalendar(year, i)
            for i in xrange(January, January+12)
        ]
        return [months[i:i+width] for i in xrange(0, len(months), width) ]


