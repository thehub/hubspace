<?python
from hubspace.validators import timeconverter, datetimeconverter2 as dt
event = None
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>
</head>
<body id="events">
    <div class="span-12" id="content-intro" py:if="not event">
      <h1 id="title" class="text_small">${page.title and page.title or "The Events"}</h1>
      <div py:if="page.content" class="text_wysiwyg" id="content">${XML(page.content)}</div>
      <div py:if="not page.content" class="text_wysiwyg" id="content">
          <h2>Events subtitle</h2>
          <p>From debates and Q &amp; A's to lectures and thought seminars, the Hub's inspirational events will aim to bring together unlikely allies, cut across societal and industry boundaries and challenge our members to create and lead new initiatives that address some of the world's most intractable problems.</p>
          <p>The power of art and culture to drive imaginative and interesting ideas is something close to the ethos of Hub and is reflected in our programming mix. Working with local creative artists, architects, developing film makers, and interesting musical groups, Hub Kings Cross will deliver an eclectic assortment of cultural events including exhibitions, recitals, film and documentary screenings.</p>
          <h3>WANT TO HAVE YOUR EVENT AT THE HUB KINGS CROSS?</h3>
          <p>The Hub Kings Cross can also be rented for private events during the evening from 6.00pm. The Hub has a capacity of 130 and is fully licensed to serve alcohol and play music. Private events at the Hub Kings Cross are delivered in partnership with Eat Green, renown for their ability to combine ethics with high quality food and service.</p>
          <p>For more information please email the team at: <a href="mailto:kingcross.events@the-hub.net">kingcross.events@the-hub.net</a> or call us on <strong>0207 841 3450</strong>.</p>
       </div>
    </div>

    <div class="span-12" py:if="event">
	<div id="hubHomeContent" class="clearfix">
		<div id="main" class=" content-sub">
			<div id="pub_event" class="update_item">
			<h3 class="text_small">${event.meeting_name}</h3>
				<div class="profileDetails">
				   <div class="property"><div class="propertyTitle">Organisation:</div><div class="propertyValue">${event.user.organisation}</div>
				   </div>
				   <div class="property"><div class="propertyTitle">Location:</div><div class="propertyValue">${event.resource.place.name} - ${event.resource.name}</div>
				   </div>
				   <div class="property"><div class="propertyTitle">Date:</div><div class="propertyValue">${dt.from_python(event.start)} - ${timeconverter.from_python(event.end_time)}</div>
				   </div>
				   <div py:if="event.meeting_description" class="property"><div class="propertyTitle">Description:</div><div class="propertyValue description">${event.meeting_description}</div>
				   </div>
                    <div><a href="${relative_path}icalfeed.ics/${event.id}">iCal</a></div>
				   <div><div><p class="backLink"><a href="../events.html">back to Events Page</a></p></div></div>
				</div>
			</div>
		</div>
	</div>
    </div>
    <div class="span-12 last">
        <div class="span-6 content-sub" id="upcoming-events">
          <h3 id="upcoming_events" class="text_small">${page.upcoming_events and page.upcoming_events or "Upcoming Events"}</h3>
          <ul>
            <li py:for="ev in future_events" class="event">
              <h4><a href="${relative_path}events/${ev.id}">${ev.meeting_name}</a></h4>
              <p class="event-date">${dt.from_python(ev.start)}</p>
              <p class="event-desc">${ev.meeting_description.split('.')[0] + '.'}</p>
            </li>
          </ul>
          <div><a href="${relative_path}icalfeed.ics">all events in iCal format</a></div>
      </div>
      <div class="span-6 last content-sub" id="past-events">
          <h3 id="past_events" class="text_small">${page.past_events and page.past_events or "Past Events"}</h3>
          <ul>
            <li py:for="ev in past_events" class="event">
              <h4><a href="${relative_path}events/${ev.id}">${ev.meeting_name}</a></h4>
              <p class="event-date">${dt.from_python(ev.start)}</p>
              <p class="event-desc">${ev.meeting_description.split('.')[0] + '.'}</p>
            </li>
          </ul>
      </div>
</div>
	  <div id="rss"><a href="/feed/rss2_0/events/${location.id}"><img src="/static/images/micro/page/rss-icon.gif" alt="rss feed" /></a></div>
</body>
</html>

