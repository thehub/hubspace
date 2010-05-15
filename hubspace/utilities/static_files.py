from hubspace.utilities.jsmin import jsmin
import StringIO
from os import path, unlink
import md5

css_files = ['main.css', 'newcalendar.css', 'jquery.autocomplete.css', 'feeds.css', 'flexigrid/flexigrid.css', 'jquery-ui/pepper-grinder/jquery-ui-1.7.2.custom.css']

common_js_files = ['prototype-1.6.0.3.js', 'scroll.js', 'browserdetect.js', 'jquery.min.js',
'flexigrid/flexigrid.js',
'jq.noconflict.js',
'jquery-ui-1.7.2.custom.min.js',
'overlib/overlib.js', 'jquery.bgiframe.min.js', 'jquery.dimensions.js',
'jquery.autocomplete.min.js', 'delayed-observer-0.4b.js', 'jquery.ajaxQueue.js', 'jquery.timers.js',
'jquery.confirm.js', 'jquery.confirm-1.1.js',
'hubcms.js', 'json2.js',]

js_files = common_js_files + ['hub.js']
js_files2 = common_js_files + ['hub_pluspace.js']

# Notes
# bgiframe: Helps ease the pain when having to deal with IE z-index issues.
# dimensions: Extends jQuery to provide dimension-centric methods for getting widths, heights, offsets and more.
# jQuery-ui: 1.7.2 custom build: core, Draggable, Droppable, Dialog, Datepicker, Effects Core, Effect Blind, Effect Highlight, Theme flick 

admin_js_files = ['jquery.tablednd.js', 'my.sortable.js']

def minify(input_path):
   """return a minified version of a file as a python string
   """
   js_big = open(input_path)
   minified = jsmin(js_big.read())
   js_big.close()
   return minified

def get_version_no(file_name, default_path="hubspace/static/javascript"):
   """used in master template
   """
   base = path.abspath('.')
   try:
      return open(path.join(base, default_path, file_name + '.version')).read()
   except IOError:
      return 1

def get_file_list(path_or_filename_list, default_path):
   base = path.abspath('.')
   file_list = []
   for file_path in path_or_filename_list:
      if path.exists(path.join(base, file_path)):
         file_list.append(path.join(base, file_path))
      elif path.exists(path.join(base, default_path, file_path)):
         file_list.append(path.join(base, default_path, file_path))
      else:
         print "file: " + file_path + " not found when compiling javascript"
   return file_list
   
def js_compile(path_or_filename_list, default_path="static/javascript", output_filename="file.js"):
   """Input filenames that exist in the default_path or for which a full path is provided.
      Minfies and concatanates  js strings adding a special variable at the beginning to indicate that the file is compiled to key functions
   """
   #get the descriptors
   file_list = get_file_list(path_or_filename_list, default_path)
   compiled_js = ""
   for file_name in file_list:
      compiled_js += minify(file_name)
   compiled_js += "compiled = true;"

   base = path.abspath('.')
   js_hash = md5.new(compiled_js)
   try:
      js_hash_file = open(path.join(base, default_path, output_filename + '.hash'), 'r+')
   except IOError:
      js_hash_file = open(path.join(base, default_path, output_filename + '.hash'), 'w+')

   old_hash = js_hash_file.read()
   if old_hash==js_hash.hexdigest():
      print "nothing change in: " + output_filename 
      return
   js_hash_file.seek(0)
   js_hash_file.write(js_hash.hexdigest())
   try:
      js_version_no = open(path.join(base, default_path, output_filename + '.version'), 'r+')
   except IOError:
      js_version_no = open(path.join(base, default_path, output_filename + '.version'), 'w+')
   try:
      js_v_no = int(js_version_no.read())
   except ValueError:
      js_v_no = 0
   js_v_no += 1
   js_version_no.seek(0)
   js_version_no.write(str(js_v_no))
   file_out = open(path.join(base, default_path, versioned_file_name(output_filename, js_v_no)), 'w')
   for no in range(1, js_v_no):
      old_path = path.join(base, default_path, versioned_file_name(output_filename, no))
      if path.exists(old_path):
         unlink(old_path)
   file_out.write(compiled_js)
   file_out.close()
   print "file " + versioned_file_name(output_filename, js_v_no) + " written"
   return True

def versioned_file_name(filename, no):
   file_name_parts = filename.split('.')
   file_name_parts[-2] += str(no)
   return '.'.join(file_name_parts)
   
def css_concat(path_or_filename_list, default_path="static/css", output_filename="file.css"):
   file_list = get_file_list(path_or_filename_list, default_path)
   compiled_css = ""
   for file_name in file_list:
      css_file = open(file_name)
      compiled_css += css_file.read() + "\n"

   base = path.abspath('.')
   file_out = open(path.join(base, default_path, output_filename), 'w')
   file_out.write(compiled_css)
   file_out.close()
   print "file " + output_filename + " written"
   return True

def hubspace_compile():
   js_compile(js_files, 'hubspace/static/javascript', 'hubspace.js')
   js_compile(js_files2, 'hubspace/static/javascript', 'pluspace.js')
   js_compile(admin_js_files, 'hubspace/static/javascript', 'admin.js')
   css_concat(css_files, 'hubspace/static/css', 'hubspace.css')
