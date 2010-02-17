import os
from os.path import *
from commands import getoutput

def main():
    import sys
    import pkg_resources
    pkg_resources.require("TurboGears")
    
    # first look on the command line for a desired config file,
    # if it's not on the command line, then
    # look for setup.py in this directory. If it's not there, this script is
    # probably installed

    if len(sys.argv) > 1:
        configfile = sys.argv[1]
    elif exists(join(dirname(__file__), "setup.py")):
        configfile = "dev.cfg"
    else:
        configfile = "prod.cfg"

    lucene_lock = 'index/en/write.lock'
    if exists(lucene_lock):
        os.unlink(lucene_lock)
    # Patch before you start importing etc.
    import patches
    import patches.utils
    patches.utils.configfile = configfile
    updater = patches.Updater()
    updater.update()
    del updater
    del patches

    getoutput('./bin/kidc hubspace/templates')
    import monkeypatch
    import turbogears
    import cherrypy

    cherrypy.lowercase_api = True

    turbogears.update_config(configfile, modulename="hubspace.config")

    staic_target = turbogears.config.config.configs['global']['static_target_dir']
    static_link = turbogears.config.config.configs['/static']['static_filter.dir']

    if os.path.islink(static_link):
        os.remove(static_link)

    os.symlink(staic_target, static_link)
    print "Static link: %s -> %s" % (static_link, staic_target)

    
    def add_sync_filters():
        import hubspace.sync.core
        cherrypy.root._cp_filters.extend(hubspace.sync.core._cp_filters)

    import hubspace.search

    turbogears.startup.call_on_startup.append(add_sync_filters)
    turbogears.startup.call_on_shutdown.append(hubspace.search.stop)

    from hubspace.controllers import Root
    turbogears.start_server(Root())

if __name__ == '__main__':
    main()
