import sys
import turbogears
import ldap
import hubspace.sync.export2ldap as export2ldap
import hubspace.model as model
import hubspace.sync as sync

def ldapconnect():
    uri = "ldap://ldap.the-hub.net"
    #uri = "ldap://localhost"
    u = turbogears.config.config.configs['syncer']['hubspaceadminuid']
    p = turbogears.config.config.configs['syncer']['hubspaceadminpass']
    dn = "uid=%s,ou=services,o=the-hub.net" % u
    
    conn = ldap.ldapobject.ReconnectLDAPObject(uri)
    conn.simple_bind_s(dn, p)

    return conn

sync.core.signon()
conn = ldapconnect()

class SyncObject(object):
    hubspace_model = None
    ldap_subtree = ""
    hubspace_id = ""
    ldap_id = ""
    exporters = dict (hubspace = None, ldap = None)
    get_hubspace_obj = lambda self, x: self.hubspace_model.get(x)
    def getHubspaceIds(self):
        select = self.hubspace_model.select()
        ret = set([getattr(u, self.hubspace_id) for u in select])
        if "webapi" in ret: ret.remove("webapi")
        return ret
    def getLDAPIds(self):
        search = conn.search_s(self.ldap_subtree, ldap.SCOPE_ONELEVEL, filterstr='(objectClass=hubGlobalUser)', attrlist=['uid'], attrsonly=0)
        return set([x[1]['uid'][0] for x in search])
        # check sizelimit in slapd config if above fails
    def missingIds(self):
        hubspace_ids = self.getHubspaceIds()
        ldap_ids = self.getLDAPIds()
        return dict (
            ldap = hubspace_ids.difference(ldap_ids),
            hubspace = ldap_ids.difference(hubspace_ids) )
    def exportMissingObjs2LDAP(self):
        missing_ids = self.missingIds()["ldap"]
        print "missing in LDAP: ", missing_ids
        for oid in missing_ids:
            print "\t ", oid
            obj = self.get_hubspace_obj(oid)
            self.exporters['ldap'](obj)
            

class User(SyncObject):
    hubspace_model = model.User
    ldap_subtree = "ou=users,o=the-hub.net"
    hubspace_id = "user_name"
    ldap_id = "uid"
    get_hubspace_obj = lambda self, x: self.hubspace_model.by_user_name(x)
    exporters = dict (ldap = export2ldap.addUser)

def exportMissingUsers2LDAP():
    sync.core.tls.syncer_trs = [] # <- hacky should go
    return User().exportMissingObjs2LDAP()
    #if sync.core.signon():
    #    return User().exportMissingObjs2LDAP()
    #else:
    #    sys.exit("syncer signon failed")


