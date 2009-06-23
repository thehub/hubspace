import logging
import time
import turbogears.config
import hubspace.config
from turbogears.identity.soprovider import SqlObjectIdentityProvider
import thread
applogger = logging.getLogger("hubspace")

try:
    ldap_sync_enabled = turbogears.config.config.configs['syncer']['sync']
except:
    ldap_sync_enabled = False


SSOIdentityProvider = SqlObjectIdentityProvider

if ldap_sync_enabled:
    import syncer
    import syncer.client
    import syncer.config
    import syncer.utils
    import cherrypy
    
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

            return iden

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

    thread.start_new(signonloop, ())
