import datetime, itertools, time, calendar, os, time, thread, logging
from glob import glob
import compat
from hubspace.model import Resource, RUsage, Location, User, resource_types
from sqlobject.sqlbuilder import IN, Select, AND
import cairoplot.cairoplot as CairoPlot
from turbogears import identity
import tariff as tarifflib

applogger = logging.getLogger("hubspace")

def sortAndGrpby(iterable, keyfn, reverse=False):
    l = sorted(iterable, key=keyfn)
    return itertools.groupby(l, keyfn)

report_img_dir = "tmp"

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

def plot_hbars(data, y_labels, legend):
    print data, y_labels, legend
    path = make_report_image_path()
    stack = len(data[0]) > 1
    CairoPlot.horizontal_bar_plot (path, data, 450, 400, display_values = True, grid = True, rounded_corners = True, stack = stack,\
                              y_labels = y_labels, series_labels = legend)
    return path

def plot_dot_line(data, h_labels):
    """
    teste_data_2 = {"john" : [10, 10, 10, 10, 30], "mary" : [0, 0, 3, 5, 15], "philip" : [13, 33, 11, 25, 2]}
    teste_h_legend = ["jan/2008", "feb/2008", "mar/2008", "apr/2008", "may/2008"]
    """
    path = make_report_image_path()
    CairoPlot.dot_line_plot(path, data, 400, 350, x_labels= h_labels, axis = True, grid = True, dots= True, series_legend=True)
    return path

def plot_vbars(data, x_labels, y_labels=None, legend=None):
    path = make_report_image_path()
    CairoPlot.vertical_bar_plot (path, data, 400, 350, border = 20, display_values = True, grid = True, rounded_corners = True, \
        stack = False, x_labels = x_labels, y_labels=y_labels, series_labels=legend)
    return path

def plot_pie_chart(data):
    """
    data: {"john" : 123, "mary" : 489, "philip" : 600 , "suzy" : 235}
    """
    #if len(data) > 25:
    #    total = sum((int(x) for x in data.values()))
    data2 = dict(others=0)
    total = sum(data.values())
    for name, v in data.items():
        if ((v*100)/total) < 3: data2['others'] += v
        else: data2[name] = v
    if not data2['others']: del data2['others']
    path = make_report_image_path()
    CairoPlot.pie_plot(path, data2, 450, 350, gradient = True, shadow = False)
    return path

def x_plot_pie_chart(data):
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie3d, Pie, LegendedPie
    from reportlab.lib import colors
    
    d = Drawing(800, 800)
    
    #pc = Pie3d()
    pc = Pie()
    pc = LegendedPie()
    pc.height = 400
    pc.width = 400
    pc.x = 80 
    pc.y = 80
    pc.drawLegend = True

    pc.data = []
    pc.labels = []
    for k,v in data.items():
        pc.data.append(v)
        pc.labels.append(k)
    pc.legend_names = pc.labels
    pc.legend_data = pc.data

    slice_2_pop = pc.data.index(max(data.values()))
    
    pc.slices.strokeWidth=1#0.5 
    pc.slices[slice_2_pop].popout = 20 
    pc.slices[3].strokeWidth = 2 
    pc.slices[3].strokeDashArray = [2,2]
    pc.slices[3].labelRadius = 1.75 
    pc.slices[3].fontColor = colors.red
    
    d.add(pc)
    
    filepath, ext = make_report_image_path().split('.')
    d.save(fnRoot="../tmp/" + filename, formats=['png',])

    return timestmp


