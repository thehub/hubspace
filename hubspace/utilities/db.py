import logging
from turbogears.database import PackageHub, commit_all, end_all
from sqlobject.util.threadinglocal import local as threading_local

hub = PackageHub("turbogears.visit")
applogger = logging.getLogger("hubspace")

class schedSafe(object):
    """
    a. may not be safe, make sure you test the transactions are executed correctly.
    b. strictly for non long running tasks
    """
    def __init__(self, f):
        self.f = f
    def __call__(self, *args, **kw):
        applogger.debug("schedSafe: begin")
        hub.threadingLocal = threading_local()
        hub.begin()
        try:
            ret = self.f(*args, **kw)
            applogger.debug("schedSafe: %s returned %s" % (self.f.__name__, ret))
        finally:
            commit_all()
            end_all()
        applogger.debug("schedSafe: done")


