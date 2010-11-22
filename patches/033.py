import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Purchase Order Numbers for Invoices"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE invoice ADD COLUMN ponumbers bytea")
        con.commit()
