import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add is_region field"
    def apply(self):
        return # this patch is now merged with #21
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE location ADD COLUMN is_region int DEFAULT 0")
        con.commit()
