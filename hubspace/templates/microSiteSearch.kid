<?python
from hubspace.utilities.permissions import is_host
from turbogears import identity
render_static = False
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>



</head>
<body id='sitesearch'>
<div id='content-intro'>      
<form action="${page.path_name}">
Search for <input type="text" name="s" value="${s}" class="searchinput input" id="searchpage-searchbox"/>
<input type="submit" value="Submit Search" class="button simple-btn" />
</form>

<ul py:if='searchresults'>
    <li py:for='result in searchresults'>
        <h3><a href="${result['url']}">${result['title']}</a></h3>
        <p>${result['description']}</p>
    </li>
</ul>
</div>      
</body>
</html>
