from sqlobject import *
from datetime import datetime
import os
from turbogears.database import PackageHub
from turbogears import config

from hubspace.utilities.image_preview import create_image_preview
import hubspace.errors
import StringIO
from turbogears import identity 
from inspect import getmodule
from sqlobject.events import listen, RowUpdateSignal, RowCreatedSignal, RowDestroySignal

import md5crypt, smbpasswd, md5, random, time, sys
import StringIO
hub = PackageHub("hubspace")
__connection__ = hub

__all__=['Visit','VisitIdentity','Group','User','Permission','Location', 'Resource','RUsage','Pricing','Todo','Invoice', 'Note', 'Alias', 'Selection', 'UserMetaData', 'Open', 'Resourcegroup', 'AccessPolicy', 'PolicyGroup', 'UserGroup', 'UserPolicyGroup']
#looks to me like foreign keys cant have names containing '_'


initial_cops = [('Designing places and spaces', 0),
                ('Progressing corporate responsibility', 0),
                ('Deploying art for social change', 0),
                ('Advancing sustainable product design', 0),
                ('Creating participatory dialogue', 0),
                ('Producing authentic communications', 0),
                ('Supporting social entrepreneurs', 0),
                ('Rethinking international development', 0),
                ('Promoting health and wellbeing', 0)]



def create_object_reference(kwargs, post_funcs):
    print "object ref created" + kwargs['class'].__name__ +  `kwargs['id']`
    obj_ref = ObjectReference(**{'object': (kwargs['class'].__name__, kwargs['id'])})

def delete_object_reference(instance, post_funcs):
    print "object ref deleted" + `instance`
    obj_ref = ObjectReference.select(AND(ObjectReference.q.object_id == instance.id,
                                         ObjectReference.q.object_type == instance.__class__.__name__))[0]
    obj_ref.destroySelf()


resource_types = ['hotdesk', 'room', 'phone', 'printer', 'tariff', 'custom', 'other', 'calendar']
graph_types = ('pattern', 'timeseries')

class Visit(SQLObject):
    class sqlmeta:
        table = "visit"

    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName="by_visit_key")
    created = DateTimeCol(default=datetime.now)
    expiry = DateTimeCol()

    def lookup_visit(cls, visit_key):
        try:
            return cls.by_visit_key(visit_key)
        except SQLObjectNotFound:
            return None
    lookup_visit = classmethod(lookup_visit)


class VisitIdentity(SQLObject):
    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName="by_visit_key")
    user_id = IntCol()



class Group(SQLObject):
    """
    An ultra-simple group definition.
    """

    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = "tg_group"

    group_name = UnicodeCol(length=40, alternateID=True, ##
                            alternateMethodName="by_group_name")
    display_name = UnicodeCol(length=255)###
    created = DateTimeCol(default=datetime.now)

    # collection of all users belonging to this group
    users = RelatedJoin("User",
                        intermediateTable="user_group",
                        createRelatedTable=False,
                        joinColumn='group_id',
                        otherColumn='user_id')

    # collection of all permissions for this group
    permissions = RelatedJoin("Permission", joinColumn="group_id", 
                              intermediateTable="group_permission",
                              otherColumn="permission_id")
    access_policies = MultipleJoin('AccessPolicy', joinColumn="group_id")    
    place = ForeignKey("Location", default=None)
    level = EnumCol(enumValues=['superuser', 'director', 'member','host'],default="member")

    def addUser(self, u):
        # for some unknown reason with default sqlobject's addUser does not fire a signal so explicitly creating
        # UserGroup instance.
        ug = UserGroup(userID=u.id, groupID=self.id)

class UserGroup(SQLObject):
    """An explicit intermidiate table between users and groups (allows firing signals on related joins)
    """
    class sqlmeta:
        table = "user_group"
    user = ForeignKey('User', notNull=True, cascade=True)
    group = ForeignKey('Group', notNull=True, cascade=True)

class UserPolicyGroup(SQLObject):
    """An explicit intermidiate table between users and policy groups (allows firing signals on related joins)
    """
    class sqlmeta:
        table = "user_policy_group"
    user = ForeignKey('User', notNull=True, cascade=True)
    policygroup = ForeignKey('PolicyGroup', notNull=True, cascade=True)


