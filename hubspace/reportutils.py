import datetime, itertools, time, calendar, os, time, thread, logging
from glob import glob
import compat
from collections import defaultdict
from hubspace.model import Resource, RUsage, Location, User, resource_types
from sqlobject.sqlbuilder import IN, Select, AND
from turbogears import identity
import tariff as tarifflib
import cairo
import pycha.bar
import pycha.pie
import pycha.line
import pycha.stackedbar

applogger = logging.getLogger("hubspace")

def sortAndGrpby(iterable, keyfn, reverse=False):
    l = sorted(iterable, key=keyfn)
    return itertools.groupby(l, keyfn)

report_img_dir = "tmp"
image_sizes = dict (small = (450, 400), big = (650, 600))
make_report_image_path = lambda: "%s/%s.png" % (report_img_dir, str(time.time()))
if not os.path.exists("tmp"): os.mkdir("tmp")

def do_report_maintainance():
    stale_imgfiles = (imgfile for imgfile in glob("%s/*.png" % report_img_dir) \
        if datetime.timedelta(0, (time.time() - os.path.getmtime (imgfile))) > datetime.timedelta(1))
    for f in stale_imgfiles:
        try:
            os.remove(f)
        except Exception, err:
            applogger.warn("reportutils: Error removing file: %s" % f)
    global get_all_usages
    get_all_usages = AllUsages()
    get_all_usages.update()

class Report(object):
    """
    pie: ( (label1, ((val1,),), label2, ((val2,),) ...)
    """
    sort_by_value = lambda self: sorted(self.data, key=lambda x: x[1][0], reverse=True)
    def __init__(self, data, options={}):
        self.data = data
        self.options = options
    def merge_options(self, chart_options):
        options = dict(colorScheme=dict(name="rainbow"), padding = dict(left = 75, bottom = 75))
        options.update(chart_options)
        options.update(self.options)
        return options
    def draw_pie_chart(self):
        width, height = (500, 400)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        chart_options = dict(legend=dict(hide=True))
        options = self.merge_options(chart_options)
        data_sorted = self.sort_by_value()
        data = data_sorted[:7]
        c = itertools.cycle((0, -1))
        data = [data.pop(c.next()) for x in range(len(data))]
        if data_sorted[7:]:
            others_value = sum(cell[1][0][1] for cell in data_sorted[7:])
            data.append(('others', ((0,others_value),)))
        chart = pycha.pie.PieChart(surface, options)
        chart.addDataset(data)
        chart.render()
        img_path = make_report_image_path()
        surface.write_to_png(img_path)
        return img_path
    def draw_multiline_chart(self):
        width, height = (500, 400)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        chart_options = dict(shouldFill=False)
        options = self.merge_options(chart_options)
        chart = pycha.line.LineChart(surface, options)
        chart.addDataset(self.data)
        chart.render()
        img_path = make_report_image_path()
        surface.write_to_png(img_path)
        return img_path
    def draw_hsbars_chart(self):
        width, height = (500, 400)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        chart_options = dict(legend=dict(position=dict(top=20, left=None, bottom=None, right=5)))
        options = self.merge_options(chart_options)
        chart = pycha.stackedbar.StackedHorizontalBarChart(surface, options)
        chart.addDataset(self.data)
        chart.render()
        img_path = make_report_image_path()
        surface.write_to_png(img_path)
        return img_path
    def draw_vbars_chart(self):
        width, height = (500, 400)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        bar_width = 0.75 if len(self.data[0][1]) > 3 else 0.50
        chart_options = dict(legend=dict(hide=True), barWidthFillFraction=bar_width)
        options = self.merge_options(chart_options)
        options.update(self.options)
        chart = pycha.bar.VerticalBarChart(surface, options)
        chart.addDataset(self.data)
        chart.render()
        img_path = make_report_image_path()
        surface.write_to_png(img_path)
        return img_path
    def save(self):
        pass

class RUsageCache(object):
    def __init__(self, ru):
        attrs2store = ('id', 'effectivecost', 'start', 'duration_or_quantity', 'resourceID', 'invoiceID', 'userID', 'tariffID')
        for attr in attrs2store:
            setattr(self, attr, getattr(ru, attr))
    def _get_resource(self):
        return Resource.get(self.resourceID)
    def _get_user(self):
        return User.get(self.userID)
    def _get_invoice(self):
        return User.get(self.userID)
    def _get_tariff(self):
        return Resource.get(self.tariffID)
    invoice = property(_get_invoice)
    user = property(_get_user)
    resource = property(_get_resource)
    tariff = property(_get_tariff)

