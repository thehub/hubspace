#!/usr/bin/python2.4

#If the database is malformed (version issue) =>
#sqlite3 hubd .dump | sqlite3 trac.db

#svn up and then run this script
from pysqlite2 import dbapi2 as sqlite
from os import system

def update_schema(con):
    cur = con.cursor()    
    cur.executescript("""
    alter table location add column homelogo_mimetype VARCHAR(15);
    alter table location add column homepage_title VARCHAR(40) DEFAULT "";
    alter table location add column homepage_description TEXT DEFAULT "";
    """)
    con.commit()


if __name__ == "__main__":
    con = sqlite.connect("../hubdata.sqlite")
    update_schema(con)

