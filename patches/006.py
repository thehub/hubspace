import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add new columns for booking cacellations"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE rusage ADD COLUMN cancelled smallint DEFAULT 0;")
        cur.execute("ALTER TABLE rusage ADD COLUMN refund smallint DEFAULT 0;")
        cur.execute("ALTER TABLE rusage ADD COLUMN refund_for int;")
        con.commit()
