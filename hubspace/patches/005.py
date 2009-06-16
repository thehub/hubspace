import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Sets hubspace user last_name attribute friendly to LDAP schema"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("UPDATE tg_user SET last_name = ' ' where last_name = '';")
        con.commit()
