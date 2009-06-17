import patches.base
from pysqlite2 import dbapi2 as sqlite

class Patch(patches.base.Patch):
    description = "Adds new columns to location table"
    def apply(self):
        con = sqlite.connect("hubdata.sqlite")
        select = "select * from location;"
        cur = con.cursor()
        res = cur.execute(select)
        res.description
        if 'homepage_title' in (col[0] for col in res.description):
            patches.base.showmsg("Table location already has new columns")
        else:
            cur = con.cursor()
            cur.executescript("""
            alter table location add column homelogo_mimetype VARCHAR(15);
            alter table location add column homepage_title VARCHAR(40);
            alter table location add column homepage_description TEXT;
            """)
        con.commit()
