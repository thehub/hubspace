#!/usr/bin/python2.4

import os, sys, re
from commands import getstatusoutput, getstatus
from sequences_sync import getPostgreSQLConnection
from sequences_sync import main

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self


def migrate():
    #Dump the sqlite db
    status, output = getstatusoutput('sqlite3 ./hubdata.sqlite .dump > hubdata2.dump')
    print output
    #Remove the old create tables statements
    from remove_create_statements import remove_create_statements
    remove_create_statements()

    #change the postgres conf file to allow non-unix users to login
    try:
        pg_conf = open("/etc/postgresql/8.3/main/pg_hba.conf")
    except:
        sys.exit("please run the script as root")
    confs = pg_conf.read()
    confs = re.sub("local[ ]+all[ ]+all[ ]+ident[ ]+sameuser", "local   all   all   md5", confs)

    pg_conf.close()
    pg_conf = open("/etc/postgresql/8.3/main/pg_hba.conf", "w")
    pg_conf.write(confs)
    pg_conf.close()
    status, output = getstatusoutput("sudo /etc/init.d/postgresql-8.3 restart")
    print output

    pg_user = raw_input("please enter your username for the new db: ")
    pg_pass = raw_input("please enter your password for the new db: ")
    #create database hubspace with 'user' and 'password';
    status, output = getstatusoutput("sudo -u postgres psql -c 'drop database hubspace;'")
    print output
    status, output = getstatusoutput("""sudo -u postgres psql -c "CREATE USER %(user)s WITH PASSWORD '%(password)s';" """ %(dict(user=pg_user, password=pg_pass)))
    print output
    status, output = getstatusoutput("sudo -u postgres psql -c 'CREATE DATABASE hubspace WITH OWNER %(user)s;'" %(dict(user=pg_user)))
    print output
    pg_uri = "postgres://%(user)s:%(password)s@localhost/hubspace" %(dict(user=pg_user, password=pg_pass))


    uri = AttrDict(pg_uri=pg_uri)
    print uri
    conn = getPostgreSQLConnection(uri)
    cur = conn.cursor()
    print "creating new schema"
    dump = file('./patches/postgres_migration/tables.txt')
    cur.execute(dump.read())
    dump.close()
    conn.commit()

    print "migrating table contents - this may take a while - have a cup of coffee"
    status, output = getstatusoutput("sudo -u postgres psql hubspace -f /tmp/postgres_compatible.dump")
    print output
    if status is not 0:
        errmsg = "migrating table contents failed. You may want to fix it before you rush for the cofee.\n"
        print errmsg
        raise Exception("migrating failed")
    #open("migration.log", "w").write(output).close()

    #copy the dev_sample.cfg to dev.cfg
    from shutil import copyfile
    print "copying dev_sample.cfg to dev.cfg"
    copyfile('./dev_sample.cfg', './dev.cfg')

    #edit the dev.cfg commenting the sqlite db and adding the username and password
    print "rewriting dev.cfg"
    dev_cfg = open('./dev.cfg', 'r+')
    new_conf = re.sub('#sqlobject.dburi="postgres://user:password', 'sqlobject.dburi="postgres://%(user)s:%(password)s' %(dict(user=pg_user, password=pg_pass)), dev_cfg.read())
    new_conf = re.sub(re.compile('^sqlobject.dburi="sqlite:/', re.M), '#sqlobject.dburi="sqlite:/', new_conf)
    dev_cfg.seek(0)
    dev_cfg.write(new_conf)
    dev_cfg.close()
    main(uri) 


#todo
#----
#change installation instructions - packages -> postgres 8.2 (ubuntu/debian)
#write postgres migrate instructions for shekhar

#when updating production ---
#correct \\\ quotes

