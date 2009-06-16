import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add new location, invoice attributes"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE location DROP COLUMN invoice_start")
        cur.execute("ALTER TABLE location ADD COLUMN invoice_newscheme int DEFAULT 0")
        con.commit()
