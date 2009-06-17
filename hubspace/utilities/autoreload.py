import cherrypy
import sys

from os import stat
from os.path import join as join_path
from os.path import exists
from thread import allocate_lock
from time import time
from types import ModuleType
from kid.compiler import compile_file


# ------------------------------------------------------------------------------
# some konstants
# ------------------------------------------------------------------------------

_auto_reload_lock = allocate_lock()

auto_reload_last= {1:time()}
package_list= []
auto_reload_dict = {}

# ------------------------------------------------------------------------------
# kore funktions
# ------------------------------------------------------------------------------
def get_watchlist():

    watchlist = {}
    add_to_watchlist = watchlist.__setitem__
    for package in package_list:
        for module_name in sys.modules:    
            if module_name.startswith(package):
                module = sys.modules[module_name]
                try:
                    if not hasattr(module, '__file__'):
                        continue
                    else:
                        pyc = module.__file__
                    
                    if pyc.endswith('.pyc'):
                        orig_path = pyc.rsplit('.', 1)[0] + '.py'
                        if not exists(orig_path):
                            orig_path = pyc.rsplit('.', 1)[0] + '.kid'
                        if not exists(orig_path):
                            orig_path = None
                        
                    if orig_path:
                        add_to_watchlist(module_name, (orig_path, pyc))
                except:
                    pass

    return watchlist
        
def get_updated_files(watchlist):

    updated = {}

    for module, (orig_path, pyc) in watchlist.iteritems():
        try:        
            if stat(pyc).st_mtime < stat(orig_path).st_mtime:
                updated[module] = watchlist[module]
        except:
            pass

    return updated

def reload_modules(updated):
    for module in updated:
        cherrypy.log("Reloading %s" % module)
        ext = updated[module][0].rsplit('.', 1)[1]
        
        if ext=='kid':
            compile_file(updated[module][0])
            reload(sys.modules[module])
        elif ext=='py':
            reload(sys.modules[module])
        else:
            raise 'unknown module type'


 
def autoreload(package='proto.package', interval=1):
    if package not in package_list:
        package_list.append(package)
 
    auto_reload_dict.update(get_watchlist())
    
    if (time() - auto_reload_last[1]) > interval:
        if _auto_reload_lock.locked():
            return "Auto-reload is already underway"
    
        _auto_reload_lock.acquire_lock()

        try:
            auto_reload_last[1] = time()
            return reload_modules(get_updated_files(auto_reload_dict))
        finally:
            _auto_reload_lock.release_lock()
