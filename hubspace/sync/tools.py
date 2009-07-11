import hubspace.model as model
import turbogears
import ldap
import hubspace.sync as sync
import hubspace.sync.export2ldap as export2ldap

def ldapconnect():
    uri = "ldap://ldap.the-hub.net"
    #uri = "ldap://localhost"
    u = turbogears.config.config.configs['syncer']['hubspaceadminuid']
    p = turbogears.config.config.configs['syncer']['hubspaceadminpass']
    dn = "uid=%s,ou=services,o=the-hub.net" % u
    
    conn = ldap.ldapobject.ReconnectLDAPObject(uri)
    conn.simple_bind_s(dn, p)

    return conn

conn = ldapconnect()

class SyncObject(object):
    hubspace_model = None
    ldap_subtree = ""
    hubspace_id = ""
    ldap_id = ""
    ldap_exporter = None
    get_hubspace_obj = lambda x: self.hubspace_model.get(x)
    def getHubspaceIds(self):
        select = self.hubspace_model.select()
        return set([getattr(u, self.hubspace_id) for u in select])
    def getLDAPIds(self):
        return set([x[0] for x in conn.search_s(self.ldap_subtree, ldap.SCOPE_ONELEVEL,
            filterstr='(objectClass=hubGlobalUser)', attrlist=['uid'], attrsonly=1)])
        # check sizelimit in slapd config if above fails
    def missingIds(self):
        hubspace_ids = self.getHubspaceIds()
        ldap_ids = self.getLDAPIds()
        return dict (
            hubspace = hubspace_ids.difference(ldap_ids),
            ldap = ldap_ids.difference(hubspace_ids) )
    def exportMissingObjs2LDAP(self):
        missing_ids = self.missingIds()["ldap"]
        print "missing in LDAP: ", missing_ids
        for oid in missing_ids:
            obj = self.get_hubspace_obj(oid)
            self.ldap_exporter(obj)
            

class User(SyncObject):
    hubspace_model = model.User
    ldap_subtree = "ou=users,o=the-hub.net"
    hubspace_id = "user_name"
    ldap_id = "uid"
    get_hubspace_obj = lambda x: self.hubspace_model.by_user_name(x)
    ldap_exporter = export2ldap.addUser

def exportMissingUsers2LDAP():
    return User().exportMissingObjs2LDAP()


