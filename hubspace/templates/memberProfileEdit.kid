<?python
from hubspace.utilities.uiutils import oddOrEven, print_error, get_freetext_metadata, selected_single
from hubspace.utilities.dicts import AttrDict
from hubspace.controllers import get_place, permission_or_owner, roles_grantable
from hubspace.model import Location, User, Group
from turbogears import identity
import itertools as it

oddness = oddOrEven()
tg_errors = None

def get_aliases(object):
	try:
		return object.aliases
	except:
		return []

def new_aliases(object):
        try:
               return object.new_alias
        except:
               return ""

def checked(user, attr):
    if getattr(user, attr):
        return {'checked':'checked'}
    return {}
def alpha(a, b):
   if a.name > b.name:
      return 1
   return -1

def locations(object):
    #superuser gets all locations
    if identity.has_permission('superuser'):
        return Location.select(orderBy='name')

    #if current user has permission 'add_members' in a location let em set that location as homeplace for any user and let em add any user as a member and add any appropriate permissions to there level. 
    locations = []
    for group in identity.current.user.groups:
        location = get_place(group)
        if location:
            if permission_or_owner(location, location, 'add_members') and location not in locations:
                locations.append(location)

    #if the user being edited is a member of any locations - then anyone who can edit their profile choose those options as the homeplace - e.g. themselves. Beware, it is possible to change another users homeplace, so that you can no longer edit there profile.
    if not hasattr(object, 'groups'):
        return locations 
    for group in object.groups:
        location = get_place(group)
        if location and location not in locations:
                locations.append(location)
    locations.sort(alpha)
    return locations
  


def current_home(location, user):
    if hasattr(user, 'homeplace') and not isinstance(user.homeplace, basestring):
        if user.homeplace.id == location.id:
            return {'checked':'checked'}
    elif identity.current.user.homeplace.id == location.id:
        return {'checked':'checked'}
    return {} 

def is_london_user(user):
    if hasattr(user, 'homeplace') and isinstance(user.homeplace, Location):
        if user.homeplace.id == 1 and permission_or_owner(user.homeplace, None, 'manage_users'):
            return True
    return False

def has_role(user, location, level):
    if not hasattr(user, 'groups'):
        return False
    for group in user.groups:
        if group.place==location and group.level==level:
            return True
    return False

def role_selected(user, location, level):
    if has_role(user, location, level):
       return {'checked':'checked'}
    return {}


roles = ('member', 'host', 'director')
add_role_perms = ['add_' + role + 's' for role in roles]

def get_current_roles(user):
    return dict((loc, tuple(g[1] for g in groups)) for loc, groups in it.groupby(sorted((g.place, g.level) for g in user.groups if g.place), lambda x: x[0]))

def can_edit(editable_roles, location, role):
    if location in editable_roles:
        return ('add_' + role + 's') in editable_roles[location]
    return False

def current_role(current_roles, location, role):
    if location in current_roles:
        return role in current_roles[location]
    return False

def get_location_data(current_roles, editable_roles, location):
    return dict((role, (current_role(current_roles, location, role), can_edit(editable_roles, location, role))) for role in roles)

def get_roles_data(current_roles, editable_roles, locations):
    return dict((location, get_location_data(current_roles, editable_roles, location)) for location in locations)
?>

