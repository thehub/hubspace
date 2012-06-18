# -*- coding: utf-8 -*-

from hubspace.model import Location, PublicPlace
from sqlobject import AND

#def navigation_text(location):
#    if location.name == location.city:
#        return location.name
#    else:
#        return location.city + ' - ' + location.name

def nav_sort(a, b):
    if a[1] > b[1]:
        return 1
    return -1


def write_link_tuple(loc, sub=False):
    if not sub:
        link_content = loc.name
    else:
        link_content = '<span class="sub_link">%s</span>' %(loc.name)
    if loc.microsite_active:
        if loc.id == 88:
            return ('http://www.hubwestminster.net/', link_content)
        return (loc.url + '/public/', link_content)
    else:
        if loc.id == 22: # #236
            return ('http://www.the-hub.co.il/home-en', loc.name)
        elif loc.id == 60:
            return ('http://www.hubzurich.org/', 'Zürich')
        map_entry = PublicPlace.select(AND(PublicPlace.q.name == loc.name.lower()))
        if map_entry.count():
            return ('http://the-hub.net/places/' + loc.name.lower(), link_content)
        
def name_sort(a, b):
    if a.name < b.name:
        return 1
    return -1

def location_links():
    locations = Location.select(AND(Location.q.in_region == None, Location.q.hidden == False), orderBy='name')
    loc_tuples = []
    for location in locations:
        if location.id in (2, 18, 32, 7, 90): continue # Website 226, 263, 271
        link = write_link_tuple(location)
        if link:
            loc_tuples.append(link)
        if location.is_region:
            hubs = location.has_hubs
            hubs.sort(name_sort)
            for hub in hubs:
                link = write_link_tuple(hub, sub=True)
                if link:
                    loc_tuples.append(link)
    return loc_tuples
