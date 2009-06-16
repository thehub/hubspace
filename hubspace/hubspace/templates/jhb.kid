<?python
from hubspace.controllers import permission_or_owner
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title></title>
</head>
<body class='Location'>
$location
$permissions
$groups
<c py:replace='str(permission_or_owner(location,tg.identity.user,"manage_userfoobar"))' />
</body>
</html>

