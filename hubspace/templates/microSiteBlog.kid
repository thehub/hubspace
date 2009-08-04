<?python
from hubspace.utilities.permissions import is_host
from turbogears import identity
render_static = False
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>
      ${XML(blog_head)}
</head>
<body id="${page.path_name}">
      <c py:strip="True" py:if="is_host(identity.current.user, location, render_static)">
          Blog URL: <span id="blog_url" class="text_small">${page.blog_url and page.blog_url or "Put your blog url here"}</span>
      </c>
      <div class="blog" py:if="page.blog_url">${XML(blog)}</div>
</body>
</html>
