<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>

</head>
<body id="${page.name}">
        <div class="span-12" id="content-intro">
            <h1 id="title" class="text_small">${page.title and page.title or "Your Header"}</h1>
            <div py:if="page.content" class="text_wysiwyg" id="content">${XML(page.content)}</div>
            <div py:if="not page.content" class="text_wysiwyg" id="content"><p>Your content here</p> 
            </div>
        </div>
        <div class="span-12 last">
            <div class="span-12 last content-sub" id="features">
                <h3 id="right_header" class="text_small">${page.right_header and page.right_header or "Your Header"}</h3>
                <div py:if="page.right_column" class="text_wysiwyg" id="right_column">${XML(page.right_column)}</div>
                <div py:if="not page.right_column" class="text_wysiwyg" id="right_column">
		   <p>Your content here</p>
                </div>
            </div>
        </div>
</body>
</html>
