<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>
</head>
<body id="contact">
    <div class="span-8" id="content-intro">
      <h1 id="title" class="text_small">${page.title and page.title or "Contact Us"}</h1>
      <div py:if="page.content" class="text_wysiwyg_small" id="content">${XML(page.content)}</div>
      <div py:if="not page.content" class="text_wysiwyg_small" id="content">
          <p>Address<br /><strong>Hub Kings Cross,<br />34b York Way,<br />London N1 9AB,<br />UK</strong><br /><a href="contact.html">Map</a></p>
          <p>Telephone<br /><strong>+44 (0)20 7841 3450</strong></p>
          <p>Email<br /><strong><a href="contact.html">kingscross.hosts@the-hub.net</a></strong></p>
      </div>
    </div>
    <div id="geo_address" class="span-16 gmap">${location.geo_address and location.geo_address or '34b York Way, London N1 9AB, UK'}</div>	
</body>
</html>
