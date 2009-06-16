from hubspace.model import *
import hubspace.model
model = hubspace.model
from sqlobject import AND, OR, IN
from hubspace.utilities.uiutils import now
from hubspace.tariff import get_tariff
import datetime
from datetime import timedelta, date, time, datetime as dt
from sqlobject.events import listen, RowCreateSignal, RowCreatedSignal, RowDestroySignal, RowUpdateSignal


##################  Policies Groups ############
#special groups, just for the purpose of assigning entry times

from hubspace.utilities.object import create_object

def add_policy_group(name, description, location):
    
    policy_group = create_object('PolicyGroup', **{'name':name, 'description':description, 'place':location})
    return policy_group

def add_users2policy_group(group, user_ids=None):
    if not isinstance(user_ids, list):
        raise "user_ids must be in a list"
    for user_id in user_ids:
        if UserPolicyGroup.select(AND(UserPolicyGroup.q.userID==user_id,
                                      UserPolicyGroup.q.policygroupID==group.id)).count():
            continue
        UserPolicyGroup(userID=user_id, policygroupID=group.id)

def remove_users2policy_group(group, user_ids=None):
    if not isinstance(user_ids, list):
        raise "user_ids must be in a list"
    memberships = UserPolicyGroup.select(AND(IN(UserPolicyGroup.q.userID, user_ids),
                                             UserPolicyGroup.q.policygroupID == group.id))
    for membership in memberships:
        membership.destroySelf()

def remove_policy_group(pol_group):
    users_relations = UserPolicyGroup.select(AND(UserPolicyGroup.q.policygroupID==pol_group.id))
    for rel in users_relations:
        rel.destroySelf()
    for access_pol in pol_group.access_policies:
        for open_time in access_pol.open_times:
            open_time.destroySelf()
        access_pol.destroySelf()
    pol_group.destroySelf()

####################Access Policies#############################
from hubspace.utilities.object import obj_of_type

class ConflictingPolicy(Exception):
    def __init__(self):
        self.value = "Policy conflicts with an existing policy"
    def __str__(self):
        return repr(self.value)

def add_accessPolicy2Proxy(policyResource, policyProxy_id, policyProxy_type, precedence, policyStartDate=None, policyEndDate=None):
    """add an access policy to a role/group, policyGroup, or tariff. There must be only 1 AccessPolicy per policyResource-policyProxy combination, for a particular period (no overlapping periods).
    """
    policyProxy = obj_of_type(policyProxy_type, policyProxy_id)
    location = policyProxy.place

    if policyResource.place != location:
        raise ValueError("access_policies can only arbitrate access to resources that are in the same location as the PolicyProxy which confers it")
    
    kwargs = {'policy_resource':policyResource.id, 'location':location.id, 'precedence':precedence}
    kwargs['policyStartDate'] = policyStartDate and policyStartDate or date.min
    kwargs['policyEndDate'] = policyEndDate and policyEndDate or date.max

    if isinstance(policyProxy, Group):
        proxy_attr = 'group'
    elif isinstance(policyProxy, PolicyGroup):
        proxy_attr = 'policygroup'
    elif isinstance(policyProxy, Resource) and policyProxy.type == 'tariff':
        proxy_attr = 'tariff'
    else:
        raise ValueError("policy proxy is not of type ['Group, PolicyGroup', 'Resource'] OR it is a resource which is not of type 'tariff'. It is a "+  `type(policyProxy)`)
    
    kwargs[proxy_attr] = policyProxy.id
    conflict = AccessPolicy.select(AND(AccessPolicy.q.policy_resourceID == kwargs['policy_resource'],
                                       AccessPolicy.q.__getattr__(proxy_attr+'ID') == policyProxy.id))


    if conflict.count():
        raise ConflictingPolicy
    return create_object('AccessPolicy', **kwargs)
    
def remove_accessPolicy2Proxy(id):
    """remove the accessPolicy and any opentimes that reference it.
    """
    access_pol = AccessPolicy.get(id)
    for open_time in access_pol.open_times:
        open_time.destroySelf()
    access_pol.destroySelf()
    return id
    
#we want to update user.access_policies whenever...