class User(SQLObject):
    """
    """
    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = "tg_user"
    user_name = UnicodeCol(length=40, 
                           alternateID=True,
                           alternateMethodName="by_user_name")
    def _get_username(self):
        return self.user_name
    email_address = UnicodeCol(length=255, 
                              alternateID=True,
                              alternateMethodName="by_email_address")
    rfid = UnicodeCol(length=255, default="")
    active = IntCol(default=1)
    display_name = UnicodeCol(length=255, default="")
    def _get_display_name(self):
        d_name = self.first_name + " " + self.last_name
        return d_name
    first_name = UnicodeCol(length=255, default="")
    def _set_first_name(self, val):
        self._SO_set_first_name(val)
        if hasattr(self, 'last_name'):
            self._SO_set_display_name(val + ' ' + self.last_name)
    last_name = UnicodeCol(length=255, default="")
    def _set_last_name(self, val):
        self._SO_set_last_name(val)
        if hasattr(self, 'first_name'):
            self._SO_set_display_name(self.first_name + ' ' + val)
    title = UnicodeCol(length=255,default="")
    organisation = UnicodeCol(length=255,default="")
    mobile = UnicodeCol(length=30,default="")
    work = UnicodeCol(length=30,default="")
    home = UnicodeCol(length=30,default="")
    fax = UnicodeCol(length=30,default="")
    password = UnicodeCol(length=40)
    created = DateTimeCol(default=datetime.now)
    modified = DateTimeCol(default=datetime.now)
    email2 = UnicodeCol(length=255,
                       default="")
    email3 =  UnicodeCol(length=255,
                        default="")
    address = UnicodeCol(default="")
    skype_id = UnicodeCol(default="")
    sip_id = UnicodeCol(default="")
    website = UnicodeCol(default="")
    homeplace = ForeignKey('Location', default=None)
    welcome_sent = IntCol(default=0)
    signedby = ForeignKey('User', default=None)
    hostcontact = ForeignKey('User', default=None)
    signedfor = MultipleJoin("User",joinColumn='signedby_id')
    hostcontactfor = MultipleJoin("User",joinColumn='hostcontact_id')

    cops = PickleCol(default=initial_cops,length=2**16+1)
    bristol_metadata = PickleCol(default={},length=2**16+1)
    def _get_bristol_metadata(self):
        val = self._SO_get_bristol_metadata()
        if not val:
            return {}
        return val

    handset = UnicodeCol(default="")
    ext = UnicodeCol(default="")
    frank_pin = UnicodeCol(default="")
    gb_storage = UnicodeCol(default="")
    os = UnicodeCol(default="")
    storage_loc = UnicodeCol(default="")
    
    description = UnicodeCol(default="")

    billto = ForeignKey("User", default=None)
    bill_to_profile = IntCol(default=1)
    bill_to_company = UnicodeCol(default="")
    billingaddress = UnicodeCol(default="")
    bill_phone = UnicodeCol(default="")
    bill_fax = UnicodeCol(default="")
    bill_email = UnicodeCol(default="")
    bill_company_no = UnicodeCol(default="")
    bill_vat_no = UnicodeCol(default="")
    # groups this user belongs to
    groups = RelatedJoin("Group",
                         intermediateTable="user_group",
                         createRelatedTable=False,
                         joinColumn="user_id",
                         otherColumn="group_id")
    access_policies = PickleCol(default=[], length=2**16+1)
    def _get_access_policies(self):
        val = self._SO_get_access_policies()
        if not val:
            return []
        return val

    disabled_policies = PickleCol(default=[], length=2**16+1)
    def _get_disabled_policies(self):
        val = self._SO_get_disabled_policies()
        if not val:
            return []
        return val

    policy_groups = RelatedJoin('PolicyGroup',
                                intermediateTable='user_policy_group',
                                joinColumn='user_id',
                                otherColumn='policygroup_id',
                                createRelatedTable=False,)
    booked_by = MultipleJoin("RUsage",joinColumn='bookedby_id')
    rusages = MultipleJoin("RUsage",joinColumn='user_id')
    invoices = MultipleJoin("Invoice",joinColumn='user_id')
    todos_outgoing = MultipleJoin("Todo",joinColumn='createdby_id')
    todos_incoming = MultipleJoin("Todo",joinColumn='foruser_id')
    billed_for = MultipleJoin("User",joinColumn='billto_id')
    notes_on =  MultipleJoin("Note", joinColumn='onuser_id')
    notes_by = MultipleJoin("Note", joinColumn='byuser_id')
    aliases = MultipleJoin("Alias",joinColumn='user_id')
    metadata = MultipleJoin("UserMetaData",joinColumn='user_id')
    selections = MultipleJoin("Selection",joinColumn='user_id')
    #For public field
    public_field=IntCol(default=0)
    

    #No clue why this is needed, but catwalk does not want to run without
    #it sucks - jhb, 01.10.06
    child_name=UnicodeCol(default=None)

    image_mimetype=UnicodeCol(default=None)

    #Password hashes
    unix_hash = UnicodeCol(length=50,default=None)
    lanman_hash = UnicodeCol(length=50,default=None)
    nt_hash = UnicodeCol(length=50,default=None)

    #Outstanding money
    outstanding = CurrencyCol(default=0)
    reminder_counter = IntCol(default=0)
    last_reminder = DateTimeCol(default=None)

    #password reminder
    reminderkey = UnicodeCol(length=50,default=None)

    def imageFilename(self):
        #server_path = config.get('server.path')
        #return os.path.join(server_path, 'binaries/user-%s' % (self.id))
        return 'binaries/user-%s' % (self.id)

    def save_image(self, prop, value, mimetype='image/png'):
        self.image_mimetype = mimetype
        self.image = value
        self.thumbnail = value
        self.thumbnail_mimetype = mimetype

    def _get_image(self):
        if not os.path.exists(self.imageFilename()):
            return None
        f = open(self.imageFilename())
        v = f.read()
        f.close()
        return v

    def _set_image(self, value):
        image = create_image_preview(StringIO.StringIO(value), height=100, width=100)
        f = open(self.imageFilename(), 'w')
        f.write(image.read())
        self.modified = datetime.now()
        f.close()

    def _set_thumbnail(self, value):
        image = create_image_preview(StringIO.StringIO(value), height=40, width=40)
        f = open(self.imageFilename()+'_thumb', 'w')
        f.write(image.read())
        f.close()

    def _get_thumbnail(self):
        if not os.path.exists(self.imageFilename()+'_thumb'):
            if self.image:
                self.thumbnail = self.image
                self.thumbnail_mimetype = self.image_mimetype
            else:
                return None
        f = open(self.imageFilename()+'_thumb')
        v = f.read()
        f.close()
        return v

    def _get_permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    def _set_password(self, cleartext_password):
        "Runs cleartext_password through the hash algorithm before saving."

        hash = identity.encrypt_password(cleartext_password)
        self.unix_hash = md5crypt.md5crypt(cleartext_password,self.get_salt())
        self.lanman_hash,self.nt_hash = smbpasswd.hash(cleartext_password) 
        self._SO_set_password(hash)

    def get_salt(self):
        r = str(random.randint(0,sys.maxint) + time.time())
        return md5.md5(r).hexdigest()[:8]
        
    def _set_outstanding(self,amount):
        if amount <=0:
            self.reminder_counter = 0
        self._SO_set_outstanding(amount) 

    def _get_tariff_name(self):
        return hubspace.tariff.get_tariff(self.homeplace.id, self.id, datetime.now(), True).name

    def _get_homeplace_name(self):
        return self.homeplace and self.homeplace.name or ""


