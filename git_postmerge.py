import os
import turbogears

turbogears.update_config("dev.cfg", modulename="hubspace.config")

staic_target = turbogears.config.config.configs['global']['static_target_dir']
static_link = turbogears.config.config.configs['/static']['static_filter.dir']

deliverance_dir = turbogears.config.config.configs['deliverance']['deliverance.dir']

def main():
    if not staic_target.endswith("hubspace/static-src"):
        print "static sync: begin"
        cmd = "/bin/cp -auv %s/* %s" % ("hubspace/static-src", staic_target)
        print "static sync: ", cmd
	os.system(cmd)
        print "static sync: done"
    """
    if not deliverance_dir.endswith('deliverance-src'):
        print "update deliverance: begin"
        cmd = "/bin/cp -auv %s/* %s" % ("deliverance-src", deliverance_dir)
        print "deliverance sync: ", cmd
        os.system(cmd)
        deliv_packages = os.path.join(deliverance_dir, 'Deliverance/lib/python2.5/site-packages/')
        try:
            os.stat(deliv_packages)
            cmd = "/bin/cp deliverance-src/myrefs.py %s\n /bin/cp deliverance-src/hubconfig.py %s" %(deliv_packages, deliv_packages)
            os.system(cmd)
        except os.error:
            print "%s does not exist" %(deliv_packages)
        print "deliverance sync: done"
        """
