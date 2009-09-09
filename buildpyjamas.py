import os
import glob
import sys
from hubspace.utilities.static_files import minify

jsbuilder = os.path.abspath("./bin/pyjsbuild")
srcdir = "hubspace/fe/src"
outdir = os.path.abspath("hubspace/static/fe")
file_types_to_minify = ['js', 'css', 'html']
build_cmd = "%(jsbuilder)s -d -m -O --print-statement -o %(outdir)s %%(src)s" % locals()

for path in (srcdir, outdir):
    if not os.path.isdir(path):
        os.makedirs(path)
    
def compilePyjSources():
    dir0 = os.getcwd()
    
    os.chdir(srcdir)
    for src in glob.glob("*.py"):
        if not "RootPanel" in file(src).read(): # Assumption is a src file with no RootPanel in it, most likely does not need direct compilation 
            continue
        cmd = build_cmd % locals()
        if not os.system(cmd) == 0:
            sys.exit("failed: %s" % cmd)
    
    os.chdir(outdir)
    for root, dirs, files in os.walk('.'):
        for name in files:
            path = os.path.join(root, name)
            ext = name.split('.')[-1]
            if ext in file_types_to_minify:
                print "minifying ", path
                out = minify(path)
                file(path, 'w').write(out)
    
    os.chdir(dir0)

if __name__ == "__main__":
    compilePyjSources()