class AllUsages(object):
    def __init__(self):
        self.storage = None
        self.last_updated = datetime.datetime.now() - datetime.timedelta(2)
        self.updating = False
    def is_updated(self):
        return self.storage and self.last_updated > (datetime.datetime.now() - datetime.timedelta(1))
    def is_updating(self):
        return self.updating
    def __call__(self):
        if not self.is_updated():
            if self.is_updating():
                while self.is_updating():
                    time.sleep(1)
                    print "waiting.. ", self.is_updating()
            else:
                self.update()
        return self.storage
    def update(self, wait_secs=0):
        if self.is_updating():
            print "quitting: update already in progress"
            return
        self.updating = True
        time.sleep(wait_secs)
        print "updating"
        try:
            self.storage = dict ( \
             (loc, list(usages)) for loc, usages in sortAndGrpby((ru for ru in (RUsageCache(ru) for ru in RUsage.select())), lambda ru: ru.resource.place.id) )
            self.last_updated = datetime.datetime.now()
        except Exception, err:
            applogger.error("reportutils: error updating cache %s" % err)
        finally:
            self.updating = False
        print "updated"
    def update_in_thread(self, wait_secs):
        thread.start_new(self.update, (wait_secs,))

get_all_usages = AllUsages()
get_all_usages.update_in_thread(3)

def get_usages_for_period(location, start, end):
    return (ru for ru in get_all_usages()[location] if end >= ru.start >= start)
        
def get_this_months_limits(someday=None):
    today = someday or datetime.date.today()
    end = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    start = datetime.datetime(end.year, end.month, 1)
    return start, end

def get_next_months_limits(someday=None):
    today = someday or datetime.date.today()
    start = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1]) + datetime.timedelta(1)
    end = datetime.datetime(start.year, start.month, calendar.monthrange(start.year, start.month)[1])

def get_last_months_limits(someday=None):
    today = someday or datetime.date.today()
    end = datetime.datetime(today.year, today.month, 1) - datetime.timedelta(1)
    start = datetime.datetime(end.year, end.month, 1)
    return start, end

def get_this_and_last_months_limits(someday=None):
    today = someday or datetime.date.today()
    end = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    lm_end = datetime.datetime(today.year, today.month, 1) - datetime.timedelta(1)
    start = datetime.datetime(lm_end.year, lm_end.month, 1)
    return start, end

def get_last_12months_limits(someday=None):
    today = someday or datetime.date.today()
    start = datetime.datetime(today.year - 1, today.month, 1)
    end = datetime.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    return start, end

def save_result(f):
    def wrap(self, *args, **kw):
        if f.func_name in self.results:
            return self.results[f.func_name]
        else:
            result = f(self, *args, **kw)
            self.results[f.func_name] = result
            return result
    return wrap