listen(create_object_reference, User, RowCreatedSignal)
listen(delete_object_reference, User, RowDestroySignal)

class Selection(SQLObject):
    user = ForeignKey('User', default=None)
    attr_name = StringCol()
    selection = IntCol(default=None)

class UserMetaData(SQLObject):
    """Works the same as Selection above, but for storing free-text properties
    """
    user = ForeignKey('User', default=None)
    attr_name = StringCol()
    attr_value = UnicodeCol(default="")


class ObjectReference(SQLObject):
    """Should delete itself when the Object no longer exists
    """
    object_type = UnicodeCol(default="")
    object_id = IntCol(default=0)
    metadata = MultipleJoin('MetaData', joinColumn='object_ref_id') 
    def _get_object(self):
        return getattr(getmodule(self), self.object_type).get(self.object_id)

    def _set_object(self, obj_tuple):
        """takes a tuple of the form (object_type, object_id)
        """
        existing_object_ref = ObjectReference.select(AND(ObjectReference.q.object_id == obj_tuple[1],
                                                         ObjectReference.q.object_type == obj_tuple[0]))
        try: 
            existing_object_ref[0] #ensure you can't have two references to the same object
            print "existing " + `existing_object_ref[0].id`
        except IndexError:
            print "object_tuple" + ` obj_tuple`
            self.object_type, self.object_id  = obj_tuple



def create_object_reference(kwargs, post_funcs):
    print "object ref created" + kwargs['class'].__name__ +  `kwargs['id']`
    obj_ref = ObjectReference(**{'object': (kwargs['class'].__name__, kwargs['id'])})

def delete_object_reference(instance, post_funcs):
    print "object ref deleted" + `instance`
    obj_ref = ObjectReference.select(AND(ObjectReference.q.object_id == instance.id,
                                         ObjectReference.q.object_type == instance.__class__.__name__))[0]
    obj_ref.destroySelf()

class Page(SQLObject):
    """Page objects which appear in the microsite and render content objects as a whole page or a fragment of html.
Page objects have a foreignkey into the location, which may be equal to None (as is the case with pages on the HubWebsite).
    """
    path_name = UnicodeCol(default="")
    name = UnicodeCol(default="")
    title = UnicodeCol(default="")
    page_type = UnicodeCol(default="PublicSpace") #determines the template used, functions calculated for it (including lists)
    location = ForeignKey('Location', default=None)
    #locale = 'en'
    subtitle = UnicodeCol(default="")
    content = UnicodeCol(default="")
    image = ForeignKey('LocationFiles', default=None) # the id  of the LocationFile
    def _get_image_name(self):
         if self.image:
             return self.image.attr_name
         else:
             return ""



listen(create_object_reference, Page, RowCreatedSignal)
listen(delete_object_reference, Page, RowDestroySignal)


#class PageObjects(SQLObject):
#    """An explicit intermidiate table between pages and metadata (allows firing signals on related joins)
#    """
#    class sqlmeta:
#        table = "page_data"
#    page = ForeignKey('Page', notNull=True, cascade=True)
#    item = ForeignKey('MetaData', notNull=True, cascade=True)


class ListItem(SQLObject):
    """This is used for managing UI navigation lists. We can have multiple lists per location, which are diffentiated by a 'list_name'. Each list begins with the item where previous=None, and can be traversed through next and previous references. ListItems can be active or not, and will be displayed or not accordingly by the gui. 
    """
    list_name = UnicodeCol() #to differentiate multiple lists in the location
    next = ForeignKey('ListItem', default=None)
    previous = SingleJoin("ListItem", joinColumn='next_id')
    location = ForeignKey("Location", default=None)
    object_ref = ForeignKey("ObjectReference", notNull=True, cascade=True)
    def _get_object(self):
        return self.object_ref.object
    def _get_meta_object(self):
        return MetaWrapper(self.object)
    active = IntCol(default=1)


