from turbogears.validators import Money
from turbogears import config, identity
from hubspace.model import Invoice, Selection, UserMetaData, Location
from pytz import common_timezones, timezone
from datetime import datetime, timedelta
from sqlobject import AND
from html5lib import sanitizer, serializer, treebuilders, treewalkers, HTMLParser

def select_home_hub(location, attrname="selected"):
    if identity.current.user.homeplace == location:
       return {attrname: attrname}
    return {}

class oddOrEven:
    def __init__(self):
        self.i = 1

    def __getattribute__(self,key):
        if key == 'odd_or_even':
            self.i = 1
        return self.__dict__[key]
    def odd_or_even(self):
        self.i +=1
        if self.i%2 is 0:
           return 'even'
        else:
           return 'odd'


def attr_not_none(object, attr):
   if hasattr(object, attr):
      if object.__getattribute__(attr):
            return True
   return False

from kid.parser import XML

def print_error(key, tg_errors):
   if tg_errors:
        if key in tg_errors:
            if not isinstance(key, basestring):
                return XML(tg_errors[key])
            return tg_errors[key]


def c2s(amount):
    amount = amount and amount or 0
    amount = Money.from_python(amount)
    return amount

def inv_currency(invoice, theuser):
    # currency is basically a meaningless string right now. 
    # if we were to have an invoice with rusages from 2 currency zones
    # we would just add the two currency values together
    # i.e. the application is not internationalised 
    if invoice:
       invoice = Invoice.get(invoice)
       return invoice.location.currency 
    return theuser.homeplace.currency

def months():
    return [(1, "January"), (2, "February"),(3, "March"), (4, "April"), (5, "May"), (6, "June"), (7, "July"), (8, "August"), (9, "September"), (10, "October"), (11, "November"), (12, "December")]
    # How about return list(enumerate([m for m in calendar.month_name]))[1:]

def zones():
    return common_timezones

def now(location=1):
    if not isinstance(location, Location):
        try:
            location = Location.get(location)
        except:
            return datetime.now()
    zone_name = location.timezone
    if not zone_name:
        zone_name = 'UTC'
    time_zone = timezone(zone_name)
    local_now = datetime.now(tz=time_zone)
    #convert back to a naive datetime object so that its comparable with those stored on rusages etc
    #ideally everything would be dealing with localised datetime objects but this would take significant work on the existing data and scripts.
    naive_now = datetime(local_now.year, local_now.month, local_now.day, local_now.hour, local_now.minute, local_now.second)
    return naive_now


def unsent_for_user(user):
    invoice = Invoice.select(AND(Invoice.q.userID==user.id,
                                 Invoice.q.sent==None))
    if invoice.count():
        return invoice[0]
    return False

def colspan(user, invoice):
    if unsent_for_user(user) and unsent_for_user(user).id==invoice:
         return "7"
    return "8"

from hubspace.model import Location, Group
def all_hosts():
    """all hosts in the system
    """
    users = []
    for location in Location.select():
        groups = Group.select(AND(Group.q.placeID==location.id,
                                  Group.q.level=="host"))
        for group in groups:
            for user in group.users:
                if user not in users:
                    users.append(user)
    users.sort(display_name)
    return users


def display_name(user1, user2):
    if user1.display_name>=user2.display_name:
        return 1
    return -1

def selected_text(obj, attr, opt, type='selected'):
    value = getattr(obj, attr)
    if value==None:
        return {}
    if int(value) == opt:
        return {type:type}
    return {}


def selected_user(user, current):
    if current == None:
        return {}
    if user.id==current.id:
        return {'selected':'selected'}
    return {}


def set_singleselected(attr_name, user, arg):
    arg = int(arg)

    obj = get_singleselected(user, attr_name)
    if obj:
        if obj.selection != arg:
            obj.destroySelf()
        else:
            return
    Selection(user=user.id, attr_name=attr_name, selection=arg)


def get_singleselected(obj, attr):
    try:
        return Selection.select(AND(Selection.q.userID == obj.id,
                                    Selection.q.attr_name==attr))[0]
    except:
        return None

def selected_single(obj, attr, opt):
    try:
        selection = int(getattr(obj, attr))
    except:
        if obj:
            try:
                selection = get_singleselected(obj, attr).selection
            except AttributeError:
                selection = None
                
    if selection == opt:
        return {'selected':'selected'}
    return {}


def set_multiselected(attr_name, user, args):
    for obj in get_multiselected(user, attr_name):
        if obj.selection not in args:
            obj.destroySelf()       
    for option in args:
        if option not in [selection.selection for selection in get_multiselected(user, attr_name)]:
            Selection(user=user.id, attr_name=attr_name, selection=option)
           

def get_multiselected(obj, attr):
    return Selection.select(AND(Selection.q.userID == obj.id,
                                Selection.q.attr_name==attr))

def selected_multiple(obj, attr, opt):
    selections = get_multiselected(obj, attr)
    for selection in selections:
        if selection.selection == opt:
            return {'selected':'selected'}
    return {}


def get_freetext_metadata(obj, attr):
    try:
        return getattr(obj, attr)
    except:
        try:
            metadata = UserMetaData.select(AND(UserMetaData.q.userID == obj.id,
                                               UserMetaData.q.attr_name == attr))
            return metadata[0].attr_value
        except:
            return u''

def set_freetext_metadata(obj, attr, val):
    metadata = UserMetaData.select(AND(UserMetaData.q.userID == obj.id,
                                       UserMetaData.q.attr_name == attr))
    try:
        metadata[0].attr_value = val
    except:
        UserMetaData(user=obj.id, attr_name=attr, attr_value=val)

def sanitize_input(chars):
    """
    html1 = "<b>shon</b>"
    html1 = "<b>shon</b><script>zzz</script>"
    print sanitize_input(html1)
    """
    p = HTMLParser(tokenizer=sanitizer.HTMLSanitizer, tree=treebuilders.getTreeBuilder("dom")) # could use Beautiful Soup here instead
    s = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False, quote_attr_values=True)
    dom_tree = p.parseFragment(chars)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(dom_tree)
    gen = s.serialize(stream)
    out = ''.join(i for i in gen)
    return out

