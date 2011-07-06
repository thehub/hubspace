import turbogears
import turbogears.config
import cherrypy
import urllib2
import hubspace.model as model

import cherrypy

def get_mimetype(object, attr_name):
   try:
      return getattr(object, attr_name+"_mimetype")
   except:
      return 'image/png'

def image_src(object, attr_name, default_image_location):
   obj_type = object.__class__.__name__
   if obj_type == 'ProfileCache':
       obj_type = 'User'
       object = model.User.get(object.id)
   if isinstance(getattr(object, attr_name), basestring) and isinstance(get_mimetype(object, attr_name), basestring):
       count = cherrypy.session.setdefault('count', 1000)
       cherrypy.session['count'] +=1
       return "/display_image/"+ obj_type +"/" + str(object.id) + "/" + attr_name
   return default_image_location

