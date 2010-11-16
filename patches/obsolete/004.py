import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Adds new column for tentative booking feature"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE rusage ADD COLUMN confirmed smallint DEFAULT 1;")
        con.commit()