class PublicPlace(SQLObject):
    """This should be referenced by a ListItem or a page
    """
    name = UnicodeCol(default="") #should be forced to be unique - this has to be reported as an error to the user
    description = UnicodeCol(default="")
    image = ForeignKey('LocationFiles', default=None) # the id  of the LocationFile
    def _get_image_name(self):
         if self.image:
             return self.image.attr_name
         else:
             return ""

listen(create_object_reference, PublicPlace, RowCreatedSignal)
listen(delete_object_reference, PublicPlace, RowDestroySignal)
    

class PublicSpace(SQLObject):
    """This should be referenced by a ListItem or a page
    """
    name = UnicodeCol(default="") #should be forced to be unique - this has to be reported as an error to the user
    description = UnicodeCol(default="")
    image = ForeignKey('LocationFiles', default=None) # the id  of the LocationFile
    def _get_image_name(self):
         if self.image:
             return self.image.attr_name
         else:
             return ""

listen(create_object_reference, PublicSpace, RowCreatedSignal)
listen(delete_object_reference, PublicSpace, RowDestroySignal)

class MetaData(SQLObject):
    """object_ref can be a "Location", a "Page", a "PublicSpace", (later a "User"). 

    We need to ensure that object_ref's for existent objects of these types exist. This is taken care of by the "listen" functions above which create object_references for every row, and delete them when the row is deleted. For "Location" we need to create objectReferences for existent locations in a "patch". 

    We need to ensure that when a MetaData object is created that the "object_ref, attr_name combination is "
    """
    object_ref = ForeignKey('ObjectReference', cascade=True)
    attr_name = StringCol()
    attr_value = UnicodeCol(default="")

class LocationMetaData(SQLObject):
    """Mostly used for storing content managed fields for the location's microsite

    Of this data, some should be migrated to Pages, and some should be MetaData on the Page object. Need a map of these attributes to Page attributes / Metadata.

    """
    location = ForeignKey('Location')
    attr_name = StringCol()
    attr_value = UnicodeCol(default="")


##Old
class MicroSiteSpace(SQLObject):
    """Space objects which appear in the microsite
    """
    location = ForeignKey('Location')
    next = ForeignKey('MicroSiteSpace', default=None)
    previous = SingleJoin("MicroSiteSpace", joinColumn='next_id')
    name = UnicodeCol(default="")
    description = UnicodeCol(default="")
    image = ForeignKey('LocationFiles', default=None) # the id  of the LocationFile
    def _get_image_name(self):
         if self.image:
             return self.image.attr_name
         else:
             return ""
    active = IntCol(default=1)


class Alias(SQLObject):
    user = ForeignKey('User', default=None)
    alias_name = UnicodeCol(default=None)

class Permission(SQLObject):
    permission_name = UnicodeCol(length=40, alternateID=True,
                                 alternateMethodName="by_permission_name")
    description = UnicodeCol(length=255,default=None)

    groups = RelatedJoin("Group",
                         intermediateTable="group_permission",
                         joinColumn="permission_id", 
                         otherColumn="group_id")


group_types = ['member_calendar', 'host_calendar', 'extras_quantity', 'extras_one_off', 'archive']
group_type_labels = {'member_calendar': 'Member Calendar Resources',
                     'host_calendar': 'Host Calendar Resources',
                     'extras_quantity': 'Quantity Specified Suggestions',
                     'extras_one_off': 'One-Off Suggestions',
                     'archive': 'Resource Archive',
                     'miscellaneous': 'Miscellaneous'}
group_types_descriptions = {'member_calendar': 'Time-based Resources in this group will be grouped together in the booking calendar for members',
                            'host_calendar': 'Time-based resources in this group will be grouped together in the booking calendar in a special group only viewable by hosts e.g. "time spent in the Hub" (measured by rfid card system)',
                            'extras_quantity': 'Resources in the group when added as an suggestions to a resource booking, will be entered with a form field specifying the quantity of the resource that should be booked. e.g. 10 cups of coffes, 5 lunches',
                            'extras_one_off': 'Resources in the group when added as an additional item to a resource booking, will be entered with a tick box allowing the user to book this as a one-off extra',
                            'archive': 'Place to put resources no longer in use',
                            'miscellaneous': ''}

class Resourcegroup(SQLObject):
    name = UnicodeCol(length=200)
    description = UnicodeCol(default=None)
    group_type = EnumCol(enumValues=group_types, default='member_calendar')
    location = ForeignKey("Location", default=None)
    resources = MultipleJoin("Resource", joinColumn="resgroup_id")
    resources_order = PickleCol(default=[],length=2**16+1)
    def _get_resources_order(self):
        val = self._SO_get_resources_order()
        if not val:
            return []
        return val


