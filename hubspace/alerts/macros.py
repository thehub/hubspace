import sys
import traceback
import turbogears
import turbogears.identity as identity

class Macro(object):
    def __new__(cls, *args, **kw):
        if hasattr(cls, 'inst'): return cls.inst
        cls.inst = object.__new__(cls, *args, **kw)
        return cls.inst
    def __init__(self):
        self.label = getattr(self.__class__, 'label', self.__class__.__name__.replace('_', ' '))
        self.name = getattr(self.__class__, 'name', self.__class__.__name__.upper())
    def getValue(self, data):
        raise NotImplemented

class Time_Now(Macro):
    def getValue(self, data):
        location = data['location']
        loc_id = location and location.id or 1
        return str(hubspace.utilities.uiutils.now(loc_id))

class Date_Now(Macro):
    def getValue(self, data):
        location = data['location']
        loc_id = location and location.id or 1
        return str(hubspace.utilities.uiutils.now(loc_id))

class Location(Macro):
    def getValue(self, data):
        return data['location'].name

class Location_URL(Macro):
    def getValue(self, data):
        return data['location'].url or "http://members.the-hub.net"

class Member_Email(Macro):
    label = "Member Email"
    def getValue(self, data):
        return data['user'].email_address

class Hosts_Email(Macro):
    label = "Host's Email"
    def getValue(self, data):
        return data['location'].hosts_email

class Membership_Number(Macro):
    def getValue(self, data):
        return data['user'].id

class Member_Name(Macro):
    def getValue(self, data):
        return data['user'].display_name

class Member_Home(Macro):
    def getValue(self, data):
        return data['user'].homeplace.name

class Member_First_Name(Macro):
    label = "First Name"
    def getValue(self, data):
        return data['user'].first_name

class Member_Last_Name(Macro):
    label = "Last Name"
    def getValue(self, data):
        return data['user'].last_name

class Username(Macro):
    def getValue(self, data):
        return data['user'].user_name

class Password(Macro):
    def getValue(self, data):
        return data['password']

class Location_Phone(Macro):
    def getValue(self, data):
        return data['location'].telephone

class Resource(Macro):
    def getValue(self, data):
        return data['rusage'].resource.name

class Booking_Contact(Macro):
    label = "Booking Contact"
    def getValue(self, data):
        return data['location'].name.lower().replace(' ', '') + ".bookings@the-hub.net"

class Booking_Start(Macro):
    label = "Start"
    def getValue(self, data):
        from hubspace.validators import timeconverter, dateconverter
        return timeconverter.from_python(data['rusage'].start)

class Booking_End(Macro):
    label = "End"
    def getValue(self, data):
        from hubspace.validators import timeconverter, dateconverter
        return timeconverter.from_python(data['rusage'].end_time)

class Booking_Date(Macro):
    def getValue(self, data):
        from hubspace.validators import timeconverter, dateconverter
        return dateconverter.from_python(data['rusage'].start)

class Booked_by(Macro):
    def getValue(self, data):
        from hubspace.validators import timeconverter, dateconverter
        return dateconverter.from_python(data['rusage'].bookedby.display_name)

class Repeat_Dates(Macro):
    label = "Repeat Dates"
    def getValue(self, data):
        return  '   ' + '\n   '.join(adate.strftime("%a, %b %d %Y") for adate in data['repeat_dates'])

class Currency(Macro):
    def getValue(self, data):
        rusage = data['rusage']
        return rusage.resource.place.currency == 'GBP' and u'\xa3' or rusage.resource.place.currency

class Cost(Macro):
    def getValue(self, data):
        from hubspace.utilities.uiutils import c2s
        rusage = data['rusage']
        return  c2s([rusage.customcost,rusage.cost][rusage.customcost == None])

class Also_Booked(Macro):
    def getValue(self, data):
        rusage = data['rusage']
        suggested_usages = [u.resource.name for u in rusage.suggested_usages]
        if suggested_usages:
            return _("Also booked: ") + ", ".join(suggested_usages)
        return ""
    
class Time_Left_To_Confirm(Macro):
    label = "Time left to confirm"
    def getValue(self, data):
        import hubspace.bookinglib as bookinglib
        rusage = data['rusage']
        return bookinglib.timeLeftToConfirm(rusage, in_hours=True)

class Traceback(Macro):
    def getValue(self, data):
        tb = sys.exc_info()[2]
        return traceback.format_exc(tb)

class Trac_URL(Macro):
    def getValue(self, data):
        return turbogears.config.config.configs['trac']['baseurl']

