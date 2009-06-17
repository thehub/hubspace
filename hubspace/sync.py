import logging
import time
import turbogears.config
import hubspace.config
import thread
applogger = logging.getLogger("hubspace")

try:
    ldap_sync_enabled = turbogears.config.config.configs['syncer']['sync']
except:
    ldap_sync_enabled = False


if ldap_sync_enabled:
    import syncer
    import syncer.client
    import syncer.config
    
    syncer.config.host = turbogears.config.config.configs['syncer']['syncer_host']
    syncer.config.port = turbogears.config.config.configs['syncer']['syncer_port']
    syncer.config.reload()
    
    _sessions = dict()
    sessiongetter = lambda: _sessions
    
    syncerclient = syncer.client.SyncerClient("hubspace", sessiongetter)
    
    def signon():
        u = turbogears.config.config.configs['syncer']['hubspaceadminuid']
        p = turbogears.config.config.configs['syncer']['hubspaceadminpass']
        tr_id, res = syncerclient.onSignon(u, p)
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
