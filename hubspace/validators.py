import string
from turbogears import validators as v
from turbogears.validators import TgFancyValidator
from formencode import All, Any, Invalid, ForEach
from hubspace import model
from sqlobject import AND
from turbogears.i18n import format
from datetime import time, datetime, timedelta
from hubspace.model import Resource, RUsage, Pricing
from hubspace.utilities.uiutils import now
from hubspace.utilities.permissions import locations
import hubspace.bookinglib as bookinglib
import hubspace.alerts.messages
from cgi import escape

__all__ = ['Numbers', 'phone', 'MessageCustSchema', 'ExportUsersJSONSchema', 'ExportUsersCSVSchema', 'ProfileSchema', 'MemberServiceSchema', 'datetimeconverter', 'datetimeconverter2', 'timeconverter', 'timeconverterAMPM', 'AddMemberSchema', 'AddNoteSchema', 'EditNoteSchema', 'BillingDetailsSchema', 'real_int', 'IntOrNone', 'dateconverter', 'EditBookingSchema', 'CreateBookingSchema',  "CreateUsageSchema", "CreateUsageByNameSchema", "EditTodoSchema", "CreateTodoSchema", 'BristolDataSchema', "AddPricingSchema", "EditLocationSchema", "FloatInRange", 'AddAction', 'DateRange', 'NoHyphen', "StartBookingSchema", "BoolInt", "valid_rfid", 'username', 'email_address', 'no_ws_ne_cp', 'no_ws']

class Numbers(v.Regex):
    """Must contain only integers and spaces (e.g. phone number)
    """
    regex = r"^[ 0-9/.\(\)\+-]*$"

    messages = {
        'invalid': 'Enter numbers, space or one of the punctuation characters ./+()-',
        }

class PostCode(v.Regex):
    regex = r"^[a-zA-Z]{1,2}[\d]{1,2}[a-zA-Z]?\s?\d[a-zA-Z]{2}$"
    messages = {
        'invalid': 'Not a valid UK postcode',
        }


class PlainText(v.Regex):
    """Must contain only alphanumic and .-_
    """
    regex = r"^[0-9a-zA-Z._-]*$"

    messages = {
        'invalid': 'Must contain only alphanumeric characters or ".", "_" or "-"',
        }


class LowerText(v.Regex):
    """Must contain only integers and spaces (e.g. phone number)
    """
    regex = r"^[0-9a-z._-]*$"

    messages = {
        'invalid': 'Must contain only lowercase letters, numbers and characters or ".", "_" or "-"',
        }

from formencode.validators import String

class Capitalise(String):
    def _to_python(self, value, state):
        try:
            return " ".join([val.capitalize() for val in value.split(" ")])
        except:
            raise Invalid(`value` + ' cannot be capitalized', value, state)

class NoHyphen(TgFancyValidator):
    def _to_python(self, value, state):
        value = v.UnicodeString().to_python(value, state)
        if u'-' in value or u'.' in value:
            raise Invalid("Resource group name cannot contain dots or hyphens", value, state)
        return value

        
class NoWhiteSpace(String):
    capitalize = False
    def _to_python(self, value, state):
        value = v.UnicodeString().to_python(value, state)
        try:
            value =  value.strip()
        except:
            raise Invalid(value + ' is not a string', value, state)
        if self.capitalize:
            value = Capitalise().to_python(value, state)

        return value

no_ws_ne = All(NoWhiteSpace(), v.NotEmpty())
no_ws = NoWhiteSpace()
no_ws_cp = NoWhiteSpace(capitalize=True)
no_ws_ne_cp = All(NoWhiteSpace(capitalize=True), v.NotEmpty())

