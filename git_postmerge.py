import os
import turbogears

turbogears.update_config("dev.cfg", modulename="hubspace.config")

staic_target = turbogears.config.config.configs['global']['static_target_dir']
static_link = turbogears.config.config.configs['/static']['static_filter.dir']

def main():
    if not staic_target.endswith("hubspace/static-src"):
        print "static sync: begin"
        cmd = "/bin/cp -auv %s/* %s" % ("hubspace/static-src", staic_target)
        print "static sync: ", cmd
        print "static sync: done"
    os.system(cmd)