class RUsageCache(object):
    def __init__(self, ru):
        attrs_not_2store = ('cost', 'customcost', 'resource_description', 'new_resource_description', 'usagesuggestedbyID', 'meeting_name', 'meeting_description', 'number_of_people', 'notes', 'public_field')
        attrs2store = [attr.name for attr in RUsage.sqlmeta.columnList if attr not in attrs_not_2store] + ['id', 'effectivecost', 'duration_or_quantity']
        for attr in attrs2store:
            setattr(self, attr, getattr(ru, attr))
    def _get_resource(self):
        return Resource.get(self.resourceID)
    def _get_user(self):
        return User.get(self.userID)
    def _get_invoice(self):
        return User.get(self.userID)
    invoice = property(_get_invoice)
    user = property(_get_user)
    resource = property(_get_resource)

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
        if period:
            if period == 'thismonth':
                self.start, self.end = get_this_months_limits()
            elif period == 'thisandlastmonths':
                self.start, self.end = get_this_and_last_months_limits()
            elif period == 'lastmonth':
                self.start, self.end = get_last_months_limits()
            elif period == 'last12months':
                self.start, self.end = get_last_12months_limits()
        else:
            if not start:
                self.start, self.end = get_this_months_limits()
        self.results = dict()

    def get_churn_stats(self):
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
            stats.append(((dateptr.year, dateptr.month), members_left, members_back))
            dateptr = current_month[-1] + datetime.timedelta(1)
            prev_month = current_month
        return stats

    def get_usage_by_tariff(self):
        tariff_ids = tuple(resource.id for resource in self.location.resources if resource.type == 'tariff')
        relevant_usages = tuple(ru for ru in self.usages if ru.resourceID not in tariff_ids)
        relevant_resources = set(ru.resourceID for ru in relevant_usages)
        r_type_map = dict((res.id, res.type) for res in self.location.resources if res.id in relevant_resources)
        r_types =  set(r_type_map.values())
        type_resources_map = dict((r_type, tuple(x[0] for x in resources)) for r_type, resources in sortAndGrpby(r_type_map.items(), lambda item: item[1]))
        # {tariff_id: {type: {resource_id: usage_quantity, ..}
        result = dict((tariff_id, dict((r_type, dict((res,0) for res in type_resources_map[r_type])) for r_type in r_types)) for tariff_id in tariff_ids)
        for ru in relevant_usages:
            quantity = isinstance(ru.duration_or_quantity, datetime.timedelta) and \
                ((ru.duration_or_quantity.days * 24 * 60 * 60) + ru.duration_or_quantity.seconds) or ru.quantity
            res_type = r_type_map[ru.resourceID]
            result[ru.tariffID][res_type][ru.resourceID] += quantity
        return result

    def get_member_summary(self):
        return dict (
            total_members_active = User.selectBy(active=1).count(),
            loc_members_active = User.selectBy(active=1, homeplace=self.location).count(),
            loc_members_not_active = User.selectBy(active=0, homeplace=self.location).count(),
            new_members = User.select( \
                AND(User.q.active == 1, User.q.homeplaceID == self.location.id, User.q.created >= self.start, User.q.created <= self.end)).count(),
            )

    def get_revenue_summary(self):
        grouped = sortAndGrpby(self.usages, lambda x: bool(x.invoice))
        invoiced = sum((ru.effectivecost for ru in grouped.next()[1]))
        try:
            uninvoiced = sum((ru.effectivecost for ru in grouped.next()[1]))
        except StopIteration:
            uninvoiced = 0
        return invoiced, uninvoiced, invoiced + uninvoiced, self.location.currency

    def get_members_by_tariff(self):
        tariff_usages = (ru for ru in self.get_usages_for_period(*get_this_months_limits()) if ru.resource.type == 'tariff')
        return sortAndGrpby(tariff_usages, lambda ru: ru.resourceID)

    def get_revenue_by_tariff(self):
        grouped = sortAndGrpby(self.usages, lambda x: x.tariffID)
        return dict((t_id, float(sum(ru.effectivecost for ru in usages))) for t_id, usages in grouped)

    def get_revenue_stats(self):
        grouped = sortAndGrpby(self.usages, lambda x: (x.start.year, x.start.month))
        stats = list()
        for month, usages in grouped:
            group = sortAndGrpby(usages, lambda x: bool(x.invoice))
            try:
                invoiced = float(sum((ru.customcost or ru.cost for ru in group.next()[1])))
            except StopIteration:
                invoiced = 0
            try:
                uninvoiced = float(sum((ru.customcost or ru.cost for ru in group.next()[1])))
            except StopIteration:
                uninvoiced = 0
            stats.append((month, invoiced, uninvoiced))
        return stats, self.location.currency

    @save_result
    def get_revenue_by_resource(self):
        grouped = sortAndGrpby(self.usages, lambda x: (x.resourceID))
        return dict(((r_id, sum((ru.effectivecost for ru in usages))) for (r_id, usages) in grouped))

    def get_revenue_by_resourcetype(self):
        by_resource = self.get_revenue_by_resource()
        result = dict((Resource.get(r_id).type, 0) for r_id in by_resource)
        for r_id, revenue in by_resource.items():
            result[Resource.get(r_id).type] += float(revenue)
        return result

    def get_resource_utilization(self):
        raise NotImplemented

    def get_usages_for_period(self, start, end):
        rusages = get_all_usages()[self.location.id]
        usages = list(ru for ru in rusages if self.end >= ru.start >= self.start)
        return usages

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
