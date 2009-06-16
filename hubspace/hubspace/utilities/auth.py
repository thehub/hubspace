import logging
from turbogears.identity.soprovider import SqlObjectIdentityProvider
import cherrypy
import turbogears.config

try:
    ldap_sync_enabled = turbogears.config.config.configs['syncer']['sync']
except:
    ldap_sync_enabled = False


if not ldap_sync_enabled:

    class SSOIdentityProvider(SqlObjectIdentityProvider): pass

else:

    import syncer
    import syncer.client
    import syncer.config
    import syncer.utils

    syncer.config.host = turbogears.config.config.configs['syncer']['syncer_host']
    syncer.config.port = turbogears.config.config.configs['syncer']['syncer_port']
    syncer.config.reload()

    sessiongetter = lambda: cherrypy.session
    syncerclient = syncer.client.SyncerClient("hubspace", sessiongetter)


    class SSOIdentityProvider(SqlObjectIdentityProvider):
    
        def validate_identity(self, user_name, password, visit_key):
            ret = super(SSOIdentityProvider, self).validate_identity(user_name, password, visit_key)
            
            applogger = logging.getLogger("hubspace")
            applogger.info("%s, %s" % (ret, syncerclient.isSyncerRequest(cherrypy.request.headers.get("user-agent", None))))
            if ret and not syncerclient.isSyncerRequest(cherrypy.request.headers.get("user-agent", None)):
                cookies = syncer.utils.convertCookie(cherrypy.request.simple_cookie)
                t_id, res = syncerclient.onSignon(user_name, password, cookies)
    
                if not syncerclient.isSuccessful(res):
                    print syncer.client.errors.res2errstr(res)
                    return None
    
                syncerclient.setSyncerToken(res['sessionkeeper']['result'])
    
                cookies = syncer.utils.mergeSimplecookies(cherrypy.request.simple_cookie, cherrypy.response.simple_cookie)
                syncerclient.onReceiveAuthcookies(syncerclient.appname, user_name, cookies)
    
            return ret
