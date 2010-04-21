import turbogears
import turbogears.config
import cherrypy
import urllib2

AVATAR_INTEGRATION_ENABLED = turbogears.config.config.configs['avatar']['enable_integration']

def get_mimetype(object, attr_name):
   try:
      return getattr(object, attr_name+"_mimetype")
   except:
      return 'image/png'

if AVATAR_INTEGRATION_ENABLED:

    def image_src(object, attr_name, default_image_location):
        obj_type = object.__class__.__name__
        if obj_type == 'User':
            return "http://plus.the-hub.net/avatar/current/%s/100/" % object.user_name
        elif isinstance(getattr(object, attr_name), basestring) and isinstance(get_mimetype(object, attr_name), basestring):
            count = cherrypy.session.setdefault('count', 1000)
            cherrypy.session['count'] +=1 
            return "/display_image/"+ obj_type +"/" + str(object.id) + "/" + attr_name
        return default_image_location
else:

    def image_src(object, attr_name, default_image_location):
       if isinstance(getattr(object, attr_name), basestring) and isinstance(get_mimetype(object, attr_name), basestring):
           count = cherrypy.session.setdefault('count', 1000)
           cherrypy.session['count'] +=1
           return "/display_image/"+ object.__class__.__name__ +"/" + str(object.id) + "/" + attr_name
       return default_image_location


