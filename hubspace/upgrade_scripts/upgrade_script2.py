#!/usr/bin/python2.4

#svn up and then run this script
from pysqlite2 import dbapi2 as sqlite
from os import system

def update_schema(con):
    cur = con.cursor()
    cur.executescript("""
    alter table location add column timezone VARCHAR(40);
    alter table location add column company_no VARCHAR(40);
    alter table location add column url VARCHAR(40);
    alter table location add column vat_no VARCHAR(40);
    alter table location add column telephone VARCHAR(40);
    alter table location add column account_no VARCHAR(40);
    alter table location add column bank VARCHAR(40);
    alter table location add column sort_code VARCHAR(40);
    alter table location add column iban_no VARCHAR(40);
    alter table location add column swift_no VARCHAR(40);
    alter table location add column payment_terms TEXT;
    alter table invoice add column location_id INT CONSTRAINT location_id_exists REFERENCES location(id);
    delete from invoice;
    delete from rusage where invoice_id is not null;
    alter table tg_user add column image_mimetype VARCHAR(15);
    update tg_user set image_mimetype = mimetype;
    alter table location add column invlogo_mimetype VARCHAR(15);
    alter table location add column logo_mimetype VARCHAR(15);
    alter table rusage add column new_resource_description TEXT;
    """)
    con.commit()


    
if __name__ == "__main__":
    con = sqlite.connect("hubdata.sqlite")
    update_schema(con)

