from turbogears import identity, redirect
import sendmail
import cherrypy
from hubspace.feeds import get_updates_data
from hubspace.utilities.i18n import get_location_from_base_url
from hubspace.utilities.permissions import is_host
from hubspace.model import User
import md5, random

def login_args(previous_url=None, *args, **kwargs):
    forward_url=None
    if 'forward_url' in kwargs:
        forward_url = kwargs['forward_url']
    if identity.was_login_attempted():
        cherrypy.response.status=403
        msg=_("Your username or password were incorrect. "
              "Please try again.")
    elif identity.get_identity_errors():
        msg=_("Please log in.")
    else:
        msg=_("Please log in.")
        forward_url=cherrypy.request.headers.get("Referer", "/")
    try:    
        location = get_location_from_base_url()
        updates = get_updates_data(location)
    except:
        location = None
        updates = None
    if (not identity.current.anonymous and identity.current.user.active) and not (is_host(identity.current.user, location) and not identity.was_login_attempted()):
        redirect(cherrypy.request.base)
    login_dict = dict(login_message=msg, previous_url=previous_url, logging_in=True,
                      original_parameters=cherrypy.request.params,
                      forward_url=forward_url, updates=updates, location=location)
    return login_dict


def requestPassword(*args, **kwargs):
    if kwargs.get('submit') == "Get Password":
        mode = "pword"
    else:
        mode = "uname"            
    email = None
    if 'email' in kwargs:
        email = kwargs['email']
    if not email:
        return dict(message=_("Please enter the email address associated with your account"),
                    showform=True)
    result = User.select(User.q.email_address==email)
            
    try:
        if mode == "uname":
            user = result[0]
            mailtext = "Dear %(first_name)s,\n\nYour username is: %(user_name)s\n\nYou can login at:\n\n%(request_url)s/public/login\n\nIf you have any questions, please contact The Hub's hosting team at %(location_name)s.hosts@the-hub.net or phone %(telephone)s.\n\nThank you very much.\n\nThe Hosting Team" %({'first_name':user.first_name, 'request_url':cherrypy.request.base, 'user_name':user.user_name, 'location_name':user.homeplace.name.lower().replace(' ', ''), 'telephone':user.homeplace.telephone})
            
            sendmail.sendmail(email, user.homeplace.name.lower().replace(' ', '') +'.hosts@the-hub.net','The Hub | username reminder',mailtext,[])
            return dict(message=_("""A confirmation email was sent to you. """),
                        showform=False)
        else:
            user = result[0]
            reminderkey = md5.new(str(random.random())).hexdigest()
            user.reminderkey = reminderkey
            mailtext = "Dear %(first_name)s,\n\nPlease click the link to reset your password:\n\n %(request_url)s/public/resetPassword?key=%(reminderkey)s\n\nIf you have any questions, please contact The Hub's hosting team at %(location_name)s.hosts@the-hub.net or phone %(telephone)s.\n\nThank you very much.\n\nThe Hosting Team" %({'first_name':user.first_name, 'request_url':cherrypy.request.base, 'reminderkey':reminderkey, 'location_name':user.homeplace.name.lower().replace(' ', ''), 'telephone':user.homeplace.telephone})
            
            sendmail.sendmail(email, user.homeplace.name.lower().replace(' ', '') +'.hosts@the-hub.net','The Hub | password reminder',mailtext,[])
            return dict(message=_("""A confirmation email was sent to you. """),
                        showform=False)
    except IndexError:            
        return dict(message=_("The email was not correct"),
                               showform=True)


def resetPassword(*args,**kwargs):
    key=kwargs['key']
    result = User.selectBy(reminderkey=key)
    if result.count()==0:
        return dict(message=_("The confirmation key is wrong - maybe you need to check your email?"),
                    showform=False)
    else:
        user=result[0]
        user.reminderkey = md5.new(str(random.random())).hexdigest()	    
        newpassword = md5.new(str(random.random())).hexdigest()[:8]
        user.password = newpassword 
        mailtext = """
Dear Member,

Your new password for The Hub is: %(newpassword)s

For your convenience and security please login and change the password at the earliest possible opportunity. To do so click 'edit' on the top section of your profile page and enter a new password in the 'password' and 'confirm password' fields.
You can login at:
%(url)s

The Hub Team
"""%({'newpassword':newpassword, 'url':user.homeplace.url})
    sendmail.sendmail(user.email_address, user.homeplace.name.lower().replace(' ', '') +'.hosts@the-hub.net','The Hub | new password',mailtext,[])
    return dict(message=_("""The new password was sent to you."""), showform=False)