class BoolInt(TgFancyValidator):
    """
    Converts a string to a boolean integer (0, 1).
    
    Values like 'true' and 'false' are considered True and False,
    respectively; anything in ``true_values`` is true, anything in
    ``false_values`` is false, case-insensitive).  The first item of
    those lists is considered the preferred form.

    ::

        >>> s = BoolInt()
        >>> s.to_python('yes'), s.to_python('no')
        (1, 0)
        >>> s.to_python(1), s.to_python('N')
        (1, 0)
        >>> s.to_python('ye')
        Traceback (most recent call last):
            ...
        Invalid: Value should be 'true' or 'false'
    """
    
    true_values = ['true', 't', 'yes', 'y', 'on', '1']
    false_values = ['false', 'f', 'no', 'n', 'off', '0']

    messages = { "string" : "Value should be %(true)r or %(false)r" }
    
    def _to_python(self, value, state):
        if isinstance(value, (str, unicode)):
            value = value.strip().lower()
            if value in self.true_values:
                return 1
            if not value or value in self.false_values:
                return 0
            raise Invalid(self.message("string", state,
                                       true=self.true_values[0],
                                       false=self.false_values[0]),
                          value, state)
        return value and 1 or 0
    
    def _from_python(self, value, state):
        if value:
            return self.true_values[0]
        else:
            return self.false_values[0]   

class IntInRange(TgFancyValidator):
    min = 0
    max = 100

    def _to_python(self, value, state):
        try:
            value = int(value)
            if value>=self.min and value<=self.max:
                return value
            raise Invalid(`value` + ' is not in range ' + `self.min` + " to " + `self.max`, value, state)
        except ValueError:
            raise Invalid(`value` + ' is a non integer value', value, state)

class IntOrNone(TgFancyValidator):
    def _to_python(self, value, state):
        value = v.Int.to_python(value)
        if not value:
            value = None
        return value

class rfid(TgFancyValidator):
    # is card already registered -> fail and say who its registered too
    #check length 8 and isHex
    hex_chars = ['a', 'b', 'c', 'd', 'e', 'f']
    hex_chars.extend(str(num) for num in range(0, 10))
    def _to_python(self, value, state):
        from hubspace.controllers import get_user_from_rfid
        if len(value) != 8:
            raise Invalid(`value` + ' is not the correct length', value, state)
        for char in value:
            if char not in self.hex_chars and char.upper() not in self.hex_chars:
                raise Invalid(`value` + ' is not hexadecimal', value, state)
        user = get_user_from_rfid(str(value))
        if user:
            raise Invalid("Card is already assigned to %s" %(user.display_name), value, state)
        return value

valid_rfid = rfid()

class FloatInRange(TgFancyValidator):
    min = 0
    max = 100

    def _to_python(self, value, state):
        try:
            value = float(value)
            if value>=self.min and value<=self.max:
                return value
            raise Invalid("Not in range " + `self.min` + " to " + `self.max`, value, state)
        except ValueError:
            raise Invalid(`value` + ' is a non float value', value, state)


phone = All(v.MaxLength(20), Numbers()) 


from hubspace.model import User
from turbogears import identity

class DontDeactivateSelf(v.FormValidator):
    show_match = False
    field_names = None
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')
    
    def validate_partial(self, field_dict, state):
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        from hubspace.controllers import permission_or_owner
        user_id = field_dict['id']
        user = User.get(user_id)
        if permission_or_owner(user.homeplace, None, 'manage_users'):
            if 'active' not in field_dict or field_dict['active'] == False:
                if identity.current.user.id == user_id:
                    raise Invalid("You Cannot Deactivate Your Own Profile", field_dict, state, error_dict={'active':"You Cannot Deactivate Your Own Profile"})




#class DateTimeC(v.DateTimeConverter):
#    def _from_python(self, value, state):
#        self.format = "%d/%m/%Y %H:%M:%S"
#        super._from_python(self, value, state)
    
    
datetimeconverter = v.DateTimeConverter("%a, %d %B %Y %H:%M:%S")
datetimeconverter2 = v.DateTimeConverter("%a, %d %B %Y %H:%M")
dateconverter = v.DateTimeConverter("%a, %d %B %Y")
timeconverter = v.DateTimeConverter("%H:%M")
timeconverterAMPM = v.DateTimeConverter("%I:%M%p")

class DateRange(TgFancyValidator):
    date_separator = ' - '
    def _to_python(self, value, state):
        value = value.split(' - ')
        try:
            value = (dateconverter.to_python(value[0]), dateconverter.to_python(value[1]))
            return value
        except:
            raise Invalid(`value` + ' is not a date range', value, state)
        
real_int = v.Int(not_empty=True)
checkbox = v.Int(if_empty=0)

