#from turbogears import testutil
#import cherrypy
#from hubspace.controllers import Root

def xtest_method():
    ""
    root = Root()
    cherrypy.root = Root()
    d = testutil.create_request('/index')
    assert d["newvalue"] == 10


def xtest_indextitle():
    "The mainpage should have the right title"
    testutil.createRequest("/")
    assert "<TITLE>Welcome to TurboGears</TITLE>" in cherrypy.response.body[0]

