from turbogears import identity
from datetime import datetime, timedelta
from hubspace.model import RUsage, Resourcegroup, ResourceQueue
from sqlobject import AND, IN
from hubspace.utilities.dicts import AttrDict

def selected_room(room, room_selected):
    if int(room)==int(room_selected):
        return ' room_selected'
    return ''

def default_booking_params(location, resgroup=None):
    resgroup_order = location.resourcegroup_order
    if not resgroup_order:
        resgroup_order = []
    if not resgroup:
        try:
            resgroup = Resourcegroup.get(resgroup_order[0]) 
        except:
            #the first one is the ungrouped resource
            if len(resgroup_order)>1:
                resgroup = Resourcegroup.get(resgroup_order[1])
            else:
                resgroup = None
                return ([], None, None)
    res_order = resgroup.resources_order
    room_selected = 0
    rooms_displayed = []
    if res_order:
        room_selected = res_order[0]
        rooms_displayed = res_order
    return rooms_displayed, room_selected, resgroup

def booking_offset_plus_height(rusage, open):
    return booking_height(rusage) + booking_offset(rusage, open)

def get_width(no_rooms):
    width = 611.0/no_rooms
    return min(int(width), 203)


def mybooking(rusage):
    if rusage.user==identity.current.user:
        return " mybooking"
    return ""

def mewatching(booking, userid=None):
    if not userid:
        userid = identity.current.user.id
    if ResourceQueue.select(AND(ResourceQueue.q.rusageID == booking, 
                                ResourceQueue.q.foruserID == userid)).count():
        return " mewatching"
    return ""

def booking_height(rusage):
    return ((rusage.end_time-rusage.start).seconds/60.0/60.0*36)-6

def booking_offset(rusage, open):
    return ((rusage.start - datetime.combine(rusage.start.date(), open)).seconds/60.0/60.0*36)

def day_event_style(open, resources, res, rusage, no_rooms, only_my_bookings=0):
    attrs = day_coordinates(open, rusage, no_rooms)
    my_booking = mybooking(rusage)
    watching = mewatching(rusage)
    if only_my_bookings and not my_booking:
        attrs["class"] = "other_booking_off"
    elif watching:
        attrs['class'] = watching
    elif not my_booking:
        attrs["class"] = "other_booking"
    else:
        attrs["class"] = my_booking
    room_no = resources.index(res)+1
    if not rusage.confirmed:
        attrs["class"]+=" event room_t"
    else:
        attrs["class"]+=" event room"+ str(room_no)
    return attrs

def day_unavailable_style(open, resources, res, other_rusage, no_rooms, only_my_bookings):
    attrs = day_coordinates(open, other_rusage, no_rooms)
    if only_my_bookings:
        attrs["class"] = "other_booking_off"
    else:
        attrs["class"] = "other_booking"
    room_no = resources.index(res)+1
    attrs["class"]+=" unavailable room"+ str(room_no)
    return attrs
    

def day_coordinates(open, rusage, no_rooms):
    booking_width = get_width(no_rooms)-6 
    return {"style":"width: %spx; top: %spx; height: %spx;"%(booking_width, booking_offset(rusage, open), booking_height(rusage))}

def week_event_style(resources, rusage, rooms_displayed, room_selected, open, all_overlaps, only_my_bookings=0):
    """Get various style attributes for a booking
    e.g. height, width, left, top, displayed, selected etc
    """
    attribs = {}
    room = rusage.resource
    watching = mewatching(rusage)
    if rusage.confirmed:
        room_class = " room"+str(resources.index(room)+1)
    else:
        room_class = " room_t"
    my_booking = mybooking(rusage)
    if only_my_bookings and not my_booking:
	attribs['class'] = 'event other_booking_off'+ room_class + selected_room(rusage.resource.id, room_selected)
    elif watching:
        attribs['class'] = 'event' + watching + room_class + selected_room(rusage.resource.id, room_selected)
    elif not only_my_bookings and not my_booking:
        attribs['class'] = 'event other_booking' + room_class + selected_room(rusage.resource.id, room_selected)
    else:
        attribs['class'] = 'event' + my_booking + room_class + selected_room(rusage.resource.id, room_selected)
    if room.id in rooms_displayed:
        attribs['class'] += ' resource_on'
    else:
        attribs['class'] += ' resources_off'
    index, overlaps = all_overlaps[rusage.id]
    attribs['class'] += ' layer'+str(index)
    attribs['style'] = week_coordinates(open, rusage, overlaps, index)
    return attribs

