<?xml version="1.0" encoding="utf-8"?>
<?python
from hubspace.active import location_links
from hubspace.utilities.permissions import is_host
from turbogears import identity
render_static = False
?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">
<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
	<meta http-equiv="content-type" content="text/html; charset=utf-8" />
	<meta name="description" content="Places for meeting, working, learning, innovating and connecting dedicated to inspiring and supporting enterprising initiatives for a better world." />
        <meta name="keywords" content="hub, hub world, hub labs, hub working, hub culture, hub tech, innovation, social innovation, social entrepreneurship, enterprise, london, amsterdam, berkeley, berlin, bristol, bombay, brussels, cairo, halifax, johannesburg, rotterdam, berlin, oaxaca, telaviv, islington, king's cross, southbank, madrid, milan, porto, sao paulo, stockholm, toronto, social networking, eurostar, space, office, meeting rooms, sustainable" />
	<title>The Hub | ${page.name.title()}</title>
	<link rel="stylesheet" href="/static/css/hubweb.css" type="text/css" media="all" />
	<link rel="stylesheet" href="/static/css/micro/superfish.css" type="text/css" media="screen"/>
        <script src="/static/javascript/jquery.min.js" charset="utf-8" type="text/javascript"></script>
        <script src="/static/javascript/jq.noconflict.js" charset="utf-8" type="text/javascript"></script>
        <script src="/static/javascript/hoverIntent.js" charset="utf-8" type="text/javascript"></script>
        <script src="/static/javascript/superfish.js" charset="utf-8" type="text/javascript"></script>
    <c py:strip="True" py:if="is_host(identity.current.user, location, render_static)">
        <script src="/static/javascript/effects.core.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/effects.highlight.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/prototype-1.6.0.3.js" type="text/javascript" charset="utf-8"></script>
        <link rel="stylesheet" type="text/css" href="/static/javascript/yui/build/editor/assets/skins/sam/editor.css" /> 
        <link rel="stylesheet" type="text/css" href="/static/javascript/yui/build/fonts/fonts-min.css" /> 
        <link rel="stylesheet" type="text/css" href="/static/javascript/yui/build/logger/assets/skins/sam/logger.css" /> 
        <script src="/static/javascript/yui/build/yahoo-dom-event/yahoo-dom-event.js"></script> 
        <script src="/static/javascript/yui/build/element/element-min.js"></script>  
        <script src="/static/javascript/yui/build/container/container_core-min.js"></script> 
        <script src="/static/javascript/yui/build/menu/menu-min.js"></script> 
        <script src="/static/javascript/yui/build/button/button-min.js"></script> 
        <script src="/static/javascript/yui/build/editor/editor-min.js"></script> 
        <script src="/static/javascript/yui/build/animation/animation-min.js"></script> 
        <script src="/static/javascript/yui/build/logger/logger-min.js"></script> 
        <script src="/static/javascript/yui/build/dragdrop/dragdrop-min.js"></script>
        <script src="/static/javascript/yui/build/selector/selector-min.js"></script>
        <link rel="stylesheet" type="text/css" href="/static/css/list-edit-table.css" />
        <link rel="stylesheet" href="/static/css/jquery.autocomplete.css" type="text/css" media="screen"/>
        <script src="/static/javascript/jquery.bgiframe.min.js" charset="utf-8" type="text/javascript"></script>
        <script src="/static/javascript/jquery.autocomplete.min.js" charset="utf-8" type="text/javascript"></script>
        <script src="/static/javascript/jquery.confirm.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/jquery.confirm-1.1.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/list-editor.js" type="text/javascript" charset="utf-8"></script>
        <link rel="stylesheet" href="/static/css/editor-toggle.css" type="text/css" media="screen"/>
        <script src="/static/javascript/editorToggle.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/jquery.timers.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/overlib/overlib.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/hubcms.js" type="text/javascript" charset="utf-8"></script>
    </c>
        <script src="/static/javascript/thehub.js" charset="utf-8" type="text/javascript"></script>
    <link href="/static/images/favicon.ico" type="image/x-icon" rel="Shortcut icon"/>

</head>
<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()"  class="yui-skin-sam ${page.name}">
<div style="visibility:hidden;" id="location_id" class="${location.id}"></div>
<div style="visibility:hidden;" id="page_id" class="${page.id}"></div>
<div style="visibility:hidden;" id="relative_url" class="${relative_path}"></div>
<div style="visibility:hidden;" id="page_path_name" class="${page.path_name}"></div>
<span id="throbber"><img src="/static/images/timer_2.gif" /> <span id="throbtext">loading... </span></span>
<div id="wrapper">
	<a id="logo" href="index.html"><img src="/static/images/hubweb/hub_logo.png" alt="Hub Logo" /></a>
        <div class="container" id="menu-top">
            <div id="hub-selector">
                <ul class="sf-menu">
                     <li><a id="hub-anchor" href="#">Go To Hub...</a>
                          <ul id="z">
                            <?python
                               locs = location_links()
                            ?>
                             <li py:for="loc in locs"><a href="${loc[0]}">${XML(loc[1])}</a></li>
                          </ul>
		     </li>
	        </ul>
            </div>
            <ul id="left_tabs">
                 <li py:attrs="page.id==menu_item.object.id and {'class':'selected'} or {}" py:for="menu_item in lists('left_tabs')" py:if="menu_item.active"><a href="${relative_path}${menu_item.object.path_name}" id="Page-${menu_item.object.id}-name">${menu_item.object.name and menu_item.object.name or "King's Cross"}</a></li>
            </ul>
            <div py:if="is_host(identity.current.user, location, render_static)" class="edit_list" id="edit_list_left"><a href="#">Edit Left Navigation</a></div>
    <?python
       right_tabs = list(lists('right_tabs'))
       right_tabs.reverse()
    ?>
            <ul id="right_tabs">
                 <li py:attrs="page.id==menu_item.object.id and {'class':'selected right'} or {'class': 'right'}" py:for="menu_item in right_tabs" py:if="menu_item.active"><a href="${relative_path}${menu_item.object.path_name}"  id="Page-${menu_item.object.id}-name">${menu_item.object.name and menu_item.object.name or "King's Cross"}</a></li>
            </ul>
            <div py:if="is_host(identity.current.user, location, render_static)" class="edit_list" id="edit_list_right"><a href="#">Edit Right Navigation</a></div>
        </div>
         <div py:replace="item[:]"/>
</div>
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-9039567-1}");
pageTracker._trackPageview();
} catch(err) {}</script>
</body>
</html>