class UniqueAttribute(v.FormValidator):
    show_match = False
    field_names = None
    objecttype = "User"
    attr = "user_name"
    
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    
    def validate_partial(self, field_dict, state):
        for name in self.field_names:
            if not field_dict.has_key(name):
                return
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        
        theclass = getattr(model, self.objecttype)
        
        id = field_dict.get('id', None)

        this_object = None
        this_value = None
        attr_value = field_dict[self.attr]
        errors = {}

        if id:
            this_object = theclass.get(id)
            this_value = getattr(this_object, self.attr)
            
        if attr_value in [getattr(obj, self.attr) for obj in theclass.select()]: #this is extemely inefficient - rewrite with a specific sql request
            if attr_value != this_value:
                errors[self.attr] = "The " + self.attr + " "+ str(attr_value) + " already exists"
                raise Invalid(
                    'That username already exists', field_dict, state, error_dict=errors)


class ManagedLocation(v.FancyValidator):
    def _to_python(self, value, state):
        return value == 'all' and 'all' or int(value)
    def validate_python(self, field_dict, state):
        _validator = v.OneOf([loc.id for loc in locations()])
        return _validator.validate_python(field_dict, state)

class CheckCustMessage(v.FormValidator):
    show_match = False
    field_names = None
    validate_partial_form = False
    __unpackargs__ = ('*', 'field_names')
    
    def validate_python(self, field_dict, state):
        msg = hubspace.alerts.messages.bag[field_dict["msg_name"]]
        dummy_data = dict([(m.name, m.name) for m in msg.available_macros])
        try:
            string.Template(field_dict['msg_cust']).substitute(dummy_data)
        except KeyError, e:
            error_text = 'Invalid Macro: %s' % e.args[0]
            error_dict = dict(msg_cust = error_text)
            raise Invalid(error_text, field_dict, state, error_dict=error_dict)
        except Exception, e:
            error_text = str(e)
            error_dict = dict(msg_cust = error_text)
            raise Invalid(error_text, field_dict, state, error_dict=error_dict)

class MessageCustSchema(v.Schema):
    loc_id = ManagedLocation()
    msg_name = String
    msg_cust = String
    chained_validators = [ CheckCustMessage('msg_name', 'msg_cust') ]

class ExportUsersCSVSchema(v.Schema):
    location = ManagedLocation()

class ExportUsersJSONSchema(v.Schema):
    location = ManagedLocation()
    page=v.Int()
    rp=v.Int()

class AliasSchema(v.Schema):
    id = real_int
    alias_name = no_ws

username = All(v.NotEmpty(), LowerText(), v.MinLength(1), v.MaxLength(32))
email_address = All(v.Email(), v.NotEmpty())

class ProfileSchema(v.Schema):
    id = real_int
    active = BoolInt(if_empty=0)
    user_name =  username
    first_name=no_ws_ne_cp
    last_name=no_ws_ne_cp
    title= no_ws
    organisation=no_ws
    mobile=phone
    work=phone
    home=phone
    fax= phone
    email_address=email_address
    email2=v.Email()
    email3 = v.Email()
    address=no_ws
    website=v.URL()
    sip_id=v.Email()
    skype_id=no_ws
    password=v.MinLength(5)
    password2=v.MinLength(5)
    homeplace = All(v.Int, v.NotEmpty())
    aliases = ForEach(AliasSchema())
    new_alias = no_ws
    postcode= v.UnicodeString() #PostCode(if_empty="")
    biz_type = v.UnicodeString()
    public_field = v.Int(if_empty=0)
    chained_validators = [v.FieldsMatch('password', 'password2'), UniqueAttribute('id', 'user_name'), UniqueAttribute('id', 'email_address', attr='email_address'), DontDeactivateSelf('id', 'active')]



class BristolDataSchema(v.Schema):
    org_type = ForEach(no_ws)
    no_of_emps = v.Int()
    interest_areas = ForEach(no_ws)
    org_res = no_ws
    org_prog = no_ws
    heard =  no_ws
    benefits = no_ws
    contribution = no_ws
    additional = no_ws
    
    
class MemberServiceSchema(v.Schema):
    handset = All(Numbers(), v.MinLength(2), v.MaxLength(6))
    ext = All(Numbers(), v.MinLength(2), v.MaxLength(6))
    frank_pin = All(Numbers(), v.MinLength(2), v.MaxLength(6))
    gb_storage = All(Numbers(), v.MaxLength(6))
    os = no_ws
    storage_loc = no_ws
    extra_notes = no_ws