#a) a user is added to or removed from a tariff/group/policyGroup
def user_acquires_policyProxy(user, policyProxy):
    """called when adding a user to a group/role, policyGroup, tariff (save_tariffHistoryEdit)
    """
    #get the policies associated with this policyProxy
    access_policies = user.access_policies        
    if not user.active:
        access_policies = user.disabled_policies
    if isinstance(policyProxy, Group) and user in policyProxy.users:
        print "acquired " + policyProxy.group_name
        for pol in policyProxy.access_policies:
            if int(pol.id) not in access_policies:
                access_policies.append(int(pol.id))

    elif isinstance(policyProxy, PolicyGroup) and user in policyProxy.users:
        print "acquired " + policyProxy.name
        for pol in policyProxy.access_policies:
            if int(pol.id) not in access_policies:
                access_policies.append(int(pol.id))

    elif isinstance(policyProxy, Resource) \
           and policyProxy.type=='tariff'  \
           and get_tariff(policyProxy.place.id, user.id, now(policyProxy.place)) == policyProxy:
        print "acquired " + policyProxy.name
        for pol in policyProxy.access_policies:
            if int(pol.id) not in access_policies:
                access_policies.append(int(pol.id))
    if user.active:
        user.access_policies = access_policies
    else:
        user.disabled_policies = access_policies

def user_loses_policyProxy(user, policyProxy):
    """call explicitly (better to user setter and getter on the model) *before* deleting/removing a user from a policyProxy
    """
    access_policies = user.access_policies
    if not user.active:
        access_policies = user.disabled_policies

    if isinstance(policyProxy, Group) and user in policyProxy.users:
        #user should have already been removed
        print "lost " + policyProxy.group_name
        for pol in policyProxy.access_policies:
            access_policies.remove(int(pol.id))

    if isinstance(policyProxy, PolicyGroup) and user in policyProxy.users:
        print "lost " + policyProxy.name
        for pol in policyProxy.access_policies:
            if int(pol.id) in access_policies:
                access_policies.remove(int(pol.id))

    if isinstance(policyProxy, Resource) \
           and policyProxy.type=='tariff' \
           and get_tariff(policyProxy.place.id, user.id, now(policyProxy.place)) != policyProxy:
        print "lost " + policyProxy.name
        for pol in policyProxy.access_policies:
            if int(pol.id) in access_policies:
                access_policies.remove(int(pol.id))
    if user.active:
        user.access_policies = access_policies
    else:
        user.disabled_policies = access_policies


def lose_groupProxy(instance, post_funcs):
    user_loses_policyProxy(instance.user, instance.group)
    
def acquires_groupProxy(instance):
    user_acquires_policyProxy(instance.user, instance.group)

def acquire_groupProxy(kwargs, post_funcs):
    post_funcs.append(acquires_groupProxy)

def lose_policyGroupProxy(instance, post_funcs):
    user_loses_policyProxy(instance.user, instance.policygroup)
    
def acquires_policyGroupProxy(instance):
    user_acquires_policyProxy(instance.user, instance.policygroup)

def acquire_policyGroupProxy(kwargs, post_funcs):
    post_funcs.append(acquires_policyGroupProxy)

listen(lose_groupProxy, UserGroup, RowDestroySignal)
listen(acquire_groupProxy, UserGroup, RowCreatedSignal)
listen(lose_policyGroupProxy, UserPolicyGroup, RowDestroySignal)
listen(acquire_policyGroupProxy, UserPolicyGroup, RowCreatedSignal)

#b) a group/policyGroup/tariff has a accessPolicy added or removed
from hubspace.tariff import tariff_users

def policy_removed(instance, post_funcs):
    """if a policy is removed this will be called automatically 
    """
    print "removing access policy " + `instance`
    if instance.group:
        users = instance.group.users
    elif instance.policygroup:
        users = instance.policygroup.users
    elif instance.tariff:
        users = tariff_users(instance.tariff)
        
    for user in users:
        if user.active:
            access_policies = user.access_policies
            if instance.id in access_policies:
                access_policies.remove(int(instance.id))
                user.access_policies = access_policies
        else:
            access_policies = user.disabled_policies
            if instance.id in access_policies:
                access_policies.remove(int(instance.id))
                user.disabled_policies = access_policies
            
def policy_added(instance):
    """if an access_policy is added this will be called automatically afterwards
    """
    print "adding an access policy " + `instance.id`
    if instance.group:
        users = instance.group.users
    elif instance.policygroup:
        users = instance.policygroup.users
    elif instance.tariff:
        users = tariff_users(instance.tariff)

    for user in users:
        if user.active:
            access_policies = user.access_policies

            if instance.id not in access_policies:
                access_policies.append(int(instance.id))
                user.access_policies = access_policies
        else:
            access_policies = user.disabled_policies
            if instance.id not in access_policies:
                access_policies.append(int(instance.id))
                user.disabled_policies = access_policies


    
