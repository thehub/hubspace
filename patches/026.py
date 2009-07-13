import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add is_region field"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE location add column in_region_id INTEGER CONSTRAINT in_region_id_exists REFERENCES location(id)")
        con.commit()
