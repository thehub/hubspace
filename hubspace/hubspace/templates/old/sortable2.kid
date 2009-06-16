<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<?python 
import sitetemplate
import cherrypy
from hubspace.templates.memberslist import member_list
from hubspace.model import User, Location
from hubspace.controllers import filter_members, permission_or_owner
title = {'http://localhost:8080':'The Hub',
         'http://members.the-hub.net':'The Hub',
         'http://berlin.the-hub.net':'Self'}
?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

  <head>
      <script src="/static/javascript/jquery-1.2.3.min.js"></script>
      <script src="/static/javascript/jquery.dimensions.js"></script>
      <script src="/static/javascript/ui.mouse.js"></script>
      <script src="/static/javascript/ui.sortable.js"></script>
      <script src="/static/javascript/ui.sortable.ext.js"></script>
      <script src="/static/javascript/ui.draggable.js"></script>
      <script src="/static/javascript/ui.draggable.ext.js"></script>
      <script src="/static/javascript/ui.droppable.js"></script>
      <script src="/static/javascript/ui.droppable.ext.js"></script>
      <script>
        var jq = jQuery.noConflict();
      </script>
      <script src="/static/javascript/my.sortable.js"></script>
      <style type="text/css">
           .animal{
              cursor:grab;
              cursor:-moz-grab;
           }
           .family{
              cursor:grab;
              cursor:-moz-grab;
           }
           .family li{
              cursor:grab;
              cursor:-moz-grab;
           }
           .family ul{
              min-height:50px;
           }
      </style>
  </head>
  <body>
       <ul id="groups">
        <li class="group">
	    <ul id="cats"  class="family">
                <li id="tiger" class="animal">tiger</li>
                <li id="lion" class="animal">lion</li>
                <li id="pussycat" class="animal">pussycat</li>
            </ul>
        </li>
        <li  class="group">
            <ul id="dogs"  class="family">
                <li id="wolf" class="animal">wolf</li>
                <li id="hound" class="animal">hound</li>
                <li id="scum" class="animal">scum</li>
            </ul>
        </li>
        <li  class="group">
            <ul id="fishs"  class="family">
                <li id="plaice" class="animal">plaice</li>
                <li id="cod" class="animal">cod</li>
            </ul>
        </li>
       </ul>
  </body>
</html>
