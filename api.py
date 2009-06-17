import logging
import sha
import threading
from random import random
from datetime import timedelta, datetime
import time
import types

import cherrypy
import pkg_resources
from cherrypy.filters.basefilter import BaseFilter
import turbogears

log = logging.getLogger("turbogears.visit")

# Global VisitManager
_manager = None

# Global list of plugins for the Visit Tracking framework
_plugins = list()

# Accessor functions for getting and setting the current visit information.
def current():
    '''
    Retrieve the current visit record from the cherrypy request.
    '''
    return getattr(cherrypy.request, "tg_visit", None)

def set_current(visit):
    '''
    Set the current visit record on the cherrypy request being processed.
    '''
    cherrypy.request.tg_visit = visit

def _create_visit_manager(timeout):
    '''
    Create a VisitManager based on the plugin specified in the config file.
    '''
    plugin_name = turbogears.config.get("visit.manager", "sqlobject")
    plugins = pkg_resources.iter_entry_points("turbogears.visit.manager",
                                              plugin_name)

    log.debug("Loading visit manager from plugin: %s", plugin_name)

    for entrypoint in plugins:
        plugin = entrypoint.load()
        return plugin(timeout)

    raise RuntimeError("VisitManager plugin missing: %s" % plugin_name)

def monkey_before_main(self):
    '''
    this function is used to monkey patch the decoding filter from cherrypy
    '''
    conf = cherrypy.config.get

    if not conf('decoding_filter.on', False):
        return

    if getattr(cherrypy.request, "_decoding_attempted", False):
        return
    cherrypy.request._decoding_attempted = True

    enc = conf('decoding_filter.encoding', None)
    if not enc:
        ct = cherrypy.request.headers.elements("Content-Type")
        if ct:
            ct = ct[0]
            enc = ct.params.get("charset", None)
            if (not enc) and ct.value.lower().startswith("text/"):
                # http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.7.1
                # When no explicit charset parameter is provided by the
                # sender, media subtypes of the "text" type are defined
                # to have a default charset value of "ISO-8859-1" when
                # received via HTTP.
                enc = "ISO-8859-1"

        if not enc:
            enc = conf('decoding_filter.default_encoding', "utf-8")

    try:
        self.decode(enc)
    except UnicodeDecodeError:
        # IE and Firefox don't supply a charset when submitting form
        # params with a CT of application/x-www-form-urlencoded.
        # So after all our guessing, it could *still* be wrong.
        # Start over with ISO-8859-1, since that seems to be preferred.
        self.decode("ISO-8859-1")

# Interface for the TurboGears extension
def start_extension():
    # Bail out if the application hasn't enabled this extension
    if not turbogears.config.get("visit.on", False):
        return
    # Bail out if this extension is already running
    global _manager
    if _manager:
        return

    # Monkey patch CP Decoding filter
    from cherrypy.filters import decodingfilter
    decodingfilter.DecodingFilter.before_main = monkey_before_main

    log.info("Visit Tracking starting")
    # How long may the visit be idle before a new visit ID is assigned?
    # The default is 20 minutes.
    timeout = timedelta(minutes=turbogears.config.get("visit.timeout", 20))
    # Create the thread that manages updating the visits
    _manager = _create_visit_manager(timeout)

    filter = VisitFilter()
    # Temporary until tg-admin can call create_extension_model
    create_extension_model()
    # Install Filter into the root filter chain
    if not hasattr(cherrypy.root, "_cp_filters"):
        cherrypy.root._cp_filters = list()

    cherrypy.root._cp_filters.append(filter)

def shutdown_extension():
    # Bail out if this extension is not running
    global _manager
    if not _manager:
        return
    log.info("Visit Tracking shutting down")
    _manager.shutdown()
    _manager = None

def create_extension_model():
    # Create the data model of the VisitManager if one exists.
    if _manager:
        _manager.create_model()

def enable_visit_plugin(plugin):
    '''
    Register a visit tracking plugin. These plugins will be called for each
    request.
    '''
    _plugins.append(plugin)

class Visit(object):
    '''
    Basic container for visit related data.
    '''
    def __init__(self, key, is_new):
        self.key = key
        self.is_new = is_new

