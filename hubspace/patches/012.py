import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add new locale field to location"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE location ADD COLUMN locale character varying(8) DEFAULT 'en'")
        con.commit()
