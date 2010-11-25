import sys
sys.path.extend(['develop-eggs/PIL-1.1.6-py2.7-linux-i686.egg', 'develop-eggs/pycairo-1.8.10-py2.7-linux-i686.egg'])

reload(sys)
sys.setdefaultencoding('utf-8')
del sys.setdefaultencoding
print "default encoding: utf-8"

#monkeypatch cherrypy, see
#http://trac.turbogears.org/turbogears/ticket/1022
import cherrypy

def our_decode(self, enc):
    def decodeit(value, enc):
        if hasattr(value,'file'):
            return value
        elif isinstance(value,list):
            return [decodeit(v,enc) for v in value]
        elif isinstance(value,dict):
            for k,v in value.items():
                value[k] = decodeit(v,enc)
            return value
            #return value here?
        else:
            return value.decode(enc)
            
    decodedParams = {}
    
    for key, value in cherrypy.request.params.items():
        decodedParams[key] = decodeit(value,enc)
    
    cherrypy.request.params = decodedParams

from cherrypy.filters.decodingfilter import DecodingFilter

DecodingFilter.decode = our_decode

