from model import User, RUsage, Resource, Location
from sqlobject import AND, IN
from sqlobject.events import listen, RowUpdateSignal, RowCreatedSignal, RowDestroySignal
from datetime import datetime, date, time, timedelta

import logging
import datetime

PAST_EVENTS_MAX = 30
FUTURE_EVENTS_MAX = 30

applogger = logging.getLogger("hubspace")

def on_exception(dont_fail=True, log=True):
    def deco(f):
        def wrap(*args, **kw):
            try:
                ret = f(*args, **kw)
                return ret
            except Exception, err:
                if log: print err
                if not dont_fail: raise
        return wrap
    return deco

class ObjectCache(object):
    def __init__(self, instance):
        for attr in self.attrs_to_remember:
            setattr(self, attr, getattr(instance, attr))
        self.inithook(instance)
    def inithook(self, instance):
        pass
    def __repr__(self):
        return "<Event: %s>" % self.id
    def update(self, attrs_dict):
        for k, v in attrs_dict.items():
            if k in self.attrs_to_remember:
                setattr(self, k, v)

class ObjectCacheContainer(list):
    objectcache_factory = ObjectCache
    def __init__(self, location, *args, **kw):
        self.location = location
        list.__init__(self, *args, **kw)
    def populate(self):
        raise NotImplemented
    def add(self, instance):
        cache_obj = self.objectcache_factory(instance)
        self.insert(0, cache_obj)
        self.cleanup()
    def has_object(self, instance_id):
        for instance in self:
            if instance.id == instance_id: return True
        return False
    def remove(self, instance_id):
        for instance in self:
            if instance.id == instance_id:
                list.remove(self, instance)
                return True
    def get(self, instance_id):
        for instance in self:
            if instance.id == instance_id:
                return instance
    def cleanup(self):
        raise NotImplemented

class EventCache (ObjectCache):
    attrs_to_remember = ('id', 'start', 'end_time', 'resource_name', 'meeting_name', 'meeting_description', 'date_booked', 'url')
    def inithook(self, rusage):
        self.resourceID = rusage.resource.id
        self.locationID = rusage.resource.place.id
        self.location_name = rusage.resource.place.name
        self.user_display_name = rusage.user.display_name
    def is_future(self):
        return self.start > datetime.datetime.now()
    def __cmp__(self, other):
        return cmp(self.start, other.start)
    def __repr__(self):
        return "<Event: %s on %s at %s>" % (self.id, self.start, self.location_name)

class EventCacheContainer(ObjectCacheContainer):
    objectcache_factory = EventCache
    def _post_make_cache_obj(self, cache_obj, instance):
        cache_obj.resourceID = instance.resource.id
        cache_obj.locationID = instance.resource.place.id
        cache_obj.location_name = instance.resource.place.name
    def populate(self):
        now = datetime.datetime.now()
        till_dt = datetime.datetime(now.year, now.month, now.day) - datetime.timedelta(90)
        if self.location == 'global':
            events_select = RUsage.select \
                (AND(RUsage.q.resourceID==Resource.q.id, RUsage.q.public_field == 1, RUsage.q.start >= till_dt)).orderBy('start').reversed()
        else:
            events_select = RUsage.select \
                (AND(RUsage.q.resourceID==Resource.q.id, Resource.q.placeID==self.location, RUsage.q.public_field == 1, RUsage.q.start >= till_dt)).orderBy('start').reversed()
        no_past_events = 0
        for event in events_select:
            cache_obj = self.objectcache_factory(event)
            self.append(cache_obj)
            if not cache_obj.is_future():
                no_past_events += 1
                if no_past_events == PAST_EVENTS_MAX:
                    break
    @on_exception()
    def cleanup(self):
        past_events = self.get_past_events()
        if len(past_events) > PAST_EVENTS_MAX:
            for event in past_events[PAST_EVENTS_MAX:]:
                self.remove(event)
    def get_past_events(self, n=None):
        return sorted([event for event in self if not event.is_future()], reverse=True)[:n]
    def get_future_events(self, n=None):
        return sorted([event for event in self if event.is_future()])[:n]

class ProfileCache(ObjectCache):
    attrs_to_remember = ('id', 'user_name', 'display_name', 'has_avatar', 'description', 'modified', 'homeplaceID', 'active', 'public_field', 'created', 'organisation', 'url')
    def __cmp__(self, other):
        return cmp(self.modified, other.modified)
    def __repr__(self):
        return "<Profile: %s @ location %s>" % (self.user_name, self.homeplaceID)

