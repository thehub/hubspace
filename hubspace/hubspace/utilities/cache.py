import cherrypy

def strongly_expire(func):
    """Decorator that sends headers that instruct browsers and proxies not to cache.
    """
    def newfunc(*args, **kwargs):
        cherrypy.response.headers['expires'] = 'Sun, 19 Nov 1978 05:00:00 GMT' #'-1'
        cherrypy.response.headers['cache-control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=-1'
        cherrypy.response.headers['pragma'] = 'no-cache, no-store',
        return func(*args, **kwargs)
    return newfunc
