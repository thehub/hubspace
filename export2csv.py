"""
Sqlobject instances => CSV by location
"""
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import datetime, time, os
import itertools, csv, codecs

import turbogears
turbogears.update_config(configfile="dev.cfg", modulename="hubspace.config")
from hubspace import model

instance2kw = lambda o: {'class':o.__class__, 'id':o.id}

def main():

    select = model.User.select(orderBy='homeplaceID')
    grouped = itertools.groupby(select, lambda u: u.homeplace.name)
    #usersbyplace = list(grouped)
    csvdir = "csv"
    if not os.path.exists(csvdir): os.makedirs(csvdir)
    for placename, users in grouped:
        print "%s Writing data" % placename
        rows = [(u.display_name, u.active, u.email_address, u.website, u.work, u.home, u.mobile, u.organisation, u.address) for u in list(users)]
        rows.insert(0, ("Display Name", "Active", "Email Address", "Website", "Telephone (work)", "Telephone (Home)" "Mobile", "Organisation", "Address"))
        out = file("%s/%s.csv" % (csvdir, placename), "w")
        writer = csv.writer(out, lineterminator='\n')
        #writer.encoder = codecs.getincrementalencoder("utf-8")()
        writer.writerows(sorted(rows))
    print "Find files in %s" % os.path.abspath(csvdir)
