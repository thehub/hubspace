import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add company_name to Location - this appears in the Edit Location page. This field helps to re-format invoice format as per Hub Prague's requirement."
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("""alter table location add column company_name VARCHAR(255) default NULL""")
        con.commit()
