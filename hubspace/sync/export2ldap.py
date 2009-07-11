"""
Sqlobject instances => syncer => LDAP
"""
import sys, datetime, time
from sqlobject import AND, OR, DESC
import turbogears
turbogears.update_config(configfile="dev.cfg", modulename="hubspace.config")
from hubspace import model
import syncer.helpers.ldap
import syncer.client
import syncer.config
import hubspace.sync.core as core

syncerclient = core.syncerclient # = syncerclient

instance2kw = lambda o: {'class':o.__class__, 'id':o.id}

#assert turbogears.config.config.configs['syncer']['sync'], "Turn the sync ON in dev.cfg"

def addUser(instance):
    print '\t adding ', instance.user_name,
    then = datetime.datetime.now()
    ret = core.usr_add_listener(instance2kw(instance), [])
    now = datetime.datetime.now()
    print str(now - then), " (%s)" % ret[0]
    return ret

def addHub(instance):
    print '\t adding ', instance.name, instance.holidays
    return core.hub_add_listener(instance2kw(instance),[])

def addGroup(instance):
    print '\t adding ', instance.group_name
    if instance.place:
        return core.grp_add_listener(instance2kw(instance),[])

def addUser2Group(instance):
    print '\t adding ', instance.user.user_name, 'to', instance.group.group_name
    return core.add_user2grp_listener(instance2kw(instance),[])

def addAccesspolicy(instance):
    print '\t adding policy ', instance.id, 'to', instance.location.id
    return core.accesspolicy_add_listener(instance2kw(instance), [])

def addOpentime(instance):
    print '\t adding openTime', instance.id, 'to policy', instance.policy.id
    return core.opentimes_add_listener(instance2kw(instance), [])

def addTariff(instance):
    print '\t adding tariff', instance.id
    return core.tariff_add_listener(instance2kw(instance), [])

def assignTariff(user):
    tr_ids = []
    for loc in model.Location.select():
        instances = list(model.RUsage.select(AND(model.Resource.q.type=="tariff",
                                                 model.RUsage.q.userID==user.id,
                                                 model.RUsage.q.resourceID==model.Resource.q.id,
                                                 model.Resource.q.placeID==loc.id)).orderBy(DESC(model.RUsage.q.start))[0:1])
        if instances:
            instance = instances[0]
            print '\t assigning tariff', instance.id, 'for user ', user.user_name
            tr_ids.append(core.tariff_listener(instance2kw(instance), [])[0])
    return tr_ids


def checkSyncerErrors(f):
    def wrap(*args, **kw):
        try:
            return f(*args, **kw)
        except core.SyncerError:
            sys.exit("Failed! Check logs/hubspace.log")
    return wrap

@checkSyncerErrors
def main():
    time.sleep(2)

    print 'Adding Hubs'
    print
    for hub in model.Location.select():
        tr_id, ret = addHub(hub)
        syncerclient.completeTransactions([tr_id])

    print 'Adding Users'
    print
    now = datetime.datetime.now()
    for user in model.User.select():
        if user.user_name in ('webapi',): continue
        tr_id, ret = addUser(user)
        syncerclient.completeTransactions([tr_id])

    print 'Adding Groups'
    print
    for group in model.Group.select():
        if group.group_name in ('webapi','superuser'):
            print 'skipping', group.group_name
            continue 
        ret = addGroup(group)
        tr_id, ret = ret
        syncerclient.completeTransactions([tr_id])

    print 'Adding users to groups'
    for instance in model.UserGroup.select():
        if instance.group.place is None:
            print "\t skipping", instance.user.user_name, '->', instance.group.group_name
            continue 
        addUser2Group(instance)

    print 'Adding Tariffs'
    for instance in model.Resource.select():
        if instance.type == "tariff":
            tr_id, ret = addTariff(instance)
            syncerclient.completeTransactions([tr_id])

    print 'Adding policies to hubs'
    for instance in model.AccessPolicy.select():
        tr_id, ret = addAccesspolicy(instance)
        syncerclient.completeTransactions([tr_id])

    print 'Adding openTimes'
    for instance in model.Open.select():
        tr_id, ret = addOpentime(instance)
        syncerclient.completeTransactions([tr_id])

    print 'Assignining Tariffs'
    print
    now = datetime.datetime.now()
    for user in model.User.select():
        if user.user_name in ('webapi',): continue
        tr_ids = assignTariff(user)
        syncerclient.completeTransactions(tr_ids)