def policy_add(kwargs, post_funcs):
    post_funcs.append(policy_added)

listen(policy_removed, AccessPolicy, RowDestroySignal)
listen(policy_add, AccessPolicy, RowCreatedSignal)

#c) when the month turns we call this from the scheduler
from hubspace.utilities.users import filter_members

def recalculate_tariff_accessPolicies(location=None):
    """call explicitly when the month changes. Assumes monthly tariffs.
    Executed every hour on turn of the month so that updates are done per location at midnight.
    """
    if not location:
        raise ValueError("There should be a location")

    users = filter_members(location, "", "member_search", active_only=False, start=None, end=None, override_user=True)
    time_here = now(location)
    #time_here = dt(2009, 2, 1) # for testing
    new_month = time_here + timedelta(days=1)
    old_month = time_here - timedelta(days=27)
    model.hub.commit()
    model.hub.begin()
    for user in users:
        old_tariff = get_tariff(location.id, user.id, old_month)
        new_tariff = get_tariff(location.id, user.id, new_month)
        if old_tariff != new_tariff:
            user_acquires_policyProxy(user, new_tariff)
            user_loses_policyProxy(user, old_tariff)        
            model.hub.commit()
            model.hub.begin()
    model.hub.commit()
#d) if a user is made inactive remove all his access policies
#e) if a user is made active re-enable all his access policies from scratch

def toggle_active(instance, kwargs):
    """if a user is edited this is called
    """
    if 'active' in kwargs:
        if kwargs['active'] and kwargs['active'] != instance.active:
            instance.access_policies = instance.disabled_policies
            instance.disabled_policies = []
        elif kwargs['active'] != instance.active:
            instance.disabled_policies = instance.access_policies
            instance.access_policies = []

listen(toggle_active, User, RowUpdateSignal)
        

##################  Opening Times ##############
def check_access(user, policy_resource, check_datetime):
    """check if the user can access the domain at the specified time and return a boolean
    """
    times = get_times(policy_resource, check_datetime.date(), user=user)
    for time in times:
        if check_datetime.time() >= time[0] and check_datetime.time() <= time[1]:
            return True
    return False

def get_times(policy_resource, check_date, user=None, role=None, combined=True):
    if user:
        available_policies = user.access_policies
    elif role:
        available_policies = role.access_policies

    policies = get_applicable_accessPolicies(policy_resource, check_date, available_policies)
    policies = filter_policy_precedence(policies)
    times = get_times_from_policies(policies)
    if combined:
        times = combine_times(times)
    if not times:
        #ensure that if the user doesn't have any access policies the calendar can still be rendered but the user cannot book
        times.append(time(9,00), time(8,59))
    return times

def combine_times(policy_times):
    """We now combine times from all access_policies additively.
    """
    all_times = []
    for pol, times in policy_times.iteritems():
        all_times.extend(times)
    all_times.sort(lambda x, y: cmp(x.openTimeStart, y.openTimeStart))
    new_times = []
    for time in all_times:
        start_time = time.openTimeStart
        end_time = time.openTimeEnd
        if new_times==[] or start_time > new_times[-1][1]:
            new_times.append([start_time, end_time])
        elif start_time <= new_times[-1][1] and end_time > new_times[-1][1]:
            new_times[-1][1] = end_time
        else:
            pass
    return new_times

def get_times_from_policies(policies):
    """Evaluate the times from each AccessPolicy (of equal precedence). Within an AccessPolicy a date entry, will override a holiday, will override a day entry. Filter out any day entries which are not the newest for their policy.  
    """
    policy_times = {}
    for pol in policies:
        date_times = []
        holiday_times = []
        day_times = []
        for time in pol.open_times:
            if time.openTimeDay in range(0,7):
                day_times.append(time)
            elif time.openTimeDay == 7:
                holiday_times.append(time)
            elif isinstance(time.openTimeDate, datetime.date):
                date_times.append(time)
            else:
                pass
            
        if date_times:
            policy_times[pol.id] = date_times
        elif holiday_times:
            policy_times[pol.id] = holiday_times
        elif day_times:
            min_date = datetime.date.min
            filtered_day_times = []
            for time in day_times:
                if time.openTimeStartDate > min_date:
                    min_date = time.openTimeStartDate
                    filtered_day_times = [time]
                elif time.openTimeStartDate == min_date:
                    filtered_day_times.append(time)
            policy_times[pol.id] = filtered_day_times
        else:
            pass
    return policy_times

    
