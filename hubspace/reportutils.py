import datetime, itertools, time, calendar
import compat
from hubspace.model import Resource

def sortAndGrpby(iterable, keyfn, reverse=False):
    l = sorted(iterable, key=keyfn)
    return itertools.groupby(l, keyfn)

class r_schemes:
    quantity_based = 0
    time_based = 1

def datetime2date(dt, keepdate=True):
    if keepdate:
        return datetime.date(*dt.timetuple()[:3])
    else:
        return datetime.date(*(list(dt.timetuple()[:2])+[1]))

class TimeUnit(object):

    title = ""
    strfformat = "%b %d %Y"

    def __init__(self, resource):
        if resource.time_based:
            self.r_scheme = r_schemes.time_based
        else:
            self.r_scheme = r_schemes.quantity_based

    def getLabel(self, what): return what
    
    def dt2strf(self, dt):
        return dt.strftime(self.strfformat)

    def toEpochSecs(self, start):
        return int(time.mktime((start.year, start.month, start.day, 0, 0, 0, 0, 0, 0)))

    def getUsage(self, entry):
        """
        @entry: RUsage instance
        -> [(int:time since epoch, int:usage), ...]
        """
        raise NotImplemented

    def addTitlerow(self, rows):
        if self.r_scheme == r_schemes.time_based:
            title_row = (self.title, "Usage (Hrs)")
        else:
            title_row = (self.title, "Usage")
        rows.insert(0, title_row)
        return rows

    def getUsageSums(self, entries):
        flattened_entries = []
        [flattened_entries.extend(self.getUsage(ru)) for ru in entries]
        if self.r_scheme == r_schemes.time_based:
            sumusage = lambda entries: sum((e[2] for e in entries)) / (60 * 60.0)
        else:
            sumusage = lambda entries: sum((e[2] for e in entries))
        return [ [t, sumusage(entries_grp)] for (t, entries_grp) in sortAndGrpby(flattened_entries, lambda x: x[0]) ]

    def groupAndAverage(self, entries):
        flattened_entries = []
        [flattened_entries.extend(self.getUsage(ru)) for ru in entries]
        if self.r_scheme == r_schemes.time_based:
            def avgusage(entries):
                sum_entries = sum((e[2] for e in entries))
                timestamp_getter = lambda e: e[0]
                groups = [grp for (ts, grp) in sortAndGrpby(entries, timestamp_getter)]
                no_uniq_ts = len(list(groups))
                return sum_entries / (60 * 60 * no_uniq_ts)
        else:
            def avgusage(entries):
                sum_entries = sum((e[2] for e in entries))
                timestamp_getter = lambda e: e[0]
                groups = [grp for (ts, grp) in sortAndGrpby(entries, timestamp_getter)]
                no_uniq_ts = len(list(groups))
                return sum_entries / no_uniq_ts
        ret = [(self.getLabel(t), avgusage(list(entries_grp))) for (t, entries_grp) in sortAndGrpby(flattened_entries, lambda e: e[1])]
        return ret

class Hour(TimeUnit):

    title = "Hours"
    getLabel = lambda self, t: datetime.time(t).strftime("%l%p")
    strfformat = "%l%p"
    getRange = lambda x: xrange(24)

    def getUsage(self, entry):
        t_range = xrange(entry.start.hour, entry.end_time.hour + 1)
        abshr = datetime.datetime(entry.start.year, entry.start.month, entry.start.day, entry.start.hour)
        hrs_list = []

        if self.r_scheme == r_schemes.time_based:
            for t in t_range:
                if t == t_range[0]:
                    usage = (60 - entry.start.minute) * 60.0
                    hrs_list.append((entry.start, t, usage))
                elif t == t_range[-1]:
                    usage = entry.end_time.minute * 60.0
                    hrs_list.append((entry.start, t, usage))
                else:
                    hrs_list.append((entry.start, t, 60 * 60))
        else:
            hrs_list = [(entry.start, entry.start.hour, entry.quantity)]
        return hrs_list

class Month(TimeUnit):

    title = "Months"
    getLabel = lambda self, t: calendar.month_name.__getitem__(t)
    strfformat = "%b %Y"
    getRange = lambda x: xrange(1, 13)

    def toEpochSecs(self, start):
        return int(time.mktime((start.year, start.month, 0, 0, 0, 0, 0, 0, 0)))

    def getUsage(self, entry):
        if self.r_scheme == r_schemes.time_based:
            usage = (entry.end_time - entry.start).seconds
        else:
            usage = entry.quantity
        return [(datetime2date(entry.start, False), entry.start.month, usage)]

class Weekday(TimeUnit):

    title = "Weekdays"
    getLabel = lambda self, t: calendar.day_name.__getitem__(t)
    strfformat = "%b %d %Y"
    getRange = lambda x: compat.Calendar().iterweekdays()
    
    def getUsage(self, entry):

        if self.r_scheme == r_schemes.time_based:
            usage = (entry.end_time - entry.start).seconds
        else:
            usage = entry.quantity
        return [[datetime2date(entry.start), entry.start.weekday(), usage]]

class Day(TimeUnit):

    title = "Days"
    strfformat = "%b %d %Y"
    getRange = lambda x: xrange(1, 32)

    def getUsage(self, entry):
        if self.r_scheme == r_schemes.time_based:
            usage = (entry.end_time - entry.start).seconds
        else:
            usage = entry.quantity
        return [(datetime2date(entry.start), entry.start.day, usage)]

if __name__ == '__main__':

    t1 = datetime.datetime.now()
    t2 = t1 + datetime.timedelta(0, (60 * 60 * 2))
    t3 = t1 - datetime.timedelta(30)
    t4 = t3 + datetime.timedelta(0, (60 * 60 * 1))
    t5 = t3 - datetime.timedelta(365)
    t6 = t5 + datetime.timedelta(0, (60 * 60 * 3))
    
    class RU(object):
        pass
    
    ru1 = RU()
    ru1.start = t1
    ru1.end_time = t2
    
    ru2 = RU()
    ru2.start = t3
    ru2.end_time = t4
    
    ru3 = RU()
    ru3.start = t5
    ru3.end_time = t6
    
    entries = [ru1, ru2, ru3]
    
    
    hr = Hour()
    print hr.groupAndAverage(entries)
    
    print 
    
    mon = Month()
    print mon.groupAndAverage(entries)

    print 
    
    weekday = Weekday()
    print weekday.groupAndAverage(entries)
