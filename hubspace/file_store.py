from model import LocationFiles, MetaWrapper
from hubspace.utilities.image_preview import create_image_preview
import os
import StringIO
from sqlobject import AND
import logging
applogger = logging.getLogger("hubspace")

def save_file(location, fd, height=None, width=None, upload_dir=''):
    """here we will need to get the mime type in the various way here
    - attr is the filename
    """
    if "image/" in fd.type:
        #try:
            mime_type, file_name = save_image(location, fd, height, width, upload_dir)
        #except:
        #    raise "There was an error saving the image"
    else:
        raise "unexpected content type" + `image.type`

    return LocationFiles(location=location, attr_name=file_name, mime_type=mime_type)

def get_filepath(obj, prop, upload_dir, default=''):
    """obj should usually be a MetaWrapper
    """
    prop_val = getattr(obj, prop)
    try:
        val = int(prop_val)
    except:
        return default
    return upload_dir + LocationFiles.get(val).attr_name

def locally_unique_file_name(file_name, location):
    """give a file_name test.png it should iterate through test-1.png, test-2.png etc until we reach a unique one.
    """
    if LocationFiles.select(AND(LocationFiles.q.locationID==location, LocationFiles.q.attr_name==file_name)).count():
        file_name = file_name.rsplit('.', 1)
        extra = file_name[-2].rsplit('-', 1)
        try:
            extra[-1] = str(int(extra[-1])+1)
            extra = '-'.join(extra)
            file_name[-2] = extra
            return locally_unique_file_name('.'.join(file_name), location)
        except ValueError:
            extra[-1] += '-1'
            file_name[-2] = '-'.join(extra)
            return locally_unique_file_name('.'.join(file_name), location)            
        file_name = '.'.join(file_name)    
    return file_name

def save_image(location, fd, height, width, upload_dir):
    image = create_image_preview(fd.file, height=height, width=width)

    file_name = fd.filename 
    file_name = file_name.split('.')[0] + '.png'
    file_name = locally_unique_file_name(file_name, location)

    applogger.debug("microsite: saving image at: %s%s" % (upload_dir, file_name))
    file = open(upload_dir + file_name, 'w')
    file.write(image.read())
    file.close()
    return ('image/png', file_name)

def file_exists(location, file_name, path=''):
    """this is untested and probably not going to be used
    """
    try:
        LocationFiles.select(AND(LocationFiles.q.locationID==location,
                                 LocationFiles.q.attr_name==attr_name))[0]
        os.stat(path + attr_name)
        return True
    except:
        return False
