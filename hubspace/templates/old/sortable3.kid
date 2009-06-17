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
      <script src="/static/javascript/jquery.tablednd.js"></script>
      <script>
        var jq = jQuery.noConflict();
      </script>
      <script src="/static/javascript/my.sortable.js"></script>
      <style type="text/css">
           .dragClass{
              background-color: black;
              color: yellow;
           }
           ul.family li{
              cursor: move;
           }
           ul.family{
              margin-left:30px;
              padding-left: 0px;
              list-style-type: none;
           }
           ul.family li.place{
              font-weight:600;
           }
           ul.
      </style>
  </head>
  <body>
     <table id="groups">
        <tr>
          <td>
	    <ul id="cats"  class="family">
                <li class="place">Cats</li>
                <li id="tiger" class="animal">tiger</li>
                <li id="lion" class="animal">lion</li>
                <li id="pussycat" class="animal">pussycat</li>
            </ul>
          </td>
        </tr>
        <tr>
          <td>
            <ul id="fishs"  class="family">
                <li class="place">Fishes</li>
                <li id="plaice" class="animal">plaice</li>
            </ul>
          </td>
        </tr>
        <tr>
          <td>
            <ul id="dogs" class="family">
                <li class="place">Dogs</li>
                <li id="wolf" class="animal">wolf</li>
                <li id="hound" class="animal">hound</li>
                <li id="scum_dog" class="animal">scum</li>
            </ul>
          </td>
        </tr>
   </table>
  </body>
</html>
