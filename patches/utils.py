import re, psycopg2, sys

configfile = sys.argv[1:2] or "dev.cfg"

def parseDBURI(cfgfile):
    for line in file(cfgfile):
        line = line.strip()
        if not line.startswith('#') and "sqlobject.dburi" in line:
            return line
      
def parseDBAccessDirective():
    """
    parses sqlobject.dburi line and returns (username, password, host, dbname)
    """
    line = parseDBURI(configfile)
    if line:
        return re.findall(".*//(.*):(.*)@(.*)/(.*)\"", line)[0]

def getPostgreSQLConnection(user, password, host, dbname):
    """ Create a connection to the PostgreSQL database """
    if ':' in host:
        host, port = host.split(':')
    connection_str = "host=%(host)s user=%(user)s password=%(password)s dbname=%(dbname)s" % locals()
    if 'port' in locals():
        connection_str += ' port=%(port)s' %locals()
    return psycopg2.connect(connection_str)

