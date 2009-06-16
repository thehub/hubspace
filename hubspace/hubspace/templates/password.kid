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
    <div id="loginBox">
        <p>${message}</p>
        <form py:if='showform' action="/requestPassword" method="POST">
            <table>
                <tr>
                    <td class="label">
                        <label for="email">email:</label>
                    </td>
                    <td class="field">
                        <input type="text" id="email" name="email"/>
                    </td>
                    <td colspan="2" class="buttons">
                        <input type="submit" name="submit" value="request password"/>
                    </td>
                </tr>
            </table>
        </form>
        <form py:if='showform' action="/requestPassword/username" method="POST">
            <table>
                <tr>
                    <td class="label">
                        <label for="email">email:</label>
                    </td>
                    <td class="field">
                        <input type="text" id="email" name="email"/>
                    </td>
                    <td colspan="2" class="buttons">
                        <input type="submit" name="submit" value="request username"/>
                    </td>
                </tr>
            </table>

        </form>
    </div>
    </div>
</body>
</html> 


