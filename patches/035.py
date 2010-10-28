import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "To prevent duplicate invoice numbers"
    def apply(self):
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        cur = con.cursor()
        nonull_sql = "UPDATE invoice SET number = id where number is null;"
        constraint_sql = "ALTER TABLE invoice ADD UNIQUE (number);"
        cur.execute(nonull_sql)
        cur.execute(constraint_sql)
        con.commit()