class BillingDetailsSchema(v.Schema):
    billto = v.Int(if_empty=None)
    bill_to_profile = v.Int()
    bill_to_company = no_ws
    billingaddress = no_ws
    bill_phone = phone
    bill_fax = phone
    bill_email = v.Email()
    bill_company_no = no_ws
    bill_vat_no = no_ws

class AddMemberSchema(v.Schema):
    handset = All(Numbers(), v.MinLength(2), v.MaxLength(6))
    ext = All(Numbers(), v.MinLength(2), v.MaxLength(6))
    frank_pin = All(Numbers(), v.MinLength(2), v.MaxLength(6))
    gb_storage = All(Numbers(), v.MaxLength(6))
    os = no_ws
    storage_loc = no_ws
    extra_notes = no_ws
    active = All(BoolInt(if_empty=0))
    homeplace = All(v.Int, v.NotEmpty())
    user_name = username
    first_name= no_ws_ne_cp
    last_name = no_ws_ne_cp
    title=no_ws
    organisation=no_ws
    mobile=phone
    work=phone
    home=phone
    fax= phone
    email_address=email_address
    email2=v.Email()
    email3 = v.Email()
    address=no_ws
    website=v.URL()
    sip_id=v.Email()
    skype_id=no_ws
    password=All(v.MinLength(5), v.NotEmpty())
    password2=All(v.MinLength(5), v.NotEmpty())
    description=no_ws
    billto=v.Int()
    new_alias = no_ws
    postcode = v.UnicodeString() #needs to work interationally # PostCode()
    biz_type = v.UnicodeString()
    public_field = v.Int(if_empty=0)
    chained_validators = [v.FieldsMatch('password', 'password2'), UniqueAttribute('user_name'), UniqueAttribute('email_address', attr='email_address')]

class MonthDate(v.Schema):
    month = IntInRange(min=1, max=12)
    year = IntInRange(min=2007, max=2050)

class UniqueDate(v.FormValidator):
    show_match = False
    field_names = None
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    
    def validate_partial(self, field_dict, state):
        for name in self.field_names:
            if not field_dict.has_key(name):
                return
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        periodstarts = datetime(int(field_dict['periodstarts']['year']), int(field_dict['periodstarts']['month']), 1, 0, 0, 1)
        pricings = Pricing.select(AND(Pricing.q.periodstarts==periodstarts,
                                      Pricing.q.resourceID==int(field_dict['resource']),
                                      Pricing.q.tariffID==int(field_dict['tariff'])))
        errors = {}
        if pricings.count()>0:
            errors['periodstarts'] = "A pricing already exists for that date"
            raise Invalid(
                'A pricing already exists for that date', field_dict, state, error_dict=errors)

class AddPricingSchema(v.Schema):
    cost = v.Money(not_empty=True)
    periodstarts = MonthDate()
    tariff = real_int
    resource = real_int
    chained_validators = [UniqueDate('periodstarts', 'tariff', 'resource')]


    
class AddNoteSchema(v.Schema):
    title= no_ws
    body = no_ws
    byuser = v.Empty()
    onuser = v.Int()

class EditNoteSchema(v.Schema):
    id = real_int
    title= no_ws_ne
    body = no_ws_ne
    byuser = v.Empty()
    onuser = v.Empty()

class EditTodoSchema(v.Schema):
    id = real_int
    subject= no_ws_ne
    body = no_ws_ne
    due = dateconverter
    closed= v.Int()
    action = no_ws

class CreateTodoSchema(v.Schema):
    subject= no_ws_ne
    body = v.UnicodeString(if_empty="")
    foruser = v.Int()
    parent = v.Int()
    due = dateconverter
    action = no_ws

class AddAction(v.Schema):
    body = v.UnicodeString(if_empty="")
    foruser = v.Int()
    note = v.Int()
    due = dateconverter

class TimeDict(v.Schema):
    hour = All(IntInRange(min=0,max=23))
    minute = All(IntInRange(min=0,max=59))



