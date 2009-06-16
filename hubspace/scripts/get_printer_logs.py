#!/usr/bin/python2.4

import urllib2
import os

from datetime import datetime
date = datetime.now().strftime('%d.%m.%y')


#this should be crontabbed on london.the-hub.net. It must be on a machine which
#has access to both the web and the the hub london LAN

def get_printer_log():
    """Get printer logs from the printer and place them in:
    /var/backup/parse_print/jobacct.csv

    Only works if you are within the hub london lan
    """
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, 'http://192.168.1.238', 'hublondon', 'hublondon')
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    log=opener.open('http://192.168.1.238/jobacct.dat')
  
    local_copy = file('/var/backup/print_parse/jobacct.csv.'+ date, 'w')
    local_copy.write(log.read())
    local_copy.close()
    log.close()
    return local_copy

def send_log_to_hubspace():
    """Upload the log file to the place where hubspace reads it from:

           trunk/hubspace/printing/jobs.csv
           
    """

    os.system('curl -F "user_name=webapi" -F "password=test" -F "login=Login" -F log=@/var/backups/print_parse/jobacct.csv.'+date + ' members.the-hub.net/upload_printer_log')
    

log = get_printer_log()
send_log_to_hubspace()

