import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add new columns for vat on invoice"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE invoice ADD COLUMN vat_included smallint")
        con.commit()
