import datetime
import string
import logging

from turbogears import identity
import sendmail
import model
from utilities.dicts import ObjDict
import hubspace.alerts

t_booking_life = datetime.timedelta(3)
day_seconds = 24 * 60 * 60
hr_seconds = 60 * 60
t_booking_life_hrs = ((t_booking_life.days * day_seconds) / hr_seconds)

applogger = logging.getLogger("hubspace")

def timeLapsed(booking):
    return datetime.datetime.now() - booking.date_booked

def timeLeftToConfirm(booking, in_hours):
    t_left = t_booking_life - timeLapsed(booking)
    if in_hours:
        t_left = (((t_left.days * day_seconds) + t_left.seconds) / hr_seconds)
    return t_left

def remindForConfirmation(booking):
    to = booking.user.email_address
    d = dict ( date_expire=str(booking.date_booked + t_booking_life),
               resource_name = booking.resource_name,
               date_booked = booking.date_booked,
               start= booking.start,
               end = booking.end_time,
               to = to,
               b_id = booking.id )
    hubspace.alerts.sendTextEmail(to, "t_booking_reminder", d)
    applogger.debug("bookinglib: confirmation reminder sent to %(to)s. %(b_id)s (%(resource_name)s: %(start)s-%(end)s)" % d)

def requestBookingConfirmations():
    bookings_unconfirmed = model.RUsage.selectBy(confirmed=0)
    d1 = 24 # hours
    d2 = ((t_booking_life - datetime.timedelta(seconds=6*60*60)), (t_booking_life - datetime.timedelta(seconds=5*60*60)))
    d3 = t_booking_life + datetime.timedelta(seconds=60*60)
    for booking in bookings_unconfirmed:
        t_lapsed = timeLapsed(booking)
        try:
            ## 1 ##
            if t_lapsed >= d3: # Time over. So destroy tentative booking
                notifyTentativeBookingRelease(booking)
                for u in booking.suggested_usages:
                    applogger.debug("bookinglib: destroying suggested_usage %s" % u.id)
                    u.destroySelf()
                applogger.debug("bookinglib: destroying %s" % booking.id)
                booking.destroySelf()
                applogger.debug("bookinglib: destroyed  %s" % booking.id)
            ## 2 ##
            elif d2[0] > t_lapsed > d2[1]: # six hours left, remind
                remindForConfirmation(booking)
            ## 3 ##
            elif t_lapsed > d2[0] and ((t_lapsed.seconds / (60*60)) % d1) == 0: # Remind if more than 6 hours left and every 24 hours
                remindForConfirmation(booking)
        except Exception, err:
            applogger.exception("bookinglib: ")
    print "booking confirmations requests sent"
    return True

def notifyTentativeBookingRelease(booking):
    request_q = model.ResourceQueue.selectBy(rusage=booking)
    no_watching = request_q.count()
    extra_text = ""
    if no_watching > 1:
        extra_text = "\n%d other members also received the same alert. It is possible somebody else claims the resource before you do.\n" % no_watching
    d = dict (start_time=booking.start.strftime("%H:%M"),
              end_time=booking.end_time.strftime("%H:%M"),
              date =booking.start.strftime("%Y-%m-%d"),
              bookedby=booking.bookedby.display_name,
              resource_name=booking.resource_name,
              start=str(booking.start),
              end=str(booking.end_time),
              b_id = booking.id,
              location_name = booking.resource.place.name,
              location_url = booking.resource.place.url or "http://members.the-hub.net",
              extra_text=extra_text)
    for request in request_q:
        to = request.foruser.email_address
        d2 = dict ( to = to,
                    name = "%s %s" % (request.foruser.first_name, request.foruser.last_name),
                    req_id = request.id )
        d.update(d2)
        data = dict ( rusage = booking, user = booking.user, location = booking.resource.place )
        hubspace.alerts.sendTextEmail("t_booking_expired_watcher", to=to, data=data)
        applogger.debug("bookinglib: release notification sent to %(to)s. %(b_id)s:%(req_id)s (%(resource_name)s: %(start)s-%(end)s)" % d)
        request.destroySelf()
    data = dict ( rusage = booking, user = booking.user, location = booking.resource.place )
    hubspace.alerts.sendTextEmail("t_booking_expired_hosts", data=data)
    applogger.debug("bookinglib: release notification sent. %(b_id)s (%(resource_name)s: %(start)s-%(end)s)" % d)

def onBookingConfirmation(booking):
    request_q = model.ResourceQueue.selectBy(rusage=booking)
    for request in request_q:
        to = request.foruser.email_address
        sender = 'noreply@the-hub.net'
        subject = "Notification: Resource unavailable"
        body = string.Template(\
"""
Dear Member,

You had requested for receiving notification on availability of "$resource_name".
The member who has tentatively booked this resource has just confirmed the booking. And hence the
resource would not be available for booking from $start_time to $end_time.


This is an automated alert. Do not reply.
Thanks.
""").substitute(ObjDict(booking), start_time=str(booking.start), end_time=str(booking.end_time))
        sendmail.sendmail(to,sender,subject,body)
        request.destroySelf()
   
def isAvailabilityInfoReqValid(rusage):
    if not rusage.resource.place.tentative_booking_enabled or rusage.resource.type != 'room' or rusage.confirmed or identity.current.user == rusage.bookedby or list(model.ResourceQueue.selectBy(rusage=rusage, foruser=identity.current.user)):
        return False
    return True

def canConfirm(rusage):
    if rusage.resource.type == 'room' and not rusage.confirmed and identity.current.user == rusage.bookedby:
        return True
    return False
