<?python
from hubspace.templates import loginMaster
from docutils.core import publish_parts
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'loginMaster.kid', 'microSiteMaster.kid'">
<head>
</head>
<body>
    <div class="span-12" id="content-intro">
      <div id="loginBox" class="span-12 last content-sub">
        <h3>Request Username/Password</h3>
        <p>${message}</p>
        <form py:if='showform' action="./requestPassword" method="POST">
                        <label for="email">email:</label>
                        <input type="text" id="email" name="email"/>
                        <input type="submit" name="submit" value="Get Password"/>
                        <input type="submit" name="submit" value="Get Username"/>
        </form>
      </div>
    </div>
</body>
</html> 


