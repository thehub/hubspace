<?xml version="1.0" encoding="utf-8"?>
<?python
import cherrypy
from turbogears import identity
#from hubspace.utilities.static_files import get_version_no, css_files, js_files
#js_version_no = get_version_no("hubsite.js")
from hubspace.utilities.permissions import is_host
render_static = False
image_source_list = []
from hubspace.model import Location, Page
from sqlobject import AND
from hubspace.active import location_links
from hubspace.file_store import get_filepath
?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">
<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <?python
    title = Page.select(AND(Page.q.path_name=='index.html', Page.q.locationID==location.id))[0].title
    ?>
    <title>${title and title or "The Hub King's Cross"} ${page.title and page.title != title and '| ' + page.title.title() or ""}</title>
    <div py:replace="item[:]"/>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <meta content="Places for meeting, working, learning, innovating and connecting dedicated to inspiring and supporting enterprising and imaginative initiatives for a radically better world. " name="description" />
    <link rel="stylesheet" href="/static/css/micro/blueprint/screen.css" type="text/css" media="screen, projection"/>
    <link rel="stylesheet" href="/static/css/micro/blueprint/print.css" type="text/css" media="print"/>
    <!--[if IE]>
    <link rel="stylesheet" href="/static/css/micro/blueprint/ie.css" type="text/css" media="screen, projection"/>
    <![endif]-->
    <link rel="stylesheet" href="/static/css/micro/layout.css" type="text/css" media="screen, projection"/>
    <link rel="stylesheet" href="/static/css/micro/typography.css" type="text/css" media="screen, projection"/>
    <link rel="stylesheet" href="/static/css/micro/colours.css" type="text/css" media="screen, projection"/>
    <link rel="stylesheet" href="/static/css/micro/content.css" type="text/css" media="screen, projection"/>
    <link rel="stylesheet" href="/static/css/micro/superfish.css" type="text/css" media="screen"/>
    <script src="/static/javascript/jquery.min.js" type="text/javascript" charset="utf-8"></script>
    <script src="/static/javascript/jq.noconflict.js" type="text/javascript" charset="utf-8"></script>
    <script py:if="page.page_type=='experience'"  src="/static/javascript/jquery.cycle.lite.js" type="text/javascript" charset="utf-8"></script>
    <script src="/static/javascript/hoverIntent.js" type="text/javascript" charset="utf-8"></script>
    <script src="/static/javascript/superfish.js" type="text/javascript" charset="utf-8"></script>
    <c py:strip="True" py:if="is_host(identity.current.user, location, render_static)">
        <link rel="stylesheet" href="/static/css/jquery.autocomplete.css" type="text/css" media="screen"/>
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
        <script src="/static/javascript/jquery.confirm.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/jquery.confirm-1.1.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/jquery.bgiframe.min.js" charset="utf-8" type="text/javascript"></script>
        <script src="/static/javascript/jquery.autocomplete.min.js" charset="utf-8" type="text/javascript"></script>
        <script src="/static/javascript/list-editor.js" type="text/javascript" charset="utf-8"></script>
        <link rel="stylesheet" href="/static/css/editor-toggle.css" type="text/css" media="screen"/>
        <script src="/static/javascript/editorToggle.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/overlib/overlib.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/jquery.timers.js" type="text/javascript" charset="utf-8"></script>
        <script src="/static/javascript/hubcms.js" type="text/javascript" charset="utf-8"></script>
    </c>
    <script src="/static/javascript/thehub.js" type="text/javascript" charset="utf-8"></script>
    <link href="/static/images/favicon.ico" type="image/x-icon" rel="Shortcut icon"/>
</head>
<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()"  class="yui-skin-sam">
<div style="visibility:hidden;" id="location_id" class="${location.id}"></div>
<div style="visibility:hidden;" id="page_id" class="${page.id}"></div>
<div style="visibility:hidden;" id="page_path_name" class="${page.path_name}"></div>
<div style="visibility:hidden;" id="relative_url" class="${relative_path}"></div>
<span id="throbber"><img src="/static/images/timer_2.gif" /> <span id="throbtext">loading... </span></span>
<div class="container" id="menu-top">
  <div id="main-logo">
  <img id="Location-${location.id}-micrologo" src="${get_filepath(location,'micrologo', upload_url, '/static/images/micro/hub_logo.gif')}" height="70" alt="logo" usemap="#micrologo" />
  <map py:if="not is_host(identity.current.user, location, render_static)" name="micrologo">
      <area shape="rect" coords="0,0,70,70" href="http://www.the-hub.net" alt="back to Hub World" title="back to Hub World" />
      <area shape="rect" coords="70,0,500,500" href="/public/" alt="Home" title="${'Hub ' + location.name + ' home'}" />
  </map> 
<!--    <a href="http://www.the-hub.net" title="back to Hub World"><img id="Location-${location.id}-micrologo" height="60" src="${get_filepath(location,'micrologo', upload_url, '/static/images/micro/hub_logo.gif')}" alt="Hub Logo"/></a> -->
  </div> 
  <div py:if="is_host(identity.current.user, location, render_static)" id="admin_view_indicator">
      Admin Mode
  </div>
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
    <div id="content-highlight" class="container">
        <img py:if="not image_source_list" id="Page-${page.id}-image" src="${top_image_src}" alt="${page.image_name}" />   
        <img py:if="image_source_list" py:for="image_source in image_source_list" class="slideshow_image" id="${page.name}" src="${image_source}" />
    </div>
    <div id="content-main" class="container">
         <div py:replace="item[:]"/>
    </div>
 
<div class="container" id="footer">
    <div py:for="menu_item in list(lists('left_tabs'))[1:]" py:if="menu_item.active" class="span-3"><a href="${relative_path}${menu_item.object.path_name}">${menu_item.object.name and menu_item.object.name or "King's Cross"}</a>  <br /><span class="footer-menu-desc" id="Page-${menu_item.object.id}-subtitle">${menu_item.object.subtitle and menu_item.object.subtitle or "King's Cross"}</span></div>
    <div py:for="menu_item in lists('right_tabs')" py:if="menu_item.active" class="span-3"><a href="${relative_path}${menu_item.object.path_name}">${menu_item.object.name and menu_item.object.name or "King's Cross"}</a>  <br /><span class="footer-menu-desc" id="Page-${menu_item.object.id}-subtitle">${menu_item.object.subtitle and menu_item.object.subtitle or "King's Cross"}</span></div>
  <div class="span-3 last">
    <span class="footer-menu-desc">Spread the Hub!</span>
    <div id="add-this-widget">
    <!-- AddThis Button BEGIN -->
    <a href="http://www.addthis.com/bookmark.php" onmouseover="return addthis_open(this, '', '[URL]', '[TITLE]')" onmouseout="addthis_close()" onclick="return addthis_sendto()"><img src="http://s7.addthis.com/static/btn/sm-share-en.gif" width="83" height="16" alt="Bookmark and Share" style="border:0"/></a><script type="text/javascript" src="http://s7.addthis.com/js/152/addthis_widget.js"></script>
    <!-- AddThis Button END -->
    </div>
  </div>
</div>
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-9039567-1");
pageTracker._setDomainName(".the-hub.net");
pageTracker._trackPageview();
} catch(err) {}</script>
<script py:if="page.page_type in ['home', 'contact']" src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAiA7tLHdzZr8yhGAEbo5FGxS_srkAJTD0j5T3EF3o06M_52NTAhQM2w0ugG9dZdoyPl3s9RqydGrzpQ" type="text/javascript"></script>
</body>
</html>
