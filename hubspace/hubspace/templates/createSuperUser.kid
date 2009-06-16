<?python
from hubspace.controllers import permission_or_owner
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
</head>
<body>
     <form action="create_superuser_and_permissions" method="POST">
         <h1>Create Super User</h1>
         <div>Username <input name="user_name" type="text" /></div>
         <div>Password <input name="password" type="password" /></div>
         <div>First Name <input name="first_name" type="text" /></div>
         <div>Last Name <input name="last_name" type="text" /></div>
         <div>Email <input name="email_address" type="text" /></div>
         <div>Submit <input value="create" type="submit" /></div>
     </form>
</body>
</html>
