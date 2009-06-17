import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add new columns for booking cacellations"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE location ADD COLUMN vat_included smallint DEFAULT 1;")
        cur.execute("ALTER TABLE location ADD COLUMN rfid_enabled smallint DEFAULT 0;")
        con.commit()
