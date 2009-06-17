<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'webSiteMaster.kid'">
<head>
</head>
<body>	
        <div class="left_column" id="Page-${page.id}-description" py:if="page.description">${XML(page.description)}</div>
	<div class="left_column" id="Page-${page.id}-description" py:if="not page.description">
		<blockquote>"Probably the most gutsy and dynamic event I have ever been to."</blockquote>
		<em>Dame Anita Roddick, founder of The Body Shop</em>
		<blockquote>"This place that has become known world-wide is proving what is possible."</blockquote>
		<em>Kofi Annan speaking on the Soweto Mountain of Hope, a Hub collaboration</em>
	</div>
        <div class="right_column" id="Page-${page.id}-content" py:if="page.content">${XML(page.content)}</div>
	<div class="right_column" id="Page-${page.id}-content" py:if="not page.content">
		<p>This is the amazing thing. We all have ideas. But where to go to make them happen? We've learnt that people and institutions working at the frontier of new innovations need access to the all the experience, resources, connections and investment they can muster. So we're dedicating ourselves to designing and hosting events and experiences that create access to the resources, connections, experience, knowledge and capital to support the journey path of ideas into action.</p>
		<p>Our events range from high-profile Hub Lectures, Thought Dinners and inter-disciplinary Innovation Labs to open-source Hub Lunches that foster peer-based learning and collaboration amongst our membership. <a href="places/kingscross/events.html"><strong>Featured Events: Hub Lectures</strong></a></p>
	</div>
</body>
</html>