class StartLessThanEnd(v.FormValidator):
    show_match = False
    field_names = None
    
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    
    def validate_partial(self, field_dict, state):
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        resource = Resource.get(field_dict['resource_id'])
        if not resource.time_based:
            return
        if 'start' in field_dict and field_dict['start']:
            start = field_dict['start']
            start_time = time(int(start['hour']), int(start['minute']))
            date = dateconverter.to_python(field_dict['date'])
            start = datetime.combine(date, start_time)
        elif 'start_datetime' in field_dict and field_dict['start_datetime']:
            start = datetimeconverter.to_python(field_dict['start_datetime'])
        else:
            start = now(resource.place)
            
        if 'end' in field_dict and field_dict['end']:
            end = field_dict['end']
            end_time = time(int(end['hour']), int(end['minute']))
            date = dateconverter.to_python(field_dict['date'])
            end = datetime.combine(date, end_time)
        elif 'end_datetime' in field_dict and field_dict['end_datetime']:
            end = datetimeconverter.to_python(field_dict['end_datetime'])
        else:
            end = start
            
        errors = {}

        if end <= start:
            errors['end'] = _("The booking must end later than it starts!")
            errors['start'] = _("The booking must start before ending!")
            raise Invalid(
                'That booking ends before starting', field_dict, state, error_dict=errors)

class TentativeValidity(v.FormValidator):
    show_match = False
    field_names = None
    
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    
    def validate_partial(self, field_dict, state):
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        resource = Resource.get(field_dict['resource_id'])
        if not resource.time_based:
            return
        if 'start' in field_dict and field_dict['start']:
            start = field_dict['start']
            start_time = time(int(start['hour']), int(start['minute']))
            date = dateconverter.to_python(field_dict['date'])
            start = datetime.combine(date, start_time)
        elif 'start_datetime' in field_dict and field_dict['start_datetime']:
            start = datetimeconverter.to_python(field_dict['start_datetime'])
        else:
            start = now(resource.place)
        if field_dict.get("tentative"):
            if (start - now()) < timedelta(2):
                errors = {}
                err = _("A tentative booking should be made at least %s hours in advance!")  % bookinglib.t_booking_life_hrs
                errors['tentative'] = err
                errors['date'] = err
                raise Invalid(err, field_dict, state, error_dict=errors)


class BookingConflicts(v.FormValidator):
    show_match = False
    field_names = None
    
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    
    def validate_partial(self, field_dict, state):
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        from hubspace.controllers import unavailable_for_booking
        resource = Resource.get(field_dict['resource_id'])
        resourceid = resource.id
        if not resource.time_based:
            return

        if 'start' in field_dict:
            start = field_dict['start']
            start_time = time(int(start['hour']), int(start['minute']))
            date = dateconverter.to_python(field_dict['date'])
            start = datetime.combine(date, start_time)
        elif 'start_datetime' in field_dict:
            start = datetimeconverter.to_python(field_dict['start_datetime'])
        else:
            start = now(resource.place)
            
        if 'end' in field_dict:
            end = field_dict['end']
            end_time = time(int(end['hour']), int(end['minute']))
            date = dateconverter.to_python(field_dict['date'])
            end = datetime.combine(date, end_time)
        elif 'end_datetime' in field_dict:
            end = datetimeconverter.to_python(field_dict['end_datetime'])
        else:
            end = start + timedelta(minutes=15)
       
        errors = {}
            
        rusage = None
        if 'id' in field_dict:
            rusage = field_dict['id']

        booking_conflicts = unavailable_for_booking(resourceid, start, end, rusage)
        dfp = datetimeconverter.from_python
 
        if booking_conflicts.count():
            conflict = booking_conflicts[0]
            if resource == conflict.resource:
                errors['start'] =  escape(resource.name) + " cannot be booked from " + dfp(start) + " to "+ dfp(end) + " since it is booked from " + dfp(conflict.start) + " to " + dfp(conflict.end_time)
            else:
                errors['start'] =  escape(resource.name) + " cannot be booked from " + dfp(start) + " to "+ dfp(end) + " since it requires " + escape(conflict.resource.name)+ " which is booked from " + dfp(conflict.start) + " to " + dfp(conflict.end_time)
            raise Invalid('Booking Conflicts', field_dict, state, error_dict=errors)
        