class Resource(SQLObject):
    name = UnicodeCol(length=200)
    place = ForeignKey("Location", default=None)
    resgroup = ForeignKey("Resourcegroup", default=None)
    type = EnumCol(enumValues=resource_types, default='other')
    tariff_for = MultipleJoin("Pricing",joinColumn='tariff_id')
    default_tariff_for = MultipleJoin("Location",joinColumn='defaulttariff_id')
    prices = MultipleJoin("Pricing", joinColumn="resource_id")
    usages = MultipleJoin("RUsage", joinColumn='resource_id')

    #access policies for 'members' on this tariff (if the resource is a tariff)
    access_policies = MultipleJoin('AccessPolicy', joinColumn="tariff_id")
    
    vat = FloatCol(default=None)
    description = UnicodeCol(default=None)
    active = IntCol(default=1)
    time_based = IntCol(default=0)
    suggestions = RelatedJoin('Resource', intermediateTable='resource_suggestions',
                              joinColumn='suggesting_id',otherColumn='suggested_id',
                              addRemoveName='Suggestion')
    requires = RelatedJoin('Resource', intermediateTable='resource_dependencies',
                           joinColumn='dependend_id',otherColumn='required_id',
                           addRemoveName='Requirement')
    suggestedby = RelatedJoin('Resource', intermediateTable='resource_suggestions',
                              joinColumn='suggested_id',otherColumn='suggesting_id',
                              addRemoveName='Suggestedby')
    requiredby = RelatedJoin('Resource',
                             intermediateTable='resource_dependencies',
                             joinColumn='required_id',otherColumn='dependend_id',
                             addRemoveName='Requiredby')

    resimage_mimetype=UnicodeCol(default=None)

    def save_resimage(self, prop, value,mimetype='image/png'):
        self.resimage_mimetype = 'image/png'
        self.resimage = value

    def _get_resimage(self):
        if not os.path.exists(self.imageFilename('resimage')):
            return None
        f = open(self.imageFilename('resimage'))
        v = f.read()
        f.close()
        return v

    def _set_resimage(self, value):
        image = create_image_preview(StringIO.StringIO(value), height=150, width=230)
        f = open(self.imageFilename('resimage'), 'w')
        f.write(image.read())
        f.close()

    def imageFilename(self, prop):
        #server_path = config.get('server.path')
        #return os.path.join(server_path, 'binaries/location-%s-%s' % (prop, self.id))
        return 'binaries/resource-%s-%s' % (prop, self.id)

class LocationFiles(SQLObject):
    location = ForeignKey("Location", default=None)
    space = MultipleJoin('PublicSpace', joinColumn='image_id') #use ObjectRefences
    page = MultipleJoin('Page', joinColumn='image_id')         #use ObjectRefences
    attr_name = UnicodeCol(length=50)
    mime_type = UnicodeCol(length=20)

