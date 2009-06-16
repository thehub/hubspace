<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'webSiteMaster.kid'">
<head>
</head>
<body>	
    <div id="Page-${page.id}-description" py:if="page.description">${XML(page.description)}</div>
    <div id="Page-${page.id}-description" py:if="not page.description">
        <ul id="home_navigation">
		<li><a href="people.html"><em>People</em> who see and do things differently</a></li>
		<li><a href="places.html"><em>Places</em> for working, meeting, innovating, learning and relaxing</a></li>
		<li><a href="ideas.html" ><em>Ideas</em> that might just change the world a little</a></li>
		<li class="last"><a href="about.html">About</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;<a href="invitation.html">Invitation</a></li>
 	</ul>
    </div>
    <div id="Page-${page.id}-content" py:if="page.content">${XML(page.content)}</div>
    <div id="Page-${page.id}-content" py:if="not page.content">
	<ul id="featured">
		<li>
			<a href="people/ethical_fashion.html">
				<img src="/static/images/hubweb/featured_member.jpg" alt=""/>
				<span>Featured Member:<br />Tamsin Lejeune</span>
			</a></li>
		<li>
			<a href="places/kingscross.html">
				<img src="/static/images/hubweb/featured_hub.jpg" alt=""/>
				<span>Featured Hub:<br />Kings Cross</span>
			</a>
		</li>
		<li>
			<a href="places/kingscross/events.html">
				<img src="/static/images/hubweb/featured_event.jpg"  alt="" />
				<span>Featured Event:<br />Hub Lectures</span>
			</a>
		</li>
	</ul>
   </div>
</body>
</html>