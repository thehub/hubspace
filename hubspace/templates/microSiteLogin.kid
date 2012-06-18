<?python
migrated = [15]
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'loginMaster.kid', 'microSiteMaster.kid'">
<head>
</head>
<body py:if="location and location.id in migrated" id="login">
    <div id="main-logo"/>
        <iframe src="http://ops.the-hub.net/" width="800px" height="800em" scrolling="yes" marginwidth="0" frameborder="0"/>
    <script>
        jq('#content-highlight').hide();
    </script>
</body>
<body py:if="location and location.id not in migrated" id="login">
    <div class="span-12" id="content-intro">
    </div>
    <div class="span-12 last content-sub">
      <h3>Member Login</h3>
        <div class="span-12 last content-sub" id="member-login">
            <h3>Login</h3>
            <div>
            </div>
       </div>
    </div>
</body>
</html>
