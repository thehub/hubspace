from turbogears import identity, redirect
from hubspace.model import *
from hubspace.utilities.object import create_object
from sqlobject import AND, IN
import itertools as it

roles = ('member', 'host', 'director')
add_role_perms = ['add_' + role + 's' for role in roles]

##################  Rights management  ##########

def new_group(**kwargs):
    group = create_object('Group', **kwargs)
    perms = []
    group_name = group.group_name
    print 'Created ', group_name
    if group.level=='director' or group.level=='host':
        perms = ['manage_users','manage_todos','manage_notes', 'manage_resources', 'manage_pricings', 'manage_invoices', 'add_members', 'manage_rusages']
    if group.level == 'director':
        perms.extend(['add_hosts','add_directors', 'manage_groups', 'manage_locations'])
    for perm in perms:
        add_perm_to_group(group, perm)
                 
    return group

def add_perm_to_group(group, perm_name):
    p = Permission.selectBy(permission_name=perm_name)[0]
    print 'adding permission ', p.permission_name, ' to ', group.group_name
    group.addPermission(p)

def groups_in_place(place):
    '''Returns the current users groups in the context of a given place'''
    user = identity.current.user
    try:
        return [g for g in user.groups if g.place==place or g.place==None]
    except AttributeError:
        redirect("/login")

def gip(place):
    return [g.group_name for g in groups_in_place(place)]

def permissions_in_place(place):
    '''Returns the current users permissions in the context of a given place
    
    The problem is that turbogears has no concept of context (like e.g. Zope has).
    This means that we can't say: for this location you have the following rights.
    Instead of that we have the same set of groups for every location, and assign
    permissions to these groups. By that the admin can have different settings for
    every location. This implies however that we can't ask if a user has a certain
    permission (full stop), instead of that we need to ask if a user has a permission
    in a place - the user could be e.g. a member in one place and not a member
    in another place.
    '''
    perms = []
    user = identity.current.user
    for g in groups_in_place(place):
        for p in g.permissions:
            if p not in perms:
                perms.append(p)
    return perms

def pip(place):
    return [p.permission_name for p in permissions_in_place(place)]

#XXX make this a class method?    
def get_place(obj):
    classname = obj.__class__.__name__
    if classname in ['Group','Resource']:
        return obj.place
    elif classname == 'Location':
        return obj
    elif classname == 'RUsage':
        return obj.resource.place
    elif classname == 'User':
        return obj.homeplace
    else:
        return None
    
#XXX make this a class method?
def is_owner(obj,user=None):
    if not user:
        user = identity.current.user
    if obj == None:
        return False
    classname = obj.__class__.__name__
    if classname == 'User':
        return obj == user
    elif classname == 'Todo':
        return obj.createdby == user
    elif classname in  ['Invoice','RUsage']:
        return obj.user == user
    else:
        return False


def permission_or_owner(place,obj,permissions,user=None):
    '''obj can be set to None to _not_ check ownership
    place can be set to None for non-location specific perms
    place can be set to a list to check if the user has the permission in any of the locations'''
    if isinstance(place, list):
        for pl in place:
            if permission_or_owner(pl, obj, permissions, user):
                return True
        return False

    if type(permissions) != type([]):
        permissions = [permissions]
    has_permission = False
    if place:
        pips = pip(place)
        for perm in permissions:
            if perm in pips or 'superuser' in pips:
                has_permission = True
    else:
        for perm in permissions:
            if perm in identity.current.permissions or 'superuser' in pip(identity.current.user.homeplace):
                has_permission = True
    owner = False
    if obj:
        owner = is_owner(obj,user)
    return has_permission or owner


def loc_alpha(a, b):
    if a.name > b.name:
       return 1
    return -1


def locations(permission="manage_resources"):
    """get all the locations in which the current user has a specific permission
    """
    if identity.has_permission('superuser'):
        locations = list(Location.select())
    else:
        locations = []
        for group in identity.current.user.groups:
            location = get_place(group)
            if location:
                if permission_or_owner(location, location, permission) and location not in locations:
                    locations.append(location)
    locations.sort(loc_alpha)
    return locations


def user_locations(user, levels=['host']):
    """get all the locations in which a user has any of the "levels" (by virtue of group membership)
    """
    if 'superuser' in levels and 'superuser' in pip(user.homeplace):
        return Location.select()
    locations = []
    for group in user.groups:
        if group.level in levels and group.place and group.place not in locations:
            locations.append(group.place)
    return locations


def is_host(user, location, render_static=False):
    if render_static:
        return False    
    if not user:
        return False
    group = Group.select(AND(Group.q.level == 'host',
                             Group.q.placeID == location.id,
                             UserGroup.q.userID == user.id,
                             UserGroup.q.groupID == Group.q.id))
    if group.count():
        return True
    return False


def addUser2Group(user=None, group=None, book=True):
    if user not in group.users:
        kwargs = {'user':user, 'group':group}
        create_object('UserGroup', **kwargs)
    return 'ok'

def get_editable_roles(user):
    """
    -> {location1: [level1, level2,..], location2: ...}
    """
    c_user = identity.current.user
    is_superuser = Group.by_group_name('superuser') and Group.by_group_name('superuser') in c_user.groups
    if is_superuser:
        editable_roles = dict([(location, add_role_perms) for location in Location.select()])
    else:
        editable_roles = dict([(g.place, [p.permission_name for p in g.permissions if p.permission_name in add_role_perms]) for g in c_user.groups if g.place])
    return editable_roles

def get_current_roles(user):
    """
    -> {Location1: [level1, level2, ..], location2:...}
    """
    return dict((loc, tuple(g[1] for g in groups)) for loc, groups in it.groupby(sorted((g.place, g.level) for g in user.groups if g.place), lambda x: x[0]))
