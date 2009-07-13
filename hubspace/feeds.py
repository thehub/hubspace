from model import User, RUsage, Resource, Location
from sqlobject import AND, IN
from datetime import datetime, date, time, timedelta

cached_updates = {'profiles':{}, 'events':{}, 'past_events':{}}

page_needs_regenerating = {}
   
def get_updates_data(location):#updates=cached_updates):
    updates = {}
    if location.id not in cached_updates['profiles']:
        if location.is_region:
            hubs = location.has_hubs
            cached_updates['profiles'][location.id] = User.select(AND(IN(User.q.homeplaceID, hubs),
                                                                      User.q.public_field==1,
                                                                      User.q.description != u"",
                                                                      User.q.modified > datetime.now() - timedelta(days=365))).orderBy('modified').reversed()[:30]
        else:
            cached_updates['profiles'][location.id] = User.select(AND(User.q.homeplaceID==location.id,
                                                                      User.q.public_field==1,
                                                                      User.q.description != u"",
                                                                      User.q.modified > datetime.now() - timedelta(days=365))).orderBy('modified').reversed()[:30]
        
    if 'global' not in cached_updates['profiles']:
        cached_updates['profiles']['global'] = User.select(AND(User.q.public_field==1,
                                                               User.q.description != u"",
                                                               User.q.modified > datetime.now() - timedelta(days=365))).orderBy('modified').reversed()[:30]
    if location.id not in cached_updates['events']:
        if location.is_region:
            hubs = location.has_hubs
            cached_updates['events'][location.id] = RUsage.select(AND(RUsage.q.resourceID==Resource.q.id,
                                                                      IN(Resource.q.placeID, hubs),
                                                                      RUsage.q.start >= datetime.combine(date.today(), time(0, 0)),
                                                                      RUsage.q.public_field==1)).orderBy('start')[:10]
        else:
            cached_updates['events'][location.id] = RUsage.select(AND(RUsage.q.resourceID==Resource.q.id,
                                                                      Resource.q.placeID==location.id,
                                                                      RUsage.q.start >= datetime.combine(date.today(), time(0, 0)),
                                                                      RUsage.q.public_field==1)).orderBy('start')[:10]

    if location.id not in cached_updates['past_events']:
        if location.is_region:
            hubs = location.has_hubs
            cached_updates['past_events'][location.id] = RUsage.select(AND(RUsage.q.resourceID==Resource.q.id,
                                                                           IN(Resource.q.placeID, hubs),
                                                                           RUsage.q.start < datetime.combine(date.today(), time(0, 0)),
                                                                           RUsage.q.public_field==1)).orderBy('start').reversed()[:10]
        else:
            cached_updates['past_events'][location.id] = RUsage.select(AND(RUsage.q.resourceID==Resource.q.id,
                                                                       Resource.q.placeID==location.id,
                                                                       RUsage.q.start < datetime.combine(date.today(), time(0, 0)),
                                                                       RUsage.q.public_field==1)).orderBy('start').reversed()[:10]

    if 'global' not in cached_updates['events']:
        cached_updates['events']['global'] = RUsage.select(AND(RUsage.q.public_field==1, RUsage.q.start >= datetime.combine(date.today(), time(0, 0)))).orderBy('start')[:10]

    updates['local_profiles'] = cached_updates['profiles'][location.id]
    updates['local_events'] = cached_updates['events'][location.id]
    updates['local_future_events'] = updates['local_events']
    updates['local_past_events'] = cached_updates['past_events'][location.id]
    updates['global_profiles'] = cached_updates['profiles']['global']
    updates['global_events'] = cached_updates['events']['global']
    return updates

def clear_cache(section, location):
    if 'global' in cached_updates[section]:
        del cached_updates[section]['global']
    if location.id in cached_updates[section]:
        del cached_updates[section][location.id]
    page_needs_regenerating.setdefault(location.id, {'members.html': False, 'events.html': False})
    if section == 'profiles':
	page_needs_regenerating[location.id]['members.html'] = True
    if section == 'events':
	page_needs_regenerating[location.id]['events.html'] = True

def get_local_profiles(*args, **kwargs):
    location = Location.get(kwargs['location'])
    profiles = get_updates_data(location)['local_profiles']
    if kwargs.get('only_with_images', False) == True:
        profiles = [profile for profile in profiles if profile.image]
    if kwargs.get('no_of_images', None):
        profiles = profiles[:kwargs['no_of_images']]
    return {'profiles': profiles}

def get_local_future_events(*args, **kwargs):
    location = Location.get(kwargs['location'])
    events = get_updates_data(location)['local_future_events']
    return {'future_events':events[:kwargs['no_of_events']]}

def get_local_past_events(*args, **kwargs):
    location = Location.get(kwargs['location'])
    events = get_updates_data(location)['local_past_events']
    return {'past_events':events[:kwargs['no_of_events']]}
