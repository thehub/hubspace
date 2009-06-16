import psycopg2
from optparse import OptionParser
import sys
import cPickle
VERSION='0.1'

#postgres://hubspace:hu3n3t@localhost/hubspace

def doArgs(argv):
    """ Look if you can't guess what this function does, just give up now. """
    global VERSION   
    version = "%%prog %s" % VERSION
    usage ="usage: %prog [options] [site]"
    description="%prog is used to migrate data from SQLite to PostgreSQL."
   
    parser = OptionParser(usage=usage, version=version, description=description)
    parser.add_option("-p", "--pg_uri", dest="pg_uri", type="string",
                        help="DB URI for PostgreSQL database",  
                        metavar="<uri>")
   
    (options, args) = parser.parse_args(argv)

    if not options.pg_uri or not options.pg_uri.startswith('postgres://'):
        print ("You must specify a valid URI for the PostgreSQL database.")
        print ("  eg. postgres://user:password@localhost/dbname")
        sys.exit(1)
 
    options.args = args

    return options


def getPostgreSQLConnection(opts):
    """ Create a connection to the PostgreSQL database """
    #e.g. "postgres://hubspace:hu3n3t@localhost/hubspace" 
    dburi = opts.pg_uri 
    path = dburi.split('://')[1]
    user, password = path.split('@')[0].split(':')
    host, dbname = path.split('@')[1].split('/')
    con = psycopg2.connect("host=%(host)s user=%(user)s password=%(password)s dbname=%(dbname)s" %{'host':host, 'user':user, 'password':password, 'dbname':dbname})
    return con


def fixPickleCols(opts):
    cols = [('tg_user', 'cops'), ('tg_user', 'bristol_metadata'),
            ('resourcegroup', 'resources_order'),
            ('location', 'resourcegroup_order'), ('location', 'messages'), ('location', 'cancellation_charges')]

    def reEncode_col(cnx, col):
        table, col_name = col
        cur = cnx.cursor()
        cur.execute("SELECT id, %(col)s FROM %(table)s;"%(dict(table=table, col=col_name)))
        rows = [row for row in cur]
        print "table: "+ table + "\n col_name: " + col_name
        for id, val in rows:
            print val
            new_val = str(val).decode('base64')
            #check the validity of the decoded pickle
            try:
                print new_val
                d = cPickle.loads(new_val)
            except:
                print "Failed to unpickle id: " + `id` + "\n\n" + new_val
                if col_name=='resourcegroup_order':
                    print "defaulting to []"
                    new_val = cPickle.dumps([])
            #encode it with necessary escapes for binary storage
            new_val = psycopg2.Binary(new_val)
            query = "UPDATE %(table)s SET %(col)s = %(new_val)s WHERE %(table)s.id=%(id)s;"%(dict(table=table, col=col_name, id=id, new_val=new_val))
            cur.execute(query)
        cnx.commit()
    
    cnx = getPostgreSQLConnection(opts)
    for col in cols:
        reEncode_col(cnx, col)

    

def fixSequences(opts):			    
    def getAllTables(cnx):
        """ Queries the sqlite database for a list of tables """
        cur = cnx.cursor()
        cur.execute("""SELECT tablename FROM pg_tables WHERE tablename not like 'sql_%' AND tablename not like 'pg_%'""")
        tables = [t[0] for t in cur]
        cnx.commit()
        return tables

    def syncSequences(cnx, tables):
        for table in tables:
            cur = cnx.cursor()
            try:
                cur.execute("SELECT setval('%(table)s_id_seq', max(id)+1) FROM %(table)s;"%(dict(table=table)))
                cnx.commit()
            except psycopg2.ProgrammingError, e:
                cnx.commit()
                print str(e)
        cnx.commit()
        return "success"

    cnx = getPostgreSQLConnection(opts)
    tables = getAllTables(cnx)
    cnx = getPostgreSQLConnection(opts)
    synced = syncSequences(cnx, tables)
    print synced
    return 




def main(args):
    fixSequences(args)
    fixPickleCols(args)
    
if __name__ == '__main__':
    args = doArgs(sys.argv[1:])
    main(args)
    sys.exit(args)