def filter_policy_precedence(policies):
    """We throw away any AccessPolicies which are not of the highest precendence present.
    """
    max_precendence = 11 #max precedence is 1 min precedence is 10
    for pol in policies:
        if pol.precedence < max_precendence:
            max_precendence = pol.precedence
            new_policies = [pol]
        elif pol.precedence == max_precendence:
            new_policies.append(pol)
        else:
            pass
    return new_policies

    

def get_applicable_accessPolicies(policy_resource, check_date, available_policies):
    """Get all the access_policies which apply (in the location, for the domain, at the specified datetime).
    """            
    day_code = check_date.weekday()
    holiday = 8 #day 8 doesn't exist
    if check_date in policy_resource.place.holidays:
        holiday = 7
    return AccessPolicy.select(AND(IN(AccessPolicy.q.id, available_policies),
                                   AccessPolicy.q.policy_resourceID == policy_resource.id,
                                   AccessPolicy.q.policyStartDate <= check_date,  
                                   AccessPolicy.q.policyEndDate >= check_date,
                                   Open.q.policyID == AccessPolicy.q.id,
                                   OR(AND(OR(Open.q.openTimeDay == day_code,
                                             Open.q.openTimeDay == holiday),
                                          Open.q.openTimeStartDate <= check_date),
                                      Open.q.openTimeDate == check_date)
                                   )
                               )
    
        
def check_time_data(openTimeDay, openTimeStartDate, openTimeDate, openTimeStart, openTimeEnd):

    if isinstance(openTimeDay, int) and isinstance(openTimeDate, date):
        return False
    elif not isinstance(openTimeDay, int) and not isinstance(openTimeDate, date):
        return False
    
    if not (openTimeStart and openTimeEnd):
        return False
    return True

   
def create_openTime(pol_id, openTimeDay, openTimeStartDate, openTimeDate, openTimeStart, openTimeEnd):

    """create a new open time object
    """
    if not check_time_data(openTimeDay, openTimeStartDate, openTimeDate, openTimeStart, openTimeEnd):
        raise "not good openTime data"
    
    if openTimeDay is not None and not openTimeStartDate:
        openTimeStartDate = datetime.date.min
        
    return create_object('Open', policy=pol_id, openTimeStartDate=openTimeStartDate, openTimeDay=openTimeDay, openTimeDate=openTimeDate, openTimeStart=openTimeStart, openTimeEnd=openTimeEnd)

def delete_openTime(open_time_id):
    Open.get(open_time_id).destroySelf()
    return "deleted"

def edit_openTime(open_time_id, openTimeStartDate, openTimeDay, openTimeDate, openTimeStart, openTimeEnd):
    if not check_time_data(openTimeDay, openTimeStartDate, openTimeDate, openTimeStart, openTimeEnd):
        raise "not good openTime data"

    if openTimeDay and not openTimeStartDate:
        openTimeStartDate = datetime.date.min

    open_time = Open.get(open_time_id)
    modify_attributes(open_time, dict(openTimeStartDate=openTimeStartDate, openTimeDay=openTimeDay, openTimeDate=openTimeDate, openTimeStart=openTimeStart, openTimeEnd=openTimeEnd))
    return open_time


###############################utilities#########################

def week_from_date(date):
    week_starts = date - timedelta(days=date.weekday())
    week_ends = week_starts + timedelta(days=7)
    day = week_starts
    while day<week_ends:
        yield day
        day = day + timedelta(days=1)

def create_default_open_times(access_policy):
    for day in range(0, 7):
        create_openTime(access_policy.id, day, None, None, time(7,00), time(23, 59))


#################calendar time scripts################################
from turbogears import identity

def opening_times(policy_resource, date, role='host', period="day"):
    """Get a list of opening times for a day, or for a week, we use host access policies as we remder the whole host opening times to anyone, but simply restrict making bookings to hosts at certain times
    """
    if role in ['member', 'host', 'director']:     
        role = Group.select(AND(Group.q.level == role,
                                Group.q.placeID == policy_resource.place))[0]
    try:
        role.access_policies
    except:
        raise ValueError("no such role")                          
    if period == "day":
        return get_times(policy_resource, date, role=role)
    elif period == 'week':
        week_times = {}
        for day in week_from_date(date):
            week_times[day] = get_times(policy_resource, day, role=role)
        return week_times
