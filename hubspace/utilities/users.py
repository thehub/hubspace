import turbolucene
from hubspace.model import User, Location
from hubspace.utilities.permissions import user_locations
from turbogears import identity
from sqlobject import AND
from hubspace.utilities.dicts import ODict
import hubspace.tariff
from hubspace.utilities.uiutils import now
###################  Members  ###################

fields = ODict()
for k,v in (
    #("active", dict (label = "Active", value = "active", checked = "checked")),
    ("display_name", dict (label = "Name", value = "display_name", checked = "checked")),
    ("homeplace_name", dict (label = "Location", value = "homeplace_name", checked = "checked")),
    ("tariff_name", dict (label = "Tariff", value = "tariff_name", checked = "checked")),
    ("email_address", dict (label = "Email", value = "email_address", checked = "checked")),
    ("work", dict (label = "Work Phone", value = "work")),
    ("mobile", dict (label = "Mobile", value = "mobile")),
    ("website", dict (label = "Website", value = "website")),
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
    if override_user:
        user_locs = Location.select()
    else:
        user_locs = user_locations(identity.current.user)

    if location:
        users = set()
        users = set(User.select("""active = %s AND
                                   homeplace_id = %s"""%(1, location.id)))
        if not active_only: # get inactive users from the hosts locations
            if location in user_locs:
	        users = users.union(set(User.select(AND(User.q.active in [None, 0],
                                                        User.q.homeplaceID==location.id))))
    else:
        users = set(User.selectBy(active=1))
        if not active_only: # get inactive users from the hosts locations
            for loc in user_locs:
                users = users.union(set(User.select(AND(User.q.active in [None, 0], User.q.homeplaceID==loc.id))))
        
    users = filter_by_text(users, text_filter, type)
    if start != None and end != None:
        users = users[start:end]
    try:
        webapi = User.selectBy(first_name="web", last_name="api")[0]
        if webapi in users and not identity.has_permission("superuser"):
            users.remove(webapi)
    except:
        pass
    return users
