from hubspace.model import Location, PublicPlace
from sqlobject import AND

def navigation_text(location):
    if location.name == location.city:
        return location.name
    else:
        return location.city + ' - ' + location.name

def nav_sort(a, b):
    if a[1] > b[1]:
        return 1
    return -1

def location_links():
    locations = Location.select()
    loc_tuples = []
    for location in locations:
        if location.microsite_active:
            loc_tuples.append((location.url + '/public/', navigation_text(location)))
        else:
            map_entry = PublicPlace.select(AND(PublicPlace.q.name == location.name.lower()))
            if map_entry.count():
                loc_tuples.append(('http://the-hub.net/places/' + location.name.lower(), navigation_text(location)))
    loc_tuples.sort(nav_sort)
    return loc_tuples