class VisitFilter(BaseFilter):
    '''
    A filter that automatically tracks visitors.
    '''

    def __init__(self):
        log.info("Visit filter initialised")
        get = turbogears.config.get

        # Get the name to use for the identity cookie.
        self.cookie_name = get("visit.cookie.name", "tg-visit")
        # TODO: The path should probably default to whatever
        # the root is masquerading as in the event of a
        # virtual path filter.
        self.cookie_path = get("visit.cookie.path", "/")
        # The secure bit should be set for HTTPS only sites
        self.cookie_secure = get("visit.cookie.secure", False)
        # By default, I don't specify the cookie domain.
        self.cookie_domain = get("visit.cookie.domain", None)
        self.cookie_max_age = int(get("visit.timeout", "20")) * 60
        assert self.cookie_domain != "localhost", \
               "localhost is not a valid value for visit.cookie.domain. Try None instead."

    def before_main(self):
        '''
        Inspect the submitted request to determine whether it already belongs to
        an existing visit.
        '''
        def encode_utf8(params):
            '''
            will recursively encode to utf-8 all values in a dictionnary
            what about when a dictionary is nested in a list?
            '''
            def encode_arg(value):
                if isinstance(value, dict):
                    for k,v in value.items():
                        value[k] = encode_arg(v)
                    return value
                elif isinstance(value, list):
                    return [encode_arg(vv) for vv in value]
                else:
                    return value.encode('utf-8')
            
            res = dict()
            for k, v in params.items():
                res[k] = encode_arg(v)
            return res

        if not turbogears.config.get("visit.on", True):
            set_current(None)
            return

        visit = current()
        cookies = cherrypy.request.simple_cookie

        if not visit:
            if self.cookie_name in cookies:
                # Process visit based on cookie
                visit_key = cookies[self.cookie_name].value
                visit = _manager.visit_for_key(visit_key)

            if not visit:
                visit_key = self._generate_key()
                visit = _manager.new_visit_with_key(visit_key)
                self.send_cookie(visit_key)

            set_current(visit)

        # Inform all the plugins that a request has been made for the current
        # visit. This gives plugins the opportunity to track click-path or
        # retrieve the visitor's identity.
        try:
            for plugin in _plugins:
                plugin.record_request(visit)

        except cherrypy.InternalRedirect, e:
            # Can't allow an InternalRedirect here because CherryPy is dumb,
            # instead change cherrypy.request.object_path to the url desired.
            cherrypy.request.object_path = e.path

        cherrypy.request.params = encode_utf8(cherrypy.request.params)

    def _generate_key(self):
        '''
        Returns a (pseudo)random hash based on seed
        '''
        # Adding remoteHost and remotePort doesn't make this any more secure,
        # but it makes people feel secure... It's not like I check to make
        # certain you're actually making requests from that host and port. So
        # it's basically more noise.
        key_string= '%s%s%s%s' % (random(), datetime.now(),
                                  cherrypy.request.remote_host,
                                  cherrypy.request.remote_port)
        return sha.new(key_string).hexdigest()

    def clear_cookie(self):
        '''
        Clear any existing visit ID cookie.
        '''
        cookies= cherrypy.response.simple_cookie

        # clear the cookie
        log.debug("Clearing visit ID cookie")
        cookies[self.cookie_name] = ''
        cookies[self.cookie_name]['path'] = self.cookie_path
        cookies[self.cookie_name]['expires'] = 0

    def send_cookie(self, visit_key):
        '''
        Send an visit ID cookie back to the browser.
        '''
        cookies = cherrypy.response.simple_cookie
        cookies[self.cookie_name] = visit_key
        cookies[self.cookie_name]['path'] = self.cookie_path
        # We'd like to use the "max-age" param as
        #   http://www.faqs.org/rfcs/rfc2109.html indicates but IE doesn't
        #   save it to disk and the session is lost if people close
        #   the browser
        #   So we have to use the old "expires" ... sigh ...
        #cookies[self.cookie_name]['max-age']= self.cookie_max_age
        gmt_expiration_time = time.gmtime(time.time() + self.cookie_max_age)
        cookies[self.cookie_name]['expires'] = time.strftime(
                "%a, %d-%b-%Y %H:%M:%S GMT", gmt_expiration_time)

        if self.cookie_secure:
            cookies[self.cookie_name]['secure'] = True

        if self.cookie_domain:
            cookies[self.cookie_name]['domain'] = self.cookie_domain

        log.debug("Sending visit ID cookie: %s",
                   cookies[self.cookie_name].output())


class BaseVisitManager(threading.Thread):
    def __init__(self, timeout):
        super(BaseVisitManager,self).__init__(name="VisitManager")
        self.timeout = timeout
        self.queue = dict()
        self.lock = threading.Lock()
        self._shutdown = threading.Event()
        self.interval = 30
        self.setDaemon(True)
        self.start()

    def create_model(self):
        pass

    def new_visit_with_key(self, visit_key):
        '''
        Return a new Visit object with the given key.
        '''
        raise NotImplementedError

    def visit_for_key(self, visit_key):
        '''
        Return the visit for this key or None if the visit doesn't exist or has
        expired.
        '''
        raise NotImplementedError

    def update_queued_visits(self, queue):
        '''
        Extend the expiration of the queued visits.
        '''
        raise NotImplementedError

    def update_visit(self, visit_key, expiry):
        try:
            self.lock.acquire()
            self.queue[visit_key] = expiry
        finally:
            self.lock.release()

    def shutdown(self, timeout=None):
        self._shutdown.set()
        self.join(timeout)
        if self.isAlive():
            log.error("Visit Manager thread failed to shutdown.")

    def run(self):
        while not self._shutdown.isSet():
            self.lock.acquire()
            queue = None
            try:
                # make a copy of the queue and empty the original
                if self.queue:
                    queue = self.queue.copy()
                    self.queue.clear()

            finally:
                self.lock.release()

            if queue is not None:
                self.update_queued_visits(queue)

            self._shutdown.wait(self.interval)
