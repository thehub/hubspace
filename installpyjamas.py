import os
import sys

thispython = sys.executable
pyjversion = "pyjamas-0.6"
archive = "%(pyjversion)s.tgz" % locals()
url = "http://pypi.python.org/packages/source/P/Pyjamas/%(archive)s" % locals()

dir0 = os.getcwd()
bindir = os.path.join(dir0, "bin")
pyjamasdst = "../eggs"

os.chdir(pyjamasdst)

commands = [
    "wget %s" % url,
    "tar zxvf %s" % archive,
    "cd %(pyjversion)s && %(thispython)s bootstrap.py" % locals(),
    "cp -v %(pyjversion)s/bin/* %(bindir)s" % locals()
    ]
for cmd in commands:
    print cmd
    if os.system(cmd) != 0:
        sys.exit("%(cmd)s command failed" % locals())

os.chdir(dir0)
