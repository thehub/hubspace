<?python
from hubspace.templates import oldLoginMaster
from docutils.core import publish_parts
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="oldLoginMaster">
<head>
</head>
<body>
    <div id="hubHomeContent" class="clearfix">
        <div id="main">
            <h1 py:if="location">${location.homepage_title}</h1>
            <div py:if="location">${location.homepage_description and XML(publish_parts(location.homepage_description, writer_name="html")["html_body"])}</div>
        </div>
    </div>
</body>
</html>
