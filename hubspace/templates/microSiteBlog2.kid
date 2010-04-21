<?python
from hubspace.utilities.permissions import is_host
from turbogears import identity
render_static = False
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>



</head>
<body id="${page.path_name}">
      <c py:strip="True" py:if="is_host(identity.current.user, location, render_static)">
        <span id='blogedit'>
          <a py:ref="page.blog_url.strip()" href="${page.blog_url.strip()}/wp-admin" target="wpadmin" id="blogedit">Edit blog</a><br />
          Blog URL: <span id="blog_url" class="text_small">${page.blog_url and page.blog_url or "Put your blog url here"}</span>
      </span>      </c>
      <div id='content-intro'><div class="blog" py:if="page.blog_url">${XML(blog)}<!--nobannerplease-->
</div></div>
<ul style="display:none" id="comments-list">
<li></li>
</ul>      
</body>
</html>