class LocationStats(object):
    """
    >>> import hubspace.reportutils as reportutils
    >>> lstats = reportutils.LocationStats(1, 'thismonth')
    >>> lstats.get_revenue_summary()
        (Decimal("11235.00"), Decimal("20.00"), Decimal("11255.00"), u'GBP')
    >>> lstats.get_revenue_stats()
        ([((2009, 11), Decimal("11235.00"), Decimal("20.00"))], u'GBP')
    >>> lstats.get_revenue_summary()
        (Decimal("11235.00"), Decimal("20.00"), Decimal("11255.00"), u'GBP')
    >>> lstats.get_revenue_stats()
        ([((2009, 11), Decimal("11235.00"), Decimal("20.00"))], u'GBP')
    """
    
    def __init__(self, loc_id, period=None, start=None, end=None):
        self.location = Location.get(loc_id)
        if start and end:
            self.start, self.end = start, end
        elif period:
            if period == 'thismonth':
                self.start, self.end = get_this_months_limits()
            elif period == 'thisandlastmonths':
                self.start, self.end = get_this_and_last_months_limits()
            elif period == 'lastmonth':
                self.start, self.end = get_last_months_limits()
            elif period == 'last12months':
                self.start, self.end = get_last_12months_limits()
        else:
            self.start, self.end = get_this_months_limits()
        self.results = dict()

    def get_churn_stats(self):
        """
        -> [((2009, 3), 13, 4), ((2009, 4), 2, 5), ...]
                        ^ members left         ^ members back
        """
        tariff_ids = (resource.id for resource in self.location.resources if resource.type == 'tariff')
        dateptr = get_last_months_limits(self.start)[0]
        tariff_usages = (ru for ru in self.get_usages_for_period(dateptr, self.end) if ru.resourceID in tariff_ids)
        prev_month = get_last_months_limits(dateptr)
        stats = []
        while dateptr <= self.end:
            current_month = get_this_months_limits(dateptr)
            members_then = set(ru.userID for ru in get_usages_for_period(self.location.id, *prev_month))
            members_now = set(ru.userID for ru in get_usages_for_period(self.location.id, *current_month))
            members_left = len(members_then.difference(members_now))
            members_back = len([m_id for m_id in members_now.difference(members_then) if User.get(m_id).created < prev_month[0]])
            stats.append(("%s %s" % (calendar.month_abbr[dateptr.month], dateptr.year), (members_left, members_back)))
            dateptr = current_month[-1] + datetime.timedelta(1)
            prev_month = current_month
        return stats

    def get_usage_by_tariff(self):
        """
        -> { rtype1: 
                { tariff1:
                        { resource1: usage, resource2: usage, ..},
                  tariff2: ..
                }
        } 
        """
        tariff_ids = tuple(resource.id for resource in self.location.resources if resource.type == 'tariff')
        relevant_usages = tuple(ru for ru in self.usages if ru.resourceID not in tariff_ids)
        relevant_resources = set(ru.resourceID for ru in relevant_usages)
        r_type_map = dict((res.name, res.type) for res in self.location.resources if res.id in relevant_resources)
        r_types =  set(r_type_map.values())
        type_resources_map = dict((r_type, tuple(x[0] for x in resources)) for r_type, resources in sortAndGrpby(r_type_map.items(), lambda item: item[1]))
        resname = lambda r_id: Resource.get(r_id).name
        #result = dict((r_type, dict((resname(t_id), dict((res, 0) for res in type_resources_map[r_type])) for t_id in tariff_ids)) for r_type in r_types)
        result = dict((r_type, dict((res, defaultdict(lambda: 0)) for res in type_resources_map[r_type])) for r_type in r_types)
        for ru in relevant_usages:
            quantity = isinstance(ru.duration_or_quantity, datetime.timedelta) and \
                ((ru.duration_or_quantity.days * 24 * 60 * 60) + ru.duration_or_quantity.seconds) or ru.duration_or_quantity
            result[ru.resource.type][ru.resource.name][ru.tariffID] += quantity
        return result

    def get_summary(self):
        return dict (
            total_members_active = User.selectBy(active=1).count(),
            loc_members_active = User.selectBy(active=1, homeplace=self.location).count(),
            loc_members_not_active = User.selectBy(active=0, homeplace=self.location).count(),
            new_members = User.select( \
                AND(User.q.active == 1, User.q.homeplaceID == self.location.id, User.q.created >= self.start, User.q.created <= self.end)).count(),
            revenue = sum(ru.effectivecost for ru in self.usages),
            currency = self.location.currency,
            )

    def get_members_by_tariff(self):
        tariff_usages = (ru for ru in self.get_usages_for_period(*get_this_months_limits()) if ru.resource.type == 'tariff')
        return ((name, len(tuple(usages))) for name, usages in sortAndGrpby(tariff_usages, lambda ru: ru.resource.name))

    def get_revenue_by_tariff(self):
        grouped = sortAndGrpby(self.usages, lambda x: x.tariffID)
        return ((Resource.get(t_id).name, float(sum(ru.effectivecost for ru in usages))) for t_id, usages in grouped)

    def get_revenue_stats(self):
        grouped = sortAndGrpby(self.usages, lambda x: "%s %s" % (calendar.month_abbr[x.start.month], x.start.year))
        return tuple((month, float(sum(ru.effectivecost for ru in usages))) for month, usages in grouped)

    @save_result
    def get_revenue_by_resource(self):
        grouped = sortAndGrpby(self.usages, lambda x: (x.resourceID))
        return tuple((Resource.get(r_id).name, float(sum(ru.effectivecost for ru in usages))) for (r_id, usages) in grouped)

    def get_revenue_by_resourcetype(self):
        by_resource = self.get_revenue_by_resource()
        result = dict((r.type, 0) for r in Resource.selectBy(place=self.location))
        for name, revenue in by_resource:
            r_type = Resource.selectBy(name=name)[0].type
            result[r_type] += revenue
        return result.items()

    def get_resource_utilization(self):
        raise NotImplemented

    def get_usages_for_period(self, start, end):
        rusages = get_all_usages()[self.location.id]
        return list(ru for ru in rusages if self.end >= ru.start >= self.start)

    def __getattr__(self, attrname):
        if attrname == "usages":
            usages = self.get_usages_for_period(self.start, self.end)
            setattr(self, attrname, usages)
            return usages

    
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
