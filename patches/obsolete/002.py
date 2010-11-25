import patches.base
from pysqlite2 import dbapi2 as sqlite
from patches.postgres_migration.migrate import migrate
#from hubspace.model import User

class Patch(patches.base.Patch):
    description = "Migrates data to postgres taking care of permissions and data incompatibilities etc"
    #remove UserMetaData and Selections which refer to deleted users (in sqlite)
    def remove_fkey_violations(self):
        con = sqlite.connect("hubdata.sqlite")
        cur = con.cursor()
        mdata = cur.execute("SELECT * FROM user_meta_data")
        for mdat in mdata:
            cur = con.cursor()
            user = cur.execute("SELECT * FROM tg_user where id=%s" %(str(mdat[1])))
            user = [u for u in user]
            if not user:
                print `mdat[1]`
                cur = con.cursor()
                cur.execute("DELETE FROM user_meta_data WHERE user_id=%s" %(str(mdat[1])))
        con.commit()

    def apply(self):
        self.remove_fkey_violations()
        migrate()