from hubspace.controllers import unavailable_for_booking

def week_unavailable_style(resources, res, other_rusage, rooms_displayed, room_selected, open, all_overlaps, only_my_bookings):
    attribs = {}
    room_class = " room"+str(resources.index(res)+1)
    attribs['class'] = 'unavailable'+ room_class + selected_room(res.id, room_selected)
    if res.id in rooms_displayed:
        attribs['class'] += ' resource_on'
    else:
        attribs['class'] += ' resources_off'
    index, overlaps = all_overlaps[str(other_rusage.id)+'-'+str(res.id)]
    attribs['class'] += ' layer'+str(index)
    if only_my_bookings:
        attribs['class'] += " other_booking_off"
    attribs['style'] = week_coordinates(open, other_rusage, overlaps, index)
    
    return attribs


def week_coordinates(open, rusage, overlaps=1, overlap_index=0):
    """overlaps includes the current event
    """
    booking_h = booking_height(rusage)
    booking_o = booking_offset(rusage, open)
    half_life = 3.0
    total_width = 87.0
    booking_width = total_width/(2**((overlaps-1)/half_life))
    margin_space = total_width-booking_width
    if overlaps==1:
        margin_left = 0
    else:
        margin_left = float(overlap_index*margin_space)/float((overlaps-1))
    return "width: %spx; top: %spx; height: %spx; margin-left: %spx;"%(booking_width, booking_o, booking_h, margin_left)


def get_week_overlaps(date, resources_order):
    """get a data structure which summarizes the overlaping if events in a resource group. This is used for rendering initially and should be returned as json in order to dynamically re-render 
    """
    week_starts = date - timedelta(days=date.weekday())
    day = week_starts
    week_ends = week_starts + timedelta(days=7)
    rusages = list(RUsage.select(AND(IN(RUsage.q.resourceID, resources_order),
                                     RUsage.q.start>=week_starts,
                                     RUsage.q.end_time<=week_ends)).orderBy('start'))
    conflicting_rusages = []
    for res_id in resources_order:
        conflicting_rusages += [AttrDict(id=str(conflict.id)+'-'+str(res_id),
                                         start = conflict.start,
                                         end_time = conflict.end_time) for conflict in unavailable_for_booking(res_id, week_starts, week_ends, ignore_current_res=True)]
        
        
    rusages += conflicting_rusages
    rusages.sort(lambda x,y:cmp(x.start, y.start))
    rusages = list(rusages)
    overlaps_and_index = {}
    current = 0
    while day<=week_ends:
        day = day + timedelta(days=1)
        position_indices = []
        while current<len(rusages) and rusages[current].start<=day:
            for rusage in position_indices:
                if rusage and rusage.end_time <= rusages[current].start:
                    position_indices[position_indices.index(rusage)] = None
            try:
                position_indices[position_indices.index(None)] = rusages[current]
            except ValueError:
                position_indices.append(rusages[current])

            index = position_indices.index(rusages[current])
            look_ahead = 0
            overlaps = 1
            current_overlaps = []
            while look_ahead<len(rusages) and rusages[look_ahead].start<rusages[current].end_time:
                if rusages[look_ahead].end_time<=rusages[current].start:
                    look_ahead += 1
                    continue
                if look_ahead==current:
                    look_ahead += 1
                    continue
                #the look_ahead  current and ends after the current starts => we must add it to the current_overlaps list
                current_overlaps.append(rusages[look_ahead])
                to_remove = []
                for overlap in current_overlaps:
                    if overlap.end_time <= rusages[look_ahead].start:
                        to_remove.append(overlap)
                for remove in to_remove:
                    current_overlaps.remove(remove)
                overlaps = max(overlaps, len(current_overlaps)+1)
                look_ahead += 1
            overlaps_and_index[rusages[current].id] = (index, overlaps)
            current += 1
    return overlaps_and_index


