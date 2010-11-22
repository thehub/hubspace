import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Invoicing improvements"
    def apply(self):
        # This is copied from patch #25
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE location ADD COLUMN invoice_duedate int DEFAULT 0")
        con.commit()

