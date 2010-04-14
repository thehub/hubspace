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
    
    if not os.stat(deliverance_dir.endswith('deliverance-src')):
        print "update deliverance: begin"
        cmd = "/bin/cp -auv %s/* %s" % ("deliverance-src", deliverance_dir)
        print "deliverance sync: ", cmd
    os.system(cmd)
    print "deliverance sync: done"
