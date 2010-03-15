<?xml version="1.0" encoding="utf-8"?>
<?python
from hubspace.utilities.permissions import is_host
from turbogears import identity
render_static = False
?>

<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>

</head>
<body id="${page.name}">
        <div class="span-12" id="content-intro">
            <h1 id="title" class="text_small">${page.title and page.title or "Your Header"}</h1>
            <div py:if="page.content" class="text_large" id="content">
            <div py:if="is_host(identity.current.user, location, render_static)">edit content</div>
            ${XML(page.content)}</div>
            <div py:if="not page.content" class="text_large" id="content"><p>Your content here</p> 
            </div>
        </div>
       </body>
</html>
