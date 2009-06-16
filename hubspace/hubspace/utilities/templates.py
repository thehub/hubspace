from kid.template_util import TemplateNotFound
from turbogears.view import render 

def try_render(template_args, folder_paths=None, **kwargs):
    if folder_paths:
        temp = kwargs['template']
        for path in folder_paths:
            try:
                kwargs['template'] = path + temp
                return render(template_args, **kwargs)
            except ImportError:
                raise "module "+path+ " doesn't exist"
            except TemplateNotFound:
                pass
        raise "template not found " + kwargs['template']
    else:
        return render(template_args, **kwargs)
