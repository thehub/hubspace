import sys
reload(sys)
sys.setdefaultencoding('utf-8')
del sys.setdefaultencoding

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
