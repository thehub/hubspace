import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add new location, invoice attributes"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE location ADD COLUMN tentative_booking_enabled smallint DEFAULT 1")
        cur.execute("ALTER TABLE location ADD COLUMN invoice_start int DEFAULT NULL")
        cur.execute("ALTER TABLE invoice ADD COLUMN number int DEFAULT NULL")
        con.commit()
