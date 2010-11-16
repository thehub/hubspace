import patches.base
import patches.utils

class Patch(patches.base.Patch):
    description = "New attribute related to avatar integration"
    def apply(self):
        # This is copied from patch #25
        access_tuple = patches.utils.parseDBAccessDirective()
        con = patches.utils.getPostgreSQLConnection(*access_tuple)
        dburi = patches.utils.parseDBURI('dev.cfg').split('=')[1][1:-1]

        cur = con.cursor()
        sql = "ALTER TABLE tg_user ADD has_avatar boolean default False"
        cur.execute(sql)
        con.commit()
        database.run_with_transaction(create_subpage_lists)
