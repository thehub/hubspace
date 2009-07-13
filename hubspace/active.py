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
        return (loc.url + '/public/', link_content)
    else:
        map_entry = PublicPlace.select(AND(PublicPlace.q.name == loc.name.lower()))
        if map_entry.count():
            return ('http://the-hub.net/places/' + loc.name.lower(), link_content)
        

def location_links():
    locations = Location.select(AND(Location.q.in_region == None), orderBy='name')
    loc_tuples = []
    for location in locations:
        link = write_link_tuple(location)
        if link:
            loc_tuples.append(link)
        if location.is_region:
            for hub in location.has_hubs:
                link = write_link_tuple(hub, sub=True)
                if link:
                    loc_tuples.append(link)
    return loc_tuples