class Location(SQLObject):
    resourcegroup_order = PickleCol(default=[],length=2**16+1)
    def _get_resourcegroup_order(self):
        val = self._SO_get_resourcegroup_order()
        if not val:
            return []
        return val

    is_region = IntCol(default=0)
    in_region = ForeignKey('Location', default=None)
    has_hubs = MultipleJoin("Location", joinColumn="in_region_id")
    invoice_newscheme = IntCol(default=1)
    tentative_booking_enabled = IntCol(default=1)
    resourcegroups = MultipleJoin("Resourcegroup", joinColumn="location_id")
    name = UnicodeCol(length=200,alternateID=True, unique=True)
    city = UnicodeCol(length=40,alternateID=True, unique=True)
    currency = UnicodeCol(length=3)
    locale = UnicodeCol(length=8, default="en")
    timezone = UnicodeCol(length=100, default='Europe/London')
    calendar = ForeignKey('Resource', default=None)
    # use this to change result of datetime.now
    vat_default = FloatCol(default=0)
    billing_address = UnicodeCol(default=None)
    company_no = UnicodeCol(default=None)
    #we can use this for creating a new view onto the system
    url = UnicodeCol(default=None, unique=True) #might need to patch the db for this to take effect
    telephone = UnicodeCol(default=None)
    vat_no = UnicodeCol(default=None)
    bank = UnicodeCol(default=None)
    account_no = UnicodeCol(default=None)
    sort_code = UnicodeCol(default=None)
    iban_no = UnicodeCol(default=None)
    swift_no = UnicodeCol(default=None)
    payment_terms = UnicodeCol(default=None)
    invoice_duedate = IntCol(default=0)
    defaulttariff = ForeignKey("Resource", default=None)
    groups = MultipleJoin("Group",joinColumn='place_id')
    resources = MultipleJoin("Resource",joinColumn='place_id')
    homemembers = MultipleJoin('User',joinColumn='homeplace_id')
    invoices = MultipleJoin("Invoice",joinColumn='location_id')
    vat_included = IntCol(default=1)
    rfid_enabled = IntCol(default=0)
    messages = PickleCol(default={}, length=2**16+1)
    def _get_messages(self):
        val = self._SO_get_messages()
        if not val:
            return {}
        return val

    microsite_active = IntCol(default=0)
    homepage_title = UnicodeCol(default=u"")
    homepage_description = UnicodeCol(default=u"")
    holidays = PickleCol(default=[], length=2**16+1)
    def _get_holidays(self):
        val = self._SO_get_holidays()
        if not val:
            return []
        return val
    cancellation_charges = PickleCol(default=[], length=2**16+1) #dictionary of time periods and corresponding charges
    def _get_cancellation_charges(self):
        val = self._SO_get_cancellation_charges()
        if not val:
            return []
        return val

    #We need to be able to specify particular days when hubs are closed/open or have different opening times to normal (probably). What would be the best way of doing this? One way would be to have a table with two columns dates and corresponding opening times. Perhaps only for those dates that dont just use the default opening times specified here.
    #two tables - 1. location, day_of_the_week, start_time, end_time(not datetime)
    #             2. location, date, start_time, end_time
    
    def imageFilename(self, prop):
        #server_path = config.get('server.path')
        #return os.path.join(server_path, 'binaries/location-%s-%s' % (prop, self.id))
        return 'binaries/location-%s-%s' % (prop, self.id)

    logo_mimetype=UnicodeCol(default=None)
    invlogo_mimetype=UnicodeCol(default=None)
    homelogo_mimetype=UnicodeCol(default=None)

    def save_logo(self, prop, value,mimetype='image/png'):
        self.logo_mimetype = 'image/png'
        self.logo = value

    def _get_logo(self):
        if not os.path.exists(self.imageFilename('logo')):
            return None
        f = open(self.imageFilename('logo'))
        v = f.read()
        f.close()
        return v

    def _set_logo(self, value):        
        image = create_image_preview(StringIO.StringIO(value), height=87, width=850)
        f = open(self.imageFilename('logo'), 'w')
        f.write(image.read())
        f.close()

    def save_invlogo(self, prop, value,mimetype='image/png'):
        self.invlogo_mimetype = 'image/png'
        self.invlogo = value

    def _get_invlogo(self):
        if not os.path.exists(self.imageFilename('invlogo')):
            return None
        f = open(self.imageFilename('invlogo'))
        v = f.read()
        f.close()
        return v

    def _set_invlogo(self, value):
        image = create_image_preview(StringIO.StringIO(value), height=130, width=690)
        f = open(self.imageFilename('invlogo'), 'w')
        f.write(image.read())
        f.close()

    def save_homelogo(self, prop, value,mimetype='image/png'):
        self.homelogo_mimetype = 'image/png'
        self.homelogo = value

    def _get_homelogo(self):
        if not os.path.exists(self.imageFilename('homelogo')):
            return None
        f = open(self.imageFilename('homelogo'))
        v = f.read()
        f.close()
        return v

    def _set_homelogo(self, value):
        image = create_image_preview(StringIO.StringIO(value), height=113, width=850)
        f = open(self.imageFilename('homelogo'), 'w')
        f.write(image.read())
        f.close()
    
    def getHostsEmail(self):
        return self.name.lower().replace(' ', '') + ".hosts@the-hub.net"

    hosts_email = property(getHostsEmail)


listen(create_object_reference, Location, RowCreatedSignal)
listen(delete_object_reference, Location, RowDestroySignal)


class MetaWrapper(object):
    def __init__(self, obj):
        self.__dict__['obj'] = obj

    def __getattr__(self, name):
 	if hasattr(self.obj, name): 
            return getattr(self.obj, name)
        else:
            try:
                 return MetaData.select(AND(MetaData.q.object_refID == ObjectReference.q.id,
                                            ObjectReference.q.object_id == self.obj.id,
                                            ObjectReference.q.object_type == self.obj.__class__.__name__,
                                            MetaData.q.attr_name == name))[0].attr_value
            except IndexError:
                 return ""
 

    def __setattr__(self, name, value) :
 	if hasattr(self.obj, '_set_' + name) or hasattr(self.obj, '_set_' + name + 'ID'):
            #needs to be secured so that only explicity editable attributes are settable
            return setattr(self.obj, name, value) 
        else:
            try:
                prop = MetaData.select(AND(MetaData.q.object_refID == ObjectReference.q.id,
                                           ObjectReference.q.object_id == self.obj.id,
                                           ObjectReference.q.object_type == self.obj.__class__.__name__,
                                           MetaData.q.attr_name == name))[0]
                prop.attr_value = value

            except IndexError:
                ref = ObjectReference.select(AND(ObjectReference.q.object_id == self.obj.id,
                                                 ObjectReference.q.object_type == self.obj.__class__.__name__))[0]
                prop = MetaData(object_refID = ref,
                                attr_name = name,
                                attr_value = value)
  






class PolicyGroup(SQLObject):
    """A list of users given a freeform name, to which Access policies get assigned.
    """
    name = UnicodeCol(default=u"")
    description = UnicodeCol(default=u"")
    place = ForeignKey("Location")
    users = RelatedJoin('User',
                        intermediateTable='user_policy_group',
                        joinColumn='policygroup_id',
                        otherColumn='user_id',
                        createRelatedTable=False)
    access_policies = MultipleJoin('AccessPolicy', joinColumn="policygroup_id")    
    
