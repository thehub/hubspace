import hubspace.search
from hubspace.model import User, Location, UserGroup, Group
from hubspace.utilities.permissions import user_locations
from turbogears import identity
from sqlobject import AND, LIKE, IN, OR
from hubspace.utilities.dicts import ODict
import hubspace.tariff
from hubspace.utilities.uiutils import now

class iLIKE(LIKE):
    op = 'ilike'
###################  Members  ###################

fields = ODict()
for k,v in (
    ("id", dict (label = "Membership no.", value = "id", checked = "checked")),
    ("active", dict (label = "Active", value = "active")),
    ("display_name", dict (label = "Name", value = "display_name", checked = "checked")),
    ("homeplace_name", dict (label = "Location", value = "homeplace_name", checked = "checked")),
    ("tariff_name", dict (label = "Tariff", value = "tariff_name")),
    ("email_address", dict (label = "Email", value = "email_address", checked = "checked")),
    ("organisation", dict (label = "Organisation", value = "organisation")),
    ("address", dict (label = "Address", value = "address")),
    ("mobile", dict (label = "Mobile", value = "mobile")),
    ("work", dict (label = "Work Phone", value = "work")),
    ("fax", dict (label = "Fax", value = "fax")),
    ("skype_id", dict (label = "Skype ID", value = "skype_id")),
    ("website", dict (label = "Website", value = "website")),
    ("public_field", dict (label = "Public Profile", value = "public_field", field_type = "bool")),
    ):
    fields[k] = v

def alpha(user1, user2):
    if user1.display_name > user2.display_name:
        return 1
    else:
        return -1

def order_members(members):
    x = list(members)
    x.sort(alpha)
    return x


def filter_by_text(users, text_filter, type):
    if type=='fulltext_member_search':
        results = turbolucene.search(text_filter, 'en')
        try:
            #sqlobject 0.9 doesn't implement NOT on 'SelectResults', and so throws a not implemented error
            #so normally we should use .count()==0
            #however if there are no results turbolucene returns None 
            if not results:
                return []
        except:
            pass #we have results
        return order_members([user for user in results if user in users])

    if type=='member_search':

        filtered_users = []
        for user in users:
             matches = user.display_name.lower().split(' ')
             matches.append(user.display_name.lower())
             for word in matches:
                 if word.startswith(text_filter.lower()):
                     filtered_users.append(user)
                     break
        return order_members(filtered_users)

    if type=='rfid_member_search':
        return User.select(AND(User.q.rfid == text_filter))


def filter_members(location, text_filter, type, active_only, start, end, override_user=None):

    if type == "member_search":

        text_filter = "%" + " ".join(text_filter.split()).replace("'","\\'") + "%"

        if override_user:
            user_locs = Location.select()
        else:
            user_locs = user_locations(identity.current.user)

        if location:
            users = list(User.select("homeplace_id = %s AND display_name ilike '%s' order by display_name" % (location.id, text_filter)))
            if active_only:
                users = [user for user in users if user.active]
            else:
                if location not in user_locs:
                    users = [user for user in users if user.active]
        else:
            relevant_groups = Group.select(AND(Group.q.level=='member', IN(Group.q.place, user_locs)))
            relevant_user_ids = tuple((ug.userID for ug in UserGroup.select(IN(UserGroup.q.group, tuple(relevant_groups)))))
            display_name_clause = iLIKE(User.q.display_name, text_filter)
            user_id_clause = IN(User.q.id, relevant_user_ids)
            if active_only:
                myloc_ids = [loc.id for loc in user_locs]
                user_active_clause = OR((User.q.active == 1), IN(User.q.homeplaceID, myloc_ids))
                users = User.select(AND(user_id_clause, display_name_clause, user_active_clause))
            else:
                users = User.select(AND(user_id_clause, display_name_clause))
            users = users.orderBy('display_name')

    elif type == 'rfid_member_search':
            users = User.select(AND(User.q.rfid == text_filter))

    elif type == 'fulltext_member_search':
            users = hubspace.search.do_search(text_filter)

    if start != None and end != None:
        users = users[start:end]

    try:
        webapi = User.selectBy(first_name="web", last_name="api")[0]
        if webapi in users and not identity.has_permission("superuser"):
            users.remove(webapi)
    except:
        pass
    return users
