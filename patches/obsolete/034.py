import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add new column for recursive event booking id"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("ALTER TABLE rusage ADD COLUMN repetition_id int;")
        con.commit()
