import logging
import time
import turbogears.config
import hubspace.config
from turbogears.identity.soprovider import SqlObjectIdentityProvider
import thread
import threading
import base64
import sendmail

try:
    ldap_sync_enabled = turbogears.config.config.configs['syncer']['sync']
except Exception, err:
    print err
    ldap_sync_enabled = False

tls = threading.local()
applogger = logging.getLogger("hubspace")
SSOIdentityProvider = SqlObjectIdentityProvider
_cp_filters = []

def setupLDAPSync(): pass
def sendRollbackSignal(): pass

class SyncerError(Exception):
    """
    Raise this error when syncer transaction fails
    """

if ldap_sync_enabled:
    import syncer
    import syncer.client
    import syncer.config
    import syncer.utils
    import syncer.helpers
    import syncer.helpers.ldap
    import cherrypy
    from cherrypy.filters.basefilter import BaseFilter
    import hubspace.model as model
    
    syncer.config.host = turbogears.config.config.configs['syncer']['syncer_host']
    syncer.config.port = turbogears.config.config.configs['syncer']['syncer_port']
    syncer.config.__syncerdebug__ = True
    syncer.config.reload()
    
    _sessions = dict()
    sessiongetter = lambda: _sessions
    syncerclient = syncer.client.SyncerClient("hubspace", sessiongetter)
    
    class SSOIdentityProvider(SqlObjectIdentityProvider):
    
        def validate_identity(self, user_name, password, visit_key):
            iden = super(SSOIdentityProvider, self).validate_identity(user_name, password, visit_key)
            
            applogger = logging.getLogger("hubspace")
            if iden and not syncerclient.isSyncerRequest(cherrypy.request.headers.get("user-agent", None)):
                cookies = syncer.utils.convertCookie(cherrypy.request.simple_cookie)
                try:
                    ret = syncerclient.onUserLogin(user_name, password, cookies)
                    t_id, res = ret
                except ValueError:
                    print ret
                    # a warning here
                    return iden
                except Exception, err:
                    print err
                    # a warning here
                    return iden
    
                if not syncerclient.isSuccessful(res):
                    print syncer.client.errors.res2errstr(res)

                else:
                    for v in res.values():
                        sso_cookies = v['result']
                        c = syncer.utils.convertCookie(sso_cookies)
                        cherrypy.response.simple_cookie.update(c)

            # help issue reporter
            try:
                user = iden.user
                uinfo = "|".join((user.first_name, user.last_name, user.homeplace.name, user.email_address))
                cherrypy.response.simple_cookie['uinfo'] = base64.b64encode(uinfo)
                cherrypy.response.simple_cookie['uinfo']['domain'] = turbogears.config.config.configs['global']['session_filter.cookie_domain']
            except Exception, err:
                # dont stop on any error
                print err

            return iden

    # http://www.cherrypy.org/wiki/UpgradeTo22
    class TransactionCompleter(BaseFilter):
        def on_start_resource(self, *args, **kw):
            tls.syncer_trs = []
            print "syncer_trs created"
        def on_end_request(self, *args, **kw):
            if hasattr(tls, 'syncer_trs') and tls.syncer_trs:
                print "sending", tls.syncer_trs
                syncerclient.completeTransactions(tuple(tls.syncer_trs))

    _cp_filters.append(TransactionCompleter())

    def sendRollbackSignal():
        if hasattr(tls, "syncer_trs") and tls.syncer_trs:
            to_rollback = tls.syncer_trs
            tls.syncer_trs = []
            if to_rollback:
                syncerclient.rollbackTransactions(tuple(reversed(to_rollback)))
    
    def signon():
        u = turbogears.config.config.configs['syncer']['hubspaceadminuid']
        p = turbogears.config.config.configs['syncer']['hubspaceadminpass']
        ret = syncerclient.onSignon(u, p)
        tr_id, res = ret
        if syncerclient.isSuccessful(res):
            syncerclient.setSyncerToken(res['sessionkeeper']['result'])
            msg = "Syncer signon successful"
            applogger.info(msg)
            print msg
            return True
        msg = "Syncer signon failed: %s" % res
        applogger.warn(msg)
        print msg
        msg = syncer.client.errors.res2errstr(res)
        applogger.warn(msg)
        print msg

    def signonloop():
        while not signon():
            time.sleep(10)

    ## All sync operations ##
    
    from sqlobject.events import listen, RowUpdateSignal, RowCreatedSignal, RowDestroySignal
    
    def checkSyncerResults(f):
        def wrap(*args, **kw):
            ret = f(*args)
            f_name = getattr(f, '__name__', str(f))
            applogger.debug("syncer: %s-> %s" % (f_name, ret))
            if ret:
                t_id, res = ret
                if res and not syncerclient.isSuccessful(res):
                    raise SyncerError("syncer backend error")
                    return
                if t_id > 0:
                    tls.syncer_trs.append(t_id)
                    print "syncer_trs.append", t_id
                return ret
        return wrap
    
    def checkReqHeaders(f):
        def wrap(*args, **kw):
            try:
                if not syncerclient.isSyncerRequest(cherrypy.request.headers.get("user-agent", None)):
                    return f(*args, **kw)
            except AttributeError:
                # outside CheeryPy request which is fine
                    return f(*args, **kw)
        return wrap
    
    @checkSyncerResults
    @checkReqHeaders
    def usr_updt_listener(instance, kwargs):
        if instance.user_name == turbogears.config.config.configs['syncer']['hubspaceadminuid']: return
        kw = dict ([(k, v) for (k,v) in kwargs.items() if getattr(instance, k) != v])
        if kw:
            mod_list = syncer.helpers.ldap.object_maps['user'].toLDAP(instance, kw)
            if mod_list:
                return syncerclient.onUserMod(instance.user_name, mod_list)
    
    @checkSyncerResults
    @checkReqHeaders
    def hub_updt_listener(instance, kwargs):
        kw = dict ([(k, v) for (k,v) in kwargs.items() if getattr(instance, k) != v])
        mod_list = syncer.helpers.ldap.object_maps['hub'].toLDAP(instance, kw)
        if mod_list:
            return syncerclient.onHubMod(instance.id, mod_list)
    
    @checkReqHeaders
    @checkSyncerResults
    def usr_add_listener(kwargs, post_funcs):
        instance = kwargs['class'].get(kwargs['id'])
        mod_list = syncer.helpers.ldap.object_maps['user'].toLDAP(instance)
        return syncerclient.onUserAdd(instance.user_name, mod_list)
    
    @checkReqHeaders
    @checkSyncerResults
    def hub_add_listener(kwargs, post_funcs):
        instance = kwargs['class'].get(kwargs['id'])
        mod_list = syncer.helpers.ldap.object_maps['hub'].toLDAP(instance, {})
        return syncerclient.onHubAdd(instance.id, mod_list)
    
    @checkReqHeaders
    @checkSyncerResults
    def grp_add_listener(kwargs, post_funcs):
        instance = kwargs['class'].get(kwargs['id'])
        mod_list = syncer.helpers.ldap.object_maps['role'].toLDAP(instance, {})
        return syncerclient.onRoleAdd(instance.place.id, instance.level, mod_list)
    
    @checkReqHeaders
    @checkSyncerResults
    def grp_updt_listener(instance, kwargs):
        mod_list = syncer.helpers.ldap.object_maps['group'].toLDAP(instance, kwargs)
        return syncerclient.onGroupMod(kwargs['group_name'], mod_list)
    
    @checkReqHeaders
    @checkSyncerResults
    def accesspolicy_add_listener(kwargs, post_funcs):
        instance = kwargs['class'].get(kwargs['id'])
        mod_list = syncer.helpers.ldap.object_maps['policy'].toLDAP(instance, {})
        return syncerclient.onAccesspolicyAdd(instance.location.id, mod_list)
    
    @checkReqHeaders
    @checkSyncerResults
    def accesspolicy_updt_listener(instance, kwargs):
        mod_list = syncer.helpers.ldap.object_maps['policy'].toLDAP(instance, kwargs)
        return syncerclient.onAccesspolicyMod(instance.id, instance.location.id, mod_list)
    
    @checkReqHeaders
    @checkSyncerResults
    def accesspolicy_del_listener(instance, post_funcs):
        return syncerclient.onAccesspolicyDel(instance.id, instance.location.id)
    
    @checkReqHeaders
    @checkSyncerResults
    def opentimes_add_listener(kwargs, post_funcs):
        instance = kwargs['class'].get(kwargs['id'])
        mod_list = syncer.helpers.ldap.object_maps['opentimes'].toLDAP(instance, {})
        return syncerclient.onOpentimesAdd(instance.policy.id, instance.policy.location.id, mod_list)
    
    @checkReqHeaders
    @checkSyncerResults
    def opentimes_updt_listener(instance, kwargs):
        mod_list = syncer.helpers.ldap.object_maps['opentimes'].toLDAP(instance, kwargs)
        return syncerclient.onOpentimesMod(instance.id, instance.policy.id, instance.policy.location.id, mod_list)
    
    @checkReqHeaders
    @checkSyncerResults
    def opentimes_del_listener(instance, post_funcs):
        return syncerclient.onOpentimesDel(instance.id, instance.policy.id, instance.policy.location.id)
    
    #@checkSyncerResults
    def tariff_listener(kwargs, post_funcs):
        instance = kwargs['class'].get(kwargs['id'])
        if instance.resource.type != 'tariff':
            return 
        tariff_id = instance.resource.id
        place_id = instance.resource.place.id
        username = instance.user.user_name
        mod_list = syncer.helpers.ldap.object_maps['user'].toLDAP(None, dict(tariff_id = tariff_id, hubId = place_id))
        t_id, res = syncerclient.onUserMod(username, mod_list)
        if not syncerclient.isSuccessful(res):
            body = """
    LDAP Error: Setting Tariff for user %(username)s has failed.
    Below is the data send to syncer for the modificarion:
    Hub id: %(place_id)s
    Change data: %(mod_list)s
    """ % locals()
            sendmail.sendmail(to="world.tech.space@the-hub.net", sender="noreply@the-hub.net", \
                cc="shekhar.tiwatne@the-hub.net", subject="LDAP Error report", body=body)
        return t_id, res
    
    @checkReqHeaders
    @checkSyncerResults
    def add_user2grp_listener(kwargs, post_funcs):
        instance = kwargs['class'].get(kwargs['id'])
        if instance.group.place:
            onAssignRoles = checkSyncerResults(syncerclient.onAssignRoles)
            onAssignRoles(instance.user.user_name, instance.group.place.id, instance.group.level)
        if instance.group.group_name == "superuser":
            mod_list = syncer.helpers.ldap.object_maps['group'].toLDAP(instance)
            return syncerclient.onGroupMod("superusers", mod_list) # <- it's superusers at ldap
    
    @checkReqHeaders
    @checkSyncerResults
    def tariff_add_listener(kwargs, post_funcs):
        instance = kwargs['class'].get(kwargs['id'])
        mod_list = syncer.helpers.ldap.object_maps['tariff'].toLDAP(instance)
        return syncerclient.onTariffAdd(instance.place.id, mod_list)
    
    ## /sync operations 
    
    def setupLDAPSync():
        # in some situations it's not desired to have sync on right from the server boot. Like in new setups we may want
        # to create initial users before we start syncing.
        print "setup: Enabling LDAP sync"
        listen(usr_add_listener, model.User, RowCreatedSignal)
        listen(usr_updt_listener, model.User, RowUpdateSignal)
        listen(hub_add_listener, model.Location, RowCreatedSignal)
        listen(hub_updt_listener, model.Location, RowUpdateSignal)
        listen(grp_add_listener, model.Group, RowCreatedSignal)
        listen(grp_updt_listener, model.Group, RowUpdateSignal)
        listen(add_user2grp_listener, model.UserGroup, RowCreatedSignal)
        listen(accesspolicy_updt_listener, model.AccessPolicy, RowUpdateSignal)
        listen(accesspolicy_add_listener, model.AccessPolicy, RowCreatedSignal)
        listen(accesspolicy_del_listener, model.AccessPolicy, RowDestroySignal)
        listen(opentimes_add_listener, model.Open, RowCreatedSignal)
        listen(opentimes_updt_listener, model.Open, RowUpdateSignal)
        listen(opentimes_del_listener, model.Open, RowDestroySignal)
        listen(tariff_listener, model.RUsage, RowCreatedSignal)
        listen(tariff_add_listener, model.Resource, RowCreatedSignal)
        
        thread.start_new(signonloop, ())
