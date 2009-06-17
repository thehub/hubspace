<?python
from hubspace.utilities.image_helpers import image_src
from docutils.core import publish_parts
from hubspace.utilities.uiutils import get_freetext_metadata
from hubspace.templates import oldLoginMaster
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="oldLoginMaster.kid">
<head>
</head>
<body>
	<div id="hubHomeContent" class="clearfix">
		<div id="main">
                    <div class="update_item" id="pub_profile">
			<h1>${user.display_name}</h1>
                        <div class="profileTop">
                          <img src="${image_src(user, 'image', '/static/images/shadow.png')}" />                          
                          <table class="profileDetails">
                               <tr py:if="user.organisation" class="property"><td class="propertyTitle">Organisation</td><td class="propertyValue"> ${user.organisation}</td></tr>
                               <tr py:if="get_freetext_metadata(user, 'biz_type')" class="property"><td class="propertyTitle">Type of Business</td><td class="propertyValue"> ${get_freetext_metadata(user, 'biz_type')}</td>
                               </tr>
                          </table>
                        </div>
		    	<p>${XML(publish_parts(user.description, writer_name="html")["html_body"])}</p>
                     </div>
		</div>
	</div>
</body>
</html>
