<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" xmlns:py="http://purl.org/kid/ns#">
<head>
 <title>HubSpace: New issue</title>
</head>
<body>

<p>An error has occurred.<br/>
Every error is logged but it is helpful if you can tell us a bit more about what happened.<br/>

<h3 py:if="e_hint">Possible reasons for this error: <b>${e_hint}</b></h3> 
</p>
 
<form id="newticket" name="newticket" method="post"  action="/submitTicket">
  <p>
  <label for="summary"><strong> Can you tell us what you were doing when the error occurred? </strong><br />
  eg. Error while editing the profile</label><br />
  <input id="summary" type="text" name="u_summary" size="80" value=""/>
  </p>

  <p>
  <label for="u_desc"><strong>Please take us through, step by step, what happened before the error
occurred. This will help us recreate what happened on our machines.</strong><br />
   eg. 1) Click edit in Profile section. <br/>
       2) Change the fax no.<br/>
  </label>
  <textarea id="description" name="u_desc" rows="10" cols="78"></textarea>
  </p>

  <input type="hidden" name="e_id" value="${e_id}"/>
  <input type="hidden" name="e_path" value="${e_path}"/>
  <input type="hidden" name="e_str" value="${e_str}"/>

  <p>
  <input type="submit" value="Submit ticket" />
  </p>
</form>

</body>
</html>