class EditBookingSchema(v.Schema):
    id = real_int
    resource_id = real_int
    user = v.Int()
    quantity = v.Int(if_empty=1)
    customcost = v.Money()
    customname = v.UnicodeString(if_empty=None)
    date = dateconverter
    start = TimeDict()
    end = TimeDict()
    number_of_people = v.Int(if_empty=1)
    meeting_name = no_ws
    meeting_description = no_ws
    notes = no_ws
    options = ForEach(v.Int(not_empty=True))
    public_field = v.Int(if_empty=0)
    chained_validators=[StartLessThanEnd('start', 'end'), BookingConflicts('start', 'end', 'date', 'resource_id', 'id'), TentativeValidity('start', 'tentative')]

class StartBookingSchema(v.Schema):
    rusage_id = real_int
    start_datetime = datetimeconverter
    chained_validators=[BookingConflicts('start_datetime', 'resource_id')]    

class CreateBookingSchema(v.Schema):
    resource_id = real_int
    user = v.Int()
    quantity = v.Int(if_empty=1)
    customcost = v.Money()
    customname = v.UnicodeString(if_empty=None)
    date = dateconverter
    start = TimeDict()
    end = TimeDict()
    number_of_people = v.Int(if_empty=1)
    meeting_name = no_ws
    meeting_description = no_ws
    notes = no_ws
    options = ForEach(v.Int(not_empty=True))
    public_field = v.Int(if_empty=0)
    tentative = v.Bool(if_empty=False)
    chained_validators = [StartLessThanEnd('start', 'end'), BookingConflicts('start', 'end', 'resource_id'), TentativeValidity('start', 'tentative')]

class CreateUsageSchema(v.Schema):
    """more general, not just for the particular interface
    """
    resource_id = real_int
    user = v.Int()
    quantity = v.Int(if_empty=1)
    customcost = v.Money()
    customname = v.UnicodeString(if_empty=None)
    start_datetime = datetimeconverter
    end_datetime = datetimeconverter 
    number_of_people = v.Int(if_empty=1)
    meeting_name = no_ws
    notes = no_ws
    options = ForEach(v.Int(not_empty=True))
    public_field = BoolInt
    chained_validators = [StartLessThanEnd('start_datetime', 'end_datetime'), BookingConflicts('start_datetime', 'end_datetime', 'resource_id')]
   


class CreateUsageByNameSchema(v.Schema):
    """more general, not just for the particular interface
    """
    resource_name = no_ws
    location = real_int
    user = v.Int()
    quantity = v.Int(if_empty=1)
    customcost = v.Money()
    customname = v.UnicodeString(if_empty=None)
    start_datetime = datetimeconverter
    end_datetime = datetimeconverter 
    number_of_people = v.Int(if_empty=1)
    meeting_name = no_ws
    notes = no_ws
    options = ForEach(v.Int(not_empty=True))


from pytz import timezone

class TimeZone(TgFancyValidator):
    def _to_python(self, value, state):
        try:
            timezone(value)
            return value
        except:
            raise Invalid(`value` + ' is a valid timezone', value, state)

class Localhost(TgFancyValidator):
    def _to_python(self, value, state):
        if value.startswith('http://localhost:'):
            return value
        else:
            raise Invalid(`value` + ' is not localhost', value, state)

class EditLocationSchema(v.Schema):
    id = real_int
    name = no_ws_ne_cp
    currency = All(no_ws, v.MaxLength(3))
    timezone = TimeZone()
    vat_included = checkbox
    rfid_enabled = checkbox
    microsite_active = checkbox
    tentative_booking_enabled = checkbox
    invoice_newscheme = v.Int(if_empty=False)
    invoice_duedate = v.Int(min=0, if_empty=0)
    vat_no =  All(no_ws, v.MaxLength(40))
    vat_default = FloatInRange(min=0, max=100)
    billing_address = no_ws
    company_no = All(no_ws, v.MaxLength(40))
    bank = All(no_ws, v.MaxLength(40))
    sort_code = All(Numbers(), v.MaxLength(8))
    account_no = All(Numbers(), v.MaxLength(40))
    iban_no = All(no_ws, v.MaxLength(32))
    swift_no = All(no_ws, v.MaxLength(40))
    switch_no = All(Numbers(), v.MaxLength(8))
    url = Any(v.URL(), Localhost())
    telephone = phone
    chained_validators = [UniqueAttribute('id', 'name', attr='name', objecttype="Location")]    
