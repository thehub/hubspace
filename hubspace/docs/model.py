from datetime import datetime

from sqlobject import *

from turbogears import identity 
from turbogears.database import PackageHub

hub = PackageHub("hub_admin")
__connection__ = hub

# class YourDataClass(SQLObject):
#     pass

class Hub(SQLObject):
	name = StringCol(length=255)
	address = StringCol()
	server_url = StringCol(length=255)
	web_address = StringCol(length=255)
	phone = StringCol(length=255)
	fax = StringCol(length=255)
	main_contact = ForeignKey('User')

class Tariff(SQLObject):
	name = StringCol(length=255)
	cost_pcm = CurrencyCol()
	included_mins = IntCol()
	meeting_space_cost = CurrencyCol()
	start_date = DateCol()

class UserNotes(SQLObject):
	user = ForeignKey('User')
	creator = ForeignKey('User')
	date = DateTimeCol()
	note = StringCol()

class TextMeta(SQLObject):
	user = ForeignKey('User')
	creator = ForeignKey('User')
	text = StringCol(length=1000)
	date = DateTimeCol()

class PrintJob(SQLObject):
	user = ForeignKey('User')
	printer = ForeignKey('Printer')
	date = DateCol()
	job_name = StringCol(length=255)
	job_id = StringCol(length=255)
	toner_c = FloatCol()
	toner_m = FloatCol()
	toner_y = FloatCol()
	toner_k = FloatCol()
	pages = IntCol()
	size = EnumCol(enumValues=['a4','a3'])
	invoice = ForeignKey('Invoice')

class Printer(SQLObject):
	hub = ForeignKey('Hub')
	name = StringCol(length=255)
	a3_colour_cost = CurrencyCol()
	a3_bw_cost = CurrencyCol()
	a4_colour_cost = CurrencyCol()
	a4_bw_cost = CurrencyCol()

class ResourceLineType(SQLObject):
	name = StringCol(length=255)
	cost = CurrencyCol()
	description = StringCol(length=255)

class ResourceLine(SQLObject):
	user = ForeignKey('User')
	resource_type = ForeignKey('ResourceLineType')
	description = StringCol(length=255)
	cost = CurrencyCol()
	hub = ForeignKey('Hub')
	invoice = ForeignKey('Invoice')
	creator = ForeignKey('User')

class Space(SQLObject):
	hub = ForeignKey('Hub')
	name = StringCol(length=255)
	description = StringCol()

class SpaceBookings(SQLObject):
	user = ForeignKey('User')
	space = ForeignKey('Space')
	time_start = DateTimeCol()
	time_end = DateTimeCol()
	projector = ForeignKey('Projector')
	refreshments = ForeignKey('Refreshment')
	invoice = ForeignKey('Invoice')
	creator = ForeignKey('User')

class Projector(SQLObject):
	user = ForeignKey('User')
	booking_time_start = DateTimeCol()
	booking_time_end = DateTimeCol()
	hub = ForeignKey('Hub')
	invoice = ForeignKey('Invoice')
	creator = ForeignKey('User')

class Refreshment(SQLObject):
	user = ForeignKey('User')
	description = StringCol(length=255)
	cost = CurrencyCol()
	booking_time = DateTimeCol()
	hub = ForeignKey('Hub')
	invoice = ForeignKey('Invoice')
	creator = ForeignKey('User')

class SpaceLog(SQLObject):
	user = ForeignKey('User')
	time_in = DateTimeCol()
	time_out = DateTimeCol()
	hub = ForeignKey('Hub')

class Invoice(SQLObject):
	user = ForeignKey('User')
	sent_to_user = ForeignKey('User')
	invoice_no = IntCol()
	time_sent = DateTimeCol()
	total = CurrencyCol()
	due_date = DateCol()
	paid_date = DateCol()
	notes = StringCol(length=1000)
	creator = ForeignKey('User')

class Visit(SQLObject):
    class sqlmeta:
        table="visit"

    visit_key= StringCol( length=40, alternateID=True,
                          alternateMethodName="by_visit_key" )
    created= DateTimeCol( default=datetime.now )
    expiry= DateTimeCol()

    def lookup_visit( cls, visit_key ):
        try:
            return cls.by_visit_key( visit_key )
        except SQLObjectNotFound:
            return None
    lookup_visit= classmethod(lookup_visit)

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
        table="tg_group"
    
    group_name = UnicodeCol(length=16, alternateID=True,
                            alternateMethodName="by_group_name")
    display_name = UnicodeCol(length=255)
    created = DateTimeCol(default=datetime.now)

    # collection of all users belonging to this group
    users = RelatedJoin("User", intermediateTable="user_group",
                        joinColumn="group_id", otherColumn="user_id")

    # collection of all permissions for this group
    permissions = RelatedJoin("Permission", joinColumn="group_id", 
                              intermediateTable="group_permission",
                              otherColumn="permission_id")


class User(SQLObject):
    """
    Reasonably basic User definition. Probably would want additional attributes.
    """
    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table="tg_user"

    user_name = UnicodeCol(length=16, alternateID=True,
                           alternateMethodName="by_user_name")
    email_address = UnicodeCol(length=255, alternateID=True,
                               alternateMethodName="by_email_address")
    display_name = UnicodeCol(length=255)
    password = UnicodeCol(length=40)
    created = DateTimeCol(default=datetime.now)

    # groups this user belongs to
    groups = RelatedJoin("Group", intermediateTable="user_group",
                         joinColumn="user_id", otherColumn="group_id")
                         
    hubs = RelatedJoin('Hub')

    def _get_permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
        
    def _set_password(self, cleartext_password):
        "Runs cleartext_password through the hash algorithm before saving."
        hash = identity.encrypt_password(cleartext_password)
        self._SO_set_password(hash)
        
    def set_password_raw(self, password):
        "Saves the password as-is to the database."
        self._SO_set_password(password)



class Permission(SQLObject):
    permission_name = UnicodeCol(length=16, alternateID=True,
                                 alternateMethodName="by_permission_name")
    description = UnicodeCol(length=255)
    
    groups = RelatedJoin("Group",
                        intermediateTable="group_permission",
                         joinColumn="permission_id", 
                         otherColumn="group_id")


