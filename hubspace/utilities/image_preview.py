from PIL import Image
import StringIO


def create_image_preview(file_object, **kwargs):    

    height = None
    width = None
    if "height" in kwargs and "width" in kwargs:
        height = kwargs['height']
        width = kwargs['width']
    
    preview = resize_image(file_object, height, width)
    return preview

def resize_image(file_object, height, width):
    """resizes images to fit in the height and width
    """
    
    im = Image.open(file_object).convert('RGB')
    if float(height) > im.size[1] and float(width)> im.size[0]:
        pass
    else:
        im = crop_image(im, height, width) 
        im.thumbnail((int(width), int(height)), Image.ANTIALIAS)
    
    thumb = StringIO.StringIO()
    im.save(thumb, 'png') 
    thumb.seek(0)
    return thumb


def crop_image(im, height, width, valign="center", halign="center"):

    new_ratio = float(height)/float(width)
    old_ratio = float(im.size[1])/float(im.size[0])

    new_height = None
    new_width = None

    if new_ratio>old_ratio:
        new_width = max(width, im.size[1]/new_ratio)
    elif new_ratio<old_ratio:
        new_height = max(height, im.size[0]*new_ratio)
    else:
        return im
        
    if valign=="center" and new_height:
        cut = ((im.size[1]-new_height)/2.0)
        im = im.crop(box=(0, int(cut), im.size[0], int(im.size[1]-cut-1)))
        #raise `cut` + "height"

    if halign=="center" and new_width:
        cut = ((im.size[0]-new_width)/2.0) 
        #raise `im.size[0]` + `new_width` +`cut`
        im = im.crop(box=(int(cut), 0, int(im.size[0]-cut-1), im.size[1]))
    return im