class AccessPolicy(SQLObject):
    """An Access Policy is a set of Open times which get assigned to a user through the group (role), tariff, or special policyGroup.
    """
    location = ForeignKey('Location') #add tbese two to Policy Creation scripts
    precedence = IntCol(default=5) 
    policy_resource = ForeignKey('Resource')
    #note a user may have multiple group accessPolcies - in this case the openTimes should be additive to determine whether the user can come in.
    #an AccessPolicy should be associated with *either* a group a tariff or a policy group
    group = ForeignKey('Group', default=None) #member, host, director
    #tariff, if the Open times are of the same type as those in the group, they should override
    #tariff, policies should not apply to hosts or directors
    #initially 'appear' to inherit from group-member policy 
    tariff = ForeignKey('Resource', default=None)
    #should be applied with care, times here will override other policies and can not 'inherit' from elsewhere since users in a policy group are not a strict subset
    policygroup = ForeignKey('PolicyGroup', default=None)  
    #A User can have multiple access policies e.g. from role/group, from tariff, from user
    #policies are additive "allow" policies, if one of a users policies let them in - then they can come in.
    #ALTER TABLE accesspolicy ADD CONSTRAINT location_id_policy_name_key UNIQUE (location_id, policy_name);
    open_times = MultipleJoin('Open', joinColumn='policy_id')
    policyStartDate = DateCol(default=None)
    policyEndDate = DateCol(default=None)

       
class Open(SQLObject):
    policy = ForeignKey('AccessPolicy')
    openTimeStartDate = DateCol(default=None) # date from which openTimeDay applies
    openTimeDay = IntCol(default=None) #0-6 == Mon-Sun, 7==Holiday
    openTimeDate = DateCol(default=None) # specific date
    openTimeStart = TimeCol() 
    openTimeEnd = TimeCol()

class Pricing(SQLObject):
    resource = ForeignKey("Resource")
    tariff = ForeignKey("Resource")
    cost = CurrencyCol()
    periodstarts = DateTimeCol(default=datetime(1970, 1, 1))
    nextperiod = ForeignKey("Pricing", default=None)
    periodends = DateTimeCol(default=datetime(9999, 1, 1))
    def _get_periodends(self):
        if self.nextperiod == None:
            ends = datetime(9999, 1, 1)
        else:
            ends = self.nextperiod.periodstarts
        self._SO_set_periodends(ends)
        return ends
     
    ##when change pricing, recalculate cost for rusages associated with tariff and resource


class RUsage(SQLObject):
    user = ForeignKey("User")
    resource = ForeignKey("Resource")
    tariff = ForeignKey("Resource", default=None)
    date_booked = DateTimeCol(default=None)
    start = DateTimeCol()
    end_time = DateTimeCol(default=None)
    quantity = IntCol(default=1)
    def _isInvoiced(self):
        return bool(self.invoice and self.invoice.sent)
    invoiced = property(_isInvoiced)
    def _get_duration_or_quantity(self):
        return self.resource.time_based and self.end_time - self.start or self.quantity
    duration_or_quantity = property(_get_duration_or_quantity)
    cost=CurrencyCol(default=0)
    customcost = CurrencyCol(default=None)
    def _get_effective_cost(self): # to avoid mistakes like 1. usage.customcost or usage.cost (problem if former is 0) and 2. to serve as a shortcut
        return self.customcost if self.customcost is not None else self.cost
    effectivecost = property(_get_effective_cost)
    resource_name = UnicodeCol(length=200)
    resource_description = UnicodeCol(default=None)
    new_resource_description = UnicodeCol(default=None)
    bookedby = ForeignKey("User", default=None)
    invoice = ForeignKey("Invoice",default=None)
    usagesuggestedby = ForeignKey('RUsage', default=None)
    #should read "usages suggested and booked as a result"
    suggested_usages = MultipleJoin('RUsage', joinColumn='usagesuggestedby_id')
    meeting_name = UnicodeCol(default=None)
    meeting_description = UnicodeCol(default=None)
    number_of_people = IntCol(default=1)
    notes = UnicodeCol(default=None)
    public_field = IntCol(default=0)
    confirmed = IntCol(default=1)
    cancelled = IntCol(default=0)
    refund = IntCol(default=0)
    refund_for = IntCol(default=None)
    keys_cant_change_if_invoiced = ('start', 'end_time', 'userID', 'cost', 'customcost')
    _codetmpl = """\
def _set_%(name)s(self, val):
    if hasattr(self, 'id') and self.invoiced:
        hint = _("The action you are trying to undertake involves modification to invoice %%s. Since the invoice has already been sent no further modifications can take place and the system has rejected the changes.") %% self.invoice.number
        raise hubspace.errors.ErrorWithHint(hint)
    else:
        self._SO_set_%(name)s(val) """

    for name in keys_cant_change_if_invoiced:
        x = _codetmpl % dict(name = name)
        exec(x)
    del _codetmpl

    def __str__(self):
        return "RUsage: %s, user: %s Resource:%s (%s-%s)" % (self.id, self.user.user_name, self.resource.name, self.start, self.end_time)

