#!/usr/bin/python2.4

#svn up and then run this script
from pysqlite2 import dbapi2 as sqlite
from os import system

def update_schema(con):
    cur = con.cursor()
    cur.executescript("""
    create table user_meta_data(
      id INTEGER PRIMARY KEY,
      user_id INT CONSTRAINT user_id_exists REFERENCES tg_user(id),
      attr_name VARCHAR(40),
      value TEXT
    );
    create table selection(
      id INTEGER PRIMARY KEY,
      user_id INT CONSTRAINT user_id_exists REFERENCES tg_user(id),
      attr_name VARCHAR(40),
      value INTEGER
    );
    alter table todo add column action TEXT;
    update todo set action = 'edit';
    alter table todo add column action_id INT;
    alter table tg_user add column welcome_sent TINYINT;
    update tg_user set welcome_sent = 1;
    alter table tg_user add column signedby_id INT CONSTRAINT signedby_id_exists REFERENCES tg_user(id);
    alter table tg_user add column hostcontact_id INT CONSTRAINT hostcontact_id_exists REFERENCES tg_user(id);
    alter table note add column action_id INT CONSTRAINT action_id_exists REFERENCES todo(id);
    """)
    con.commit()


    
if __name__ == "__main__":
    con = sqlite.connect("../hubdata.sqlite")
    update_schema(con)

