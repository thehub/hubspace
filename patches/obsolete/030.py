import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "Add invoice bcc email field to Location - this appears in the Edit Location page. This field helps to send the invoice by bccing (to may be account)."
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        cur.execute("""alter table location add column invoice_bcc VARCHAR(255) default NULL""")
        con.commit()