class ProfileCacheContainer(ObjectCacheContainer):
    objectcache_factory = ProfileCache
    def populate(self):
        if not self.location == 'global':
            location = Location.get(self.location)
            if location.is_region:
                hubs = location.has_hubs
                profile_select = User.select(AND(IN(User.q.homeplaceID, hubs),
                    User.q.public_field==1,
                    User.q.active==1,
                    User.q.description != u"",
                    User.q.modified > datetime.datetime.now() - datetime.timedelta(days=365))).orderBy('modified').reversed()[:30]
            else:
                profile_select = User.select(AND(User.q.homeplaceID==location,
                    User.q.public_field==1,
                    User.q.active==1,
                    User.q.description != u"",
                    User.q.modified > datetime.datetime.now() - datetime.timedelta(days=365))).orderBy('modified').reversed()[:30]
        else:
            profile_select = User.select(AND(User.q.public_field==1,
                    User.q.active==1,
                    User.q.description != u"",
                    User.q.modified > datetime.datetime.now() - datetime.timedelta(days=365))).orderBy('modified').reversed()[:30]
        for profile in profile_select:
            cache_obj = self.objectcache_factory(profile)
            self.append(cache_obj)
    @on_exception()
    def cleanup(self):
        self.pop()

class LocationCache(dict):
    def __init__(self, location, *args, **kw):
        self.location = location
        dict.__init__(self, *args, **kw)
    def __missing__(self, key):
        object_cache_factory = cache_factories[key]
        object_cache = object_cache_factory(self.location)
        self[key] = object_cache
        object_cache.populate()
        return object_cache

class Cache(dict):
    def __missing__(self, key):
        location_cache = LocationCache(key)
        self[key] = location_cache
        return location_cache
    
def on_add_rusage(kwargs, post_funcs):
    rusage = kwargs['class'].get(kwargs['id'])
    if rusage.public_field:
        location = rusage.resource.place.id
        cached_updates[location]['events'].add(rusage)
        applogger.info("feeds.on_add_rusage: added %(id)s" % kwargs)

def on_del_rusage(rusage, post_funcs):
    applogger.info("feeds.on_del_rusage: removing %s" % rusage.id)
    location = rusage.resource.placeID
    if cached_updates[location]['events'].has_object(rusage.id):
        cached_updates[location]['events'].remove(rusage.id)

def on_add_user(kwargs, post_funcs):
    user = kwargs['class'].get(kwargs['id'])
    if user.public_field:
        location = user.homeplaceID
        cached_updates[location]['profiles'].add(user)

def on_updt_rusage(instance, kwargs):
    applogger.info("feeds.on_updt_rusage: updating %s" % instance.id)
    location = instance.resource.placeID
    instance_cache = cached_updates[location]['events'].get(instance.id)
    if instance_cache:
        instance_cache.update(kwargs)
    else:
        if kwargs.get('public_field', False):
            cached_updates[location]['events'].add(rusage)
            applogger.info("feeds.on_add_rusage: added %(id)s" % kwargs)

def on_updt_user(instance, kwargs):
    applogger.info("feeds.on_updt_user: updating %s" % instance.id)
    location = instance.homeplaceID
    instance_cache = cached_updates[location]['profiles'].get(instance.id)
    if instance_cache:
        instance_cache.update(kwargs)
    cached_updates[location]['profiles'].sort()

cache_factories = dict (events=EventCacheContainer, profiles=ProfileCacheContainer)
cached_updates = Cache()

listen(on_add_rusage, RUsage, RowCreatedSignal)
listen(on_updt_rusage, RUsage, RowUpdateSignal)
listen(on_del_rusage, RUsage, RowDestroySignal)
listen(on_add_user, User, RowCreatedSignal)
listen(on_updt_user, User, RowUpdateSignal)


def get_updates_data(location):
    local_updates = cached_updates[location.id]
    updates = {}
    updates['local_profiles'] = local_updates['profiles']
    updates['local_events'] = local_updates['events'].get_future_events()
    updates['global_profiles'] = cached_updates['global']['profiles']
    updates['global_events'] = cached_updates['global']['events'].get_future_events()
    return updates

def get_local_future_events(location, no_of_events=None, *args, **kw):
    return dict(future_events = cached_updates[location]['events'].get_future_events(no_of_events))

def get_local_past_events(location, no_of_events=None, *args, **kw):
    return dict(past_events = cached_updates[location]['events'].get_past_events(no_of_events))

def get_local_profiles(location, only_with_images=False, no_of_images=None, *args, **kw):
    profiles = cached_updates[location]['profiles']
    if only_with_images:
        profiles = [profile for profile in profiles if profile.has_avatar][:no_of_images]
    return {'profiles': profiles}

