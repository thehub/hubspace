#!/usr/bin/python2.4

#If the database is malformed (version issue) =>
#sqlite3 hubd .dump | sqlite3 trac.db

#svn up and then run this script
from pysqlite2 import dbapi2 as sqlite
from os import system

def update_schema(con):
    cur = con.cursor()    
    cur.executescript("""
    alter table tg_user add column public_field TINYINT;
    alter table tg_user add column modified TIMESTAMP;
    alter table rusage add column public_field TINYINT;
    alter table rusage add column meeting_description TINYINT;
    create table open(
      id INTEGER PRIMARY KEY,
      location_id INT CONSTRAINT location_id_exists REFERENCES location(id),
      day INTEGER,
      date DATE,
      t_open TIME, 
      t_close TIME
    );
    create table resourcegroup(
      id INTEGER PRIMARY KEY,
      name TEXT,
      description TEXT,
      location_id INT CONSTRAINT location_id_exists REFERENCES location(id),
      resources_order VARCHAR(65537)
    );
    alter table location add column resourcegroup_order VARCHAR(65537);
    alter table resource add column resgroup_id INT CONTSTRAINT resgroup_id_exists REFERENCES resourcegroup(id);
    alter table resource add column resimage_mimetype VARCHAR(15);
    """)
    con.commit()


if __name__ == "__main__":
    con = sqlite.connect("../hubdata.sqlite")
    update_schema(con)