<div py:strip="True" xmlns:py="http://purl.org/kid/ns#">
    <table py:def="load_memberProfileEdit(object, tg_errors)" cellpadding="0" cellspacing="0" class="memberProfile">
        <tr>
            <td class="photo"></td>
	    <td>
                <table class="memberProfileInner detailTable" cellpadding="0" cellspacing="0">			
                    <tr py:if="permission_or_owner(object.homeplace, None, 'manage_users')" >
                         <td class="line">Active Profile? <span py:strip="True" py:if="not isinstance(object, AttrDict) and not object.welcome_sent">(When a user is first activated, a welcome message will be sent out with the username and password. If the password field is left empty when activating the user, the password will be reset to a random string.)</span></td>
                         <td><input name="active" id="active" type="checkbox" value="1" py:attrs="checked(object, 'active')" /><div class="errorMessage" py:if="tg_errors">${print_error('active', tg_errors)}</div></td>
                    </tr>
                    <tr py:if="permission_or_owner(object.homeplace, object, 'manage_users')" >
                        <td class="line">Show profile on The Hub's public website</td>
                        <td><input name="public_field" id="public_field" type="checkbox" value="1" py:attrs="checked(object, 'public_field')" /><div class="errorMessage" py:if="tg_errors">${print_error('public_field', tg_errors)}</div></td>
                    </tr>
		    <tr>
                        <td class="line">Username</td>
                        <td><input name="user_name" id="user_name" type="text" class="text" value="${object.user_name}"/><div class="errorMessage" py:if="tg_errors">${print_error('user_name', tg_errors)}</div></td>
                    </tr>
                    <tr>
                        <td class="line"></td>
                        <td><em>To change your password enter the new one in the two fields below</em></td>
                    </tr>
                    <tr>
                        <td class="line">Password</td>
                        <td><input name="password" id="password" type="password" class="text" /><div class="errorMessage" py:if="tg_errors">${print_error('password', tg_errors)}</div></td>
                    </tr>
                    <tr>
                        <td class="line">Confirm Password</td>
                        <td><input name="password2" id="password2" type="password" class="text" /><div class="errorMessage" py:if="tg_errors">${print_error('password2', tg_errors)}</div></td>
                    </tr>
                    <tr>
                        <td class="line">First name</td>
                        <td><input name="first_name" id="first_name" type="text" class="text" value="${object.first_name}" /><div class="errorMessage" py:if="tg_errors">${print_error('first_name', tg_errors)}</div></td>
                    </tr>
                    <tr>
                        <td class="line">Last name(s)</td>
                        <td><input name="last_name" id="last_name" type="text" class="text"  value="${object.last_name}" /><div class="errorMessage" py:if="tg_errors">${print_error('last_name', tg_errors)}</div></td>
                    </tr>
                    <tr>
                        <td class="line">Organisation</td>
                        <td><input name="organisation" id="organisation" type="text" class="text"  value="${object.organisation}" /><div class="errorMessage" py:if="tg_errors">${print_error('organisation', tg_errors)}</div></td>
                    </tr>
                    <tr>
                        <td class="line">Role</td>
                        <td><input name="title" id="title" type="text" class="text"  value="${object.title}" /><div class="errorMessage" py:if="tg_errors">${print_error('title', tg_errors)}</div></td>
                    </tr>
                    <tr>
                        <td class="line">Type of business</td>
                        <td><input class="text" id="biz_type" name="biz_type" value="${get_freetext_metadata(object, 'biz_type')}" /><div id="biz_type_complete"></div><span id="indicator" style="display:none;"><img  src="/static/images/timer_2.gif" alt="completing..."/></span><div class="errorMessage" py:if="tg_errors">${print_error('biz_type', tg_errors)}</div></td>
 
                    </tr>
                    <tr>
							<td class="line">Mobile <em>(please include international dialing code)</em></td>
							<td><input name="mobile" id="mobile" type="text" class="text"  value="${object.mobile}" /><div class="errorMessage" py:if="tg_errors">${print_error('mobile', tg_errors)}</div></td>
						</tr>
						<tr>
							<td class="line">Work Phone <em>(please include international dialing code)</em></td>
							<td><input name="work" id="work" type="text" class="text"  value="${object.work}" /><div class="errorMessage" py:if="tg_errors">${print_error('work', tg_errors)}</div></td>
						</tr>
						<tr>
							<td class="line">Home Phone <em>(please include international dialing code)</em></td>
							<td><input name="home" id="home" type="text" class="text"  value="${object.home}" /><div class="errorMessage" py:if="tg_errors">${print_error('home', tg_errors)}</div></td>
						</tr>
						<tr>
							<td class="line">Fax</td>
							<td><input name="fax" id="fax" type="text" class="text"  value="${object.fax}" /><div class="errorMessage" py:if="tg_errors">${print_error('fax', tg_errors)}</div></td>
						</tr>
						<tr>
							<td class="line">Email 1</td>
							<td><input name="email_address" id="email_address" type="text" class="text"  value="${len(object.email_address.split('@', 1))==2 and object.email_address or ''}" /><div class="errorMessage" py:if="tg_errors">${print_error('email_address', tg_errors)}</div></td>
						</tr>
						<tr>
							<td class="line">Email 2</td>
							<td><input name="email2" id="email2" type="text" class="text"  value="${object.email2}" /><div class="errorMessage" py:if="tg_errors">${print_error('email2', tg_errors)}</div></td>
						</tr>
						<tr>
							<td class="line">Email 3</td>
							<td><input name="email3" id="email3" type="text" class="text" value="${object.email3}" /><div class="errorMessage" py:if="tg_errors">${print_error('email3', tg_errors)}</div></td>
						</tr>

						<tr>
							<td class="line">Website</td>
							<td><input name="website" id="website" type="text" class="text" value="${object.website}" /><div class="errorMessage" py:if="tg_errors">${print_error('website', tg_errors)}</div></td>
						</tr>
						<tr  >
							<td class="line">Address</td>
							<td><input name="address" id="address" type="text" class="text"  value="${object.address}" /><div class="errorMessage" py:if="tg_errors">${print_error('address', tg_errors)}</div></td>
						</tr>
						<tr  >
							<td class="line">Postcode</td>
							<td><input name="postcode" id="postcode" type="text" class="text"  value="${get_freetext_metadata(object, 'postcode')}" /><div class="errorMessage" py:if="tg_errors">${print_error('postcode', tg_errors)}</div></td>
						</tr>
						<tr>	
							<td class="line">Internet Phone (SIP id)</td>
							<td><input name="sip_id" id="sip_id" type="text" class="text"  value="${object.sip_id}" /><div class="errorMessage" py:if="tg_errors">${print_error('sip_id', tg_errors)}</div></td>
						</tr>
						<tr>	
							<td class="line">Skype name</td>
							<td><input name="skype_id" id="skype_id" type="text" class="text"  value="${object.skype_id}" /><div class="errorMessage" py:if="tg_errors">${print_error('skype_id', tg_errors)}</div></td>
						</tr>
						

						<tr py:if="is_london_user(object)" >	
							<td class="line">Aliases</td>
							<td>
								<div py:for="alias in get_aliases(object)">
	<input name="aliases-${alias.id}.id" type="hidden" class="text"  value="${alias.id}" />								
        <input name="aliases-${alias.id}.alias_name" type="text" class="text"  value="${alias.alias_name}" />
								</div>
								<div class="errorMessage" py:if="tg_errors">${print_error('aliases', tg_errors)}</div>
								<div>
									<input name="new_alias" type="text" class="text"  value="${new_aliases(object)}" />
                                                                <a href="#alias_area" id="add_more_alias" title="Add More Aliases">
                                                                    <big name="alias_area">+</big></a>
								<div class="errorMessage" py:if="tg_errors">${print_error('new_alias', tg_errors)}</div>
								</div>
                 </td>
                 </tr>
                 <tr>
                     <td class="line">Home Hub</td>
                     <td>
                         <table>
                            <tr><th>location</th><th>home hub</th><th>member</th><th>host</th><th>director</th></tr>
