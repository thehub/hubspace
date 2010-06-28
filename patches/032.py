import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "EU Tax exemption processing"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("""CREATE TABLE eu_tax_exemption (location_id INT NOT NULL, user_id INT NOT NULL)""")
        cur.execute("ALTER TABLE invoice ADD COLUMN rusages_cost_and_tax bytea")
        cur.execute("ALTER TABLE invoice ADD eu_vat_exempted boolean default False")
        con.commit()
