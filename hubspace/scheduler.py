import turbogears.scheduler
from turbogears.scheduler import method
import threading
from datetime import time, datetime, date
from time import mktime
_scheduler_instance = None

def _get_scheduler():
    global _scheduler_instance
    si = _scheduler_instance
    if not si:
        si = HubspaceScheduler()
        _scheduler_instance = si
    return si

def _start_scheduler():
    si = _get_scheduler()
    si.start()

def add_interval_task(action, interval, args=None, kw=None,
        initialdelay=0, processmethod=method.threaded, taskname=None):
    si = _get_scheduler()
    return si.add_interval_task(action=action, interval=interval, args=args,
            kw=kw, initialdelay=initialdelay,
            processmethod=processmethod, taskname=taskname)

def add_weekday_task(action, weekdays, timeonday, args=None, kw=None,
        processmethod=method.threaded, taskname=None):
    si = _get_scheduler()
    return si.add_daytime_task(action=action, taskname=taskname,
            weekdays=weekdays, monthdays=None, timeonday=timeonday,
            processmethod=processmethod, args=args, kw=kw)


def add_monthday_task(action, monthdays, timeonday,
        args=None, kw=None,
        processmethod=method.threaded, taskname=None):
    si = _get_scheduler()
    return si.add_daytime_task(action=action, taskname=taskname,
            weekdays=None, monthdays=monthdays, timeonday=timeonday,
            processmethod=processmethod, args=args, kw=kw)

def add_oneoff_task(action, ondate, timeonday, args=None, kw=None, processmethod=method.threaded, taskname=None):
    si = _get_scheduler()
    if not kw:
        kw = {}
    kw['oneoff'] = ondate
    return si.add_daytime_task(action=action, taskname=taskname,
            weekdays=None, monthdays=None, timeonday=timeonday,
            processmethod=processmethod, args=args, kw=kw)


def cancel(task):
    si = _get_scheduler()
    si.cancel(task)



class HubspaceScheduler(turbogears.scheduler.ThreadedScheduler):
    def add_daytime_task(self, action, taskname, weekdays, monthdays, timeonday, processmethod, args, kw):
        """Add a new Day Task (Weekday or Monthday) to the schedule."""
        if weekdays and monthdays:
            raise ValueError("you can only specify weekdays or monthdays, not both")
        if not args:
            args=[]
        if not kw:
            kw={}

        if weekdays:
            # Select the correct WeekdayTask class. Not all types may be available!
            if processmethod==method.sequential:
                TaskClass = turbogears.scheduler.WeekdayTask
            elif processmethod==method.threaded:
                TaskClass = turbogears.scheduler.ThreadedWeekdayTask
            elif processmethod==method.forked:
                TaskClass = turbogears.scheduler.ForkedWeekdayTask
            else:
                raise ValueError("invalid processmethod")
            task=TaskClass(taskname, weekdays, timeonday, action, args, kw)
        if monthdays:
            # Select the correct MonthdayTask class. Not all types may be available!
            if processmethod==method.sequential:
                TaskClass = turbogears.scheduler.MonthdayTask
            elif processmethod==method.threaded:
                TaskClass = turbogears.scheduler.ThreadedMonthdayTask
            elif processmethod==method.forked:
                TaskClass = turbogears.scheduler.ForkedMonthdayTask
            else:
                raise ValueError("invalid processmethod")
            task=TaskClass(taskname, monthdays, timeonday, action, args, kw)
        if 'oneoff' in kw:
            if processmethod==method.threaded: 
                TaskClass = ThreadedOneOffTask
                ondate = kw['oneoff']
                del kw['oneoff']
                task=TaskClass(taskname, ondate, timeonday, action, args, kw)
            else:
                raise ValueError("invalid processmethod")
        firsttime = task.get_schedule_time(True)
        self.schedule_task_abs(task, firsttime)
        return task


class OneOffTask(turbogears.scheduler.Task):
    def __init__(self, name, ondate, timeonday, action, args=None, kw=None):
        if type(timeonday) not in (list,tuple) or len(timeonday) != 2:
            raise TypeError("timeonday must be a 2-tuple (hour,minute)")
        if type(ondate) != date:
            raise TypeError("date must be a date object")
        turbogears.scheduler.Task.__init__(self, name, action, args, kw)
        self.ondatetime = datetime.combine(ondate, time(*timeonday))
        

    def execute(self):
        # This is called once, at the correct datetime. We only need to
        # it should not be rescheduled.
        self.action(*self.args, **self.kw)

    def reschedule(self, scheduler):
        raise ValueError("should not be rescheduled...its a one off task")

    def get_schedule_time(self, today):
        """Calculate the time value at which this task is to be scheduled."""
        now = self.ondatetime.timetuple()
        return mktime(now)
    

class ThreadedOneOffTask(turbogears.scheduler.ThreadedTaskMixin, OneOffTask):
    """OneOffTask that executes in its own thread
    """
    def __call__(self, schedulerref):
        threading.Thread(target=self.threadedcall).start()
