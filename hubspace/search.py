import os
import logging
from whoosh.qparser import QueryParser
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
import hubspace.model as model
from hubspace.utilities.uiutils import get_freetext_metadata
from hubspace.utilities.dicts import AttrDict

applogger = logging.getLogger("hubspace")

indexdir = "indexdir"
props = ['id', 'user_name', 'display_name', 'description', 'organisation', 'biz_type']
schema = Schema(id=ID(stored=True, unique=True), user_name=TEXT(stored=True), display_name=TEXT(stored=True), description=TEXT(), organisation=TEXT(stored=True), biz_type=TEXT(stored=True))
mparser = MultifieldParser(["display_name", "user_name", "organisation", "id", "description"], schema=schema)

def user2dict(user):
    d = dict([(prop, unicode(getattr(user, prop, None))) for prop in props])
    d['biz_type'] = get_freetext_metadata(user, 'biz_type')
    return d

def populate():
    print "Populating whoosh..."
    for user in model.User.select():
        writer.add_document(**user2dict(user))
    writer.delete_by_term("user_name", "webapi")
    writer.commit()
    print "Populating whoosh: Done"

def do_search(qry_text):
    qry_text = unicode(qry_text)
    qry = mparser.parse(qry_text)
    searcher = ix.searcher()
    return [AttrDict(item) for item in searcher.search(qry, sortedby="display_name")]

def add(user):
    try:
        writer.add_document(**user2dict(user))
        writer.commit()
    except Exception, err:
        applogger.exception("indexing user '%s' failed: " % user.user_name)
        return False
    return True

def update(user):
    try:
        writer.update_document(**user2dict(user))
        writer.commit()
    except Exception, err:
        applogger.exception("search: updating user '%s' failed: " % user.user_name)
        return False
    return True

def remove(user_name):
    writer.delete_by_term("user_name", user_name)
    writer.commit()
    return True

def sync():
    User.select()
    raise NotImplemented
    return True

if not os.path.exists(indexdir):
    os.mkdir(indexdir)
    ix = create_in(indexdir, schema)
    writer = ix.writer()
    populate()
else:
    ix = open_dir(indexdir)
    writer = ix.writer()

def stop():
    global writer
    del writer # required?
    ix.close()
    ix.unlock()
    print "search shutdown"

if __name__ == '__main__':
    def test():
        def timer(fn, args, n=1):
            import datetime
            start = datetime.datetime.now()
            for x in range(n):
                fn(*args)
            return datetime.datetime.now() - start
    
        qry_text = "shon"
        print do_search(qry_text)
        N = 1000
        print "whoosh"
        print timer(do_search, [qry_text], N)
