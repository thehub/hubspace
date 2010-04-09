import cherrypy

def get_mimetype(object, attr_name):
   try:
      return getattr(object, attr_name+"_mimetype")
   except:
      return 'image/png'
         

def image_src(object, attr_name, default_image_location):
   if isinstance(getattr(object, attr_name), basestring) and isinstance(get_mimetype(object, attr_name), basestring):
       count = cherrypy.session.setdefault('count', 1000)
       cherrypy.session['count'] +=1 
       #return "/display_image/"+ object.__class__.__name__ +"/" + str(object.id) + "/" + attr_name
   return "http://plus.the-hub.net/site_media/avatars/%(user_name)s/resized/180/avatars/%(user_name)s/%(user_name)s" % \
          dict(user_name = object.user_name)
