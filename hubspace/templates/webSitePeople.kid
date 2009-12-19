<?python
from hubspace.utilities.permissions import is_host
from turbogears import identity
render_static = False
from urllib import quote
class name_attribute(dict):
    def __missing__(self, x):
        return 'name'

name_map = name_attribute({'User' : 'display_name'})
from hubspace.utilities.image_helpers import image_src
user = None
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'webSiteMaster.kid'">
<head>
</head>
<body>	
	<div id="people_links">
		<ul id="people_list" py:if="not user">
			<li py:for="member in lists('people_list')" id="User-${member.object.id}" py:if="member.object.active and member.object.public_field" >
				<a href="${relative_path}people/${quote(member.object.user_name)}" title="${member.object.display_name}" class="people-link" id="${member.object.user_name}">
					<img src="${image_src(member.object, 'image', '/static/images/shadow.png')}" alt="${member.object.display_name + ' ' +member.object.organisation}"/>
					<span>${member.object.display_name}<br />{member.object.organisation}</span>
				</a>
			</li>
		</ul>
                <div py:if="is_host(identity.current.user, location, render_static)" class="edit_list" id="edit_list_members"><a href="#">Edit People</a></div>
	</div>
	<div id="people-detail" py:if="user">
		<div id="people-detail-content">
			<img src="${image_src(user, 'image', '/static/images/shadow.png')}" alt="${user.display_name + ' ' +user.organisation}"/>
			<div id="people-detail-copy">
				<h4>${user.display_name}, ${user.organisation} </h4>
                                <p>${user.description}</p>
			</div>
		</div>
		<a id="people-detail-close" href="${relative_path}people.html" title="close"></a>
	</div>
</body>
</html>
