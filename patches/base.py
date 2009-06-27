import os
import imp
import sys
from glob import glob

class PatchLevel(object):
    def __init__(self, plpath):
        self.plpath = plpath
        self._pl = None
        if not os.path.isfile(self.plpath):
            file(self.plpath, 'w').write("%d" % 0)
    def __get__(self, o, otype):
        if self._pl == None:
            self._pl = int(file(self.plpath).read().strip())
        return self._pl
    def __set__(self, cls, pl):
        file(self.plpath, 'w').write("%d" % pl)
        self._pl = pl

def showmsg(msg, exit=None):
    sys.stderr.write("PATCH: %s\n" % msg)
    if exit != None: sys.exit(exit)

class Patch(object):
    description = ""
    def __init__(self, pl):
        assert isinstance(pl, int), "patchlevel should be an integer"
        self.level = pl
    def apply(self):
        raise NotImplemented
    def __call__(self):
        self.apply()
    def __str__(self):
        return "patch # %d" % self.level
    def __eq__(self, o):
        return isinstance(o, self.__class__) and x.level == self.level
    def __cmp__(self, o):
        return self.level.__cmp__(o.level)

class Updater(object):
    plpath = "patchlevel"
    if sys.argv[1:2] == ["test.cfg"]:
        plpath = plpath + ".test"
    patchesdir = "patches"
    current_pl = PatchLevel(plpath)
    def __init__(self):
        self.patches = []
        self.findPatchs()
    def findPatchs(self):
        patches = []
        patchfiles = [f[:-3] for f in glob(self.patchesdir + "/[0-9]*.py") if os.path.basename(f[:-3]).isdigit()]
        if not patchfiles: showmsg("No patches to apply!", 0)
        for patchfile in patchfiles:
            try:
                mod = imp.load_module(patchfile, *imp.find_module(patchfile))
            except Exception, err:
                showmsg("Importing patch file %s failed with error: %s" % (patchfile, err), True)
            patchfile = os.path.basename(patchfile)
            for o in mod.__dict__.values():
                if type(o) == type and issubclass(o, Patch):
                    patch_no = int(patchfile)
                    if patch_no == 0:
                        showmsg("%s.py: patchfile name should be > 0" % patchfile, 1)
                    patch = o(patch_no)
                    showmsg("Found %s" % patch)
                    if patch in patches:
                        showmsg("%s.py conflicts with some other patchfile with same level" % patchfile)
                    patches.append(patch)
                    break
            else:
                showmsg("Found no patch in %s.py" % patchfile)
        patches.sort()
        self.patches = patches
    def update(self):
        for patch in self.patches:
            if self.current_pl >= patch.level:
                showmsg("%s already applied (current patchlevel: %s)" % (patch, self.current_pl))
                continue
            showmsg("Applying %s" % patch)
            if patch.description:
                showmsg("%s description: %s" % (patch, patch.description))
            try:
                patch()
            except Exception:
                showmsg("%s failed" % patch)
                raise
            showmsg("Successful: Applying %s" % patch)
            self.current_pl = patch.level
