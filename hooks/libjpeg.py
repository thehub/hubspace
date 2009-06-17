import os
def premake(options, buildout):
    """libjpeg install assumes its prefix has bin, lib, ... dirs; make them.
    """
    libjpeg_location = buildout['libjpeg']['location']
    dirs = ("bin", "man/man1", "lib", "include")
    for dir in dirs:
        os.makedirs('%s/%s' % (libjpeg_location, dir)) 
