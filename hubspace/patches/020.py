import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add microsite active field"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE location ADD COLUMN microsite_active int DEFAULT 0")
        con.commit()
