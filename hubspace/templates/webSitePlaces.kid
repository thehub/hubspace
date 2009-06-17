<?python
from hubspace.utilities.permissions import is_host
from turbogears import identity
render_static = False
from urllib import quote
def coordinates(place):
    top = place.top and (place.top.strip()) + 'px' or "0px"
    left = place.left and (place.left.strip() +'px') or "0px"
    style = {'style':'top:' + top + '; left:' + left + ';'}
    return style
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'webSiteMaster.kid'">
<head>
</head>
<body>	
	<div id="worldmap">
		<div id="places_list">
                   <div py:for="hub in lists('places_list')"  id="PublicPlaces-${hub.object.id}"   py:attrs="coordinates(hub.meta_object)" py:if="hub.active">
                     <a  class="worlddot" href="${relative_path}places/${quote(hub.object.name)}" title="${hub.object.name}"></a>
                     <img src="/static/images/drag.png" py:if="is_host(identity.current.user, location, render_static)" />
                    </div>
		</div>
                <div py:if="is_host(identity.current.user, location, render_static)" class="edit_list" id="edit_list_places"><a href="#">Edit Places</a></div>
	</div>
	<div id="place_info" py:if="place is not None">
                <a class="close" href="${relative_path}places.html" title="close">X</a>
                <div>
                    <img width="185px" height="102px" id="PublicPlace-${place.id}-image"  src="${place.image_name and upload_url + place.image_name or '/static/images/hubweb/berlin.jpg'}" alt="${place.name}" />
                </div>
                <div class="description" py:if="place.description" id="PublicPlace-${place.id}-description">${XML(place.description)}</div>
                <div class="description" py:if="not place.description" id="PublicPlace-${place.id}-description">
                    <h4>Visit  <a class="" href="http://berlin.the-hub.net/public/">Hub Berlin</a></h4>
	            <p>Erkelenzdamm 59-61, Portal 1, 3. OG<br />10999 Berlin - Kreuzberg, Germany<br />Telephone:+49 30 707 1950</p>
                </div>
	</div>
</body>
</html>