class Invoice(SQLObject):
    """An Invoice. A collection of rusages, collected on a specific date for a specific
    user."""
    number = IntCol(default=None)
    def _get_number(self):
        return self._SO_get_number() or "H%s" % self.id
    billingaddress = UnicodeCol()
    user = ForeignKey("User")
    start = DateTimeCol()
    end_time = DateTimeCol()
    created = DateTimeCol(default=datetime.now)
    sent = DateTimeCol(default=None)
    #paid = BoolCol(default=False)
    #reminder_count = IntCol(default=0)
    rusages = MultipleJoin("RUsage",joinColumn='invoice_id')
    amount = CurrencyCol(default=0)
    def _set_amount(self, amount):
        if not self.sent or not self.amount:
            self._SO_set_amount(amount)
        else:
            raise ValueError
    total_tax = CurrencyCol(default=0)
    def _set_total_tax(self, tax):
        if not self.sent or self.total_tax == None:
            self._SO_set_total_tax(tax)
        else:
            raise ValueError
    resource_tax_dict = PickleCol(length=2**16+1, default={})
    def _set_resource_tax_dict(self, tax_dict):
        if not self.sent or not self.resource_tax_dict:
            self._SO_set_resource_tax_dict(tax_dict)
        else:
            raise ValueError
    vat_included = IntCol(default=1)
    def _set_vat_included(self, included):
        if not self.sent or self.vat_included==None:
            self._SO_set_vat_included(included)
        else:
            raise ValueError
    location = ForeignKey('Location')
    def __str__(self):
        return "Invoice id: %s, number %s, user: %s %s" % (self.id, self.number, self.user.user_name, str([r.id for r in self.rusages]))

def findNumberMissing(start, l):
    """
    >>> test_data = (
    >>>                 (100, [55, 70, 75], 75),
    >>>                 (20, [3], 3),
    >>>                 (1000, [175, 678], 678),
    >>>                 (99, [], None),
    >>>                 (9, [7], 7),
    >>>                 (9, [9], 9), # invalid case as even after removing 9 list is still in order and not missing any number 
    >>>             )
    >>> for data in test_data:
    >>>     max_no, missings, exp_ret = data
    >>>     l = range(1, (max_no + 1))
    >>>     for m in missings:
    >>>         l.remove(m)
    >>>     print exp_ret, print findNumberMissing(l)
    75, 75
    3, 3
    678, 678
    None, None
    7, 7
    9, None
    >>> l = [120000001, 120000002, 120000003, 120000004, 120000005, 120000006, 120000007, 120000008, 120000009, 120000011, 120000012, 120000013, 120000014, 120000015, 120000016, 120000017, 120000018, 120000019, 120000020, 120000021, 120000022]
    >>> print findNumberMissing(l)
    120000010
    >>> print findNumberMissing([140000001, 140000002, 140000003, 140000005])
    140000004
    """
    start = start
    end = max(l) + 1
    linear = set(range(start, end))
    missings = list(linear.difference(l))
    if missings:
        return missings[0]

def setInvoiceNumber(kwargs, post_funcs):
    instance = kwargs['class'].get(kwargs['id'])
    location_id = instance.location.id
    if instance.location.invoice_newscheme:
        # do we need to acquire a lock here? why?
        inv_all = list(Invoice.select(Invoice.q.locationID == location_id, orderBy='created').reversed())
        # Above query may slow down things a bit, however with difficulties of producing right query as we have
        # two different invoicing numbering with ORM on top, I prefer slower but cleaner approach. Ideally I wanted to
        # step through smaller blocks
        inv_numbers = sorted([i.number for i in inv_all if isinstance(i.number, int)])
        start = int("%s0000001" % instance.location.id)
        if inv_numbers:
            next_num = findNumberMissing(start, inv_numbers)
            if not next_num:
                next_num = max(inv_numbers) + 1
        else:
            next_num = start
        def f(inv):
            inv.number = next_num
        post_funcs.append(f)


listen(setInvoiceNumber, Invoice, RowCreatedSignal)

class Note(SQLObject):
    title = UnicodeCol(length=200)
    body = UnicodeCol()
    date = DateTimeCol()
    onuser = ForeignKey("User")
    byuser = ForeignKey("User")
    action = ForeignKey("Todo", default=None)

class Todo(SQLObject):
    body = UnicodeCol(default=None)
    action = UnicodeCol(default="edit")
    action_id = IntCol(default=0)
    subject = UnicodeCol(length=200)
    foruser = ForeignKey("User")
    createdby = ForeignKey("User")
    opened = DateTimeCol()
    due = DateTimeCol(default=None)
    closed = DateTimeCol(default=None)
    parent = ForeignKey("Todo", default=None)
    children = MultipleJoin('Todo', joinColumn='parent_id')

class Report(SQLObject):
    owner = ForeignKey("User")
    generated_on = DateTimeCol(default=datetime.now)
    rtype = EnumCol(enumValues=graph_types)
    start_date = DateTimeCol(default=None)
    end_date = DateTimeCol(default=None)
    grpby = StringCol()
    records_filter = PickleCol(default=dict())
    def _get_records_filter(self):
        val = self._SO_get_records_filter()
        if not val:
            return {}
        return val

class MessageCustomization(SQLObject):
    message = UnicodeCol()
    location = ForeignKey("Location")
    lang = StringCol(default=None)
    text = UnicodeCol()

class ResourceQueue(SQLObject):
    foruser = ForeignKey("User")
    rusage = ForeignKey("RUsage")

# Create missing tables
for sobj in [MessageCustomization]:
    sobj.createTable(ifNotExists=True)