<?python
c_user = identity.current.user
is_superuser = Group.by_group_name('superuser') and Group.by_group_name('superuser') in c_user.groups
if is_superuser:
    editable_roles = dict([(g.place, add_role_perms) for g in c_user.groups if g.place])
else:
    editable_roles = dict([(g.place, [p.permission_name for p in g.permissions if p.permission_name in add_role_perms]) for g in c_user.groups if g.place])
current_roles = get_current_roles(object)
all_locations = list(set(current_roles.keys() + editable_roles.keys()))
roles_data = get_roles_data(current_roles, editable_roles, all_locations)
?>
                            <tr py:for="location in all_locations">
                                <td>
                                    ${location.name}
                                    <div class="errorMessage" py:if="tg_errors">${print_error('groups', tg_errors)}</div>
                                </td>
                                <td>
                                    <input type="radio" name="homeplace" value="${location.id}" py:attrs="current_home(location, object)" />
                                    <div class="errorMessage" py:if="tg_errors">${print_error('homeplace', tg_errors)}</div>
                                </td>
                                <td py:for="role in roles">
                                    <input py:if="roles_data[location][role][1]" type="checkbox" name="groups.${location.id}.${role}" 
                                        value="1" py:attrs="roles_data[location][role][0] and {'checked':'checked'} or {}"/>
                                    <span py:if="not roles_data[location][role][1]">
                                        <c py:if="roles_data[location][role][0]" py:strip="True">Yes</c>
                                        <c py:if="not roles_data[location][role][0]" py:strip="True"></c>
                                    </span>
                                </td>
                            </tr>
                         </table>
                      </td>
                  </tr>				
              </table>
            </td>
         </tr>
  </table>
  ${load_memberProfileEdit(object, tg_errors=tg_errors)}
</div>		
