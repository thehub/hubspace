<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>
</head>
<body id="index">
        <div class="span-12" id="content-intro">
            <h1 class="text_small" id="title">${page.title and page.title or "The Hub King's Cross"}</h1>
            <h3 class="text_small" id="sub_title">${page.sub_title and page.sub_title or """A new members space for people working to create a better world."""}</h3>
            <div class="text_wysiwyg" id="content" py:if="page.content">${XML(page.content and page.content)}</div>
            <div class="text_wysiwyg" id="content" py:if="not page.content"><p>Another world is not just possible, it's happening. All around us individuals ranging from corporate executives to community leaders, from policy-makers to freelance professionals are pursuing ideas and initiatives for a better world. Hub Kings Cross is a unique ecosystem designed to enable these people to thrive. It's a place to access innovation, knowledge, market opportunities, inspiration and experience.</p><p>This beautiful listed building, one minute from Kings Cross station, offers an inspired place for meeting, working, innovating, learning and connecting. Members of Hub Kings Cross enjoy access to touchdown meeting and work spaces, a state of the art exhibition and events space, a bar with a cafe, and an evening programme of lectures, film, debates and music. You're invited. </p></div>
        </div>
        <div class="span-12 last">
            <div class="span-12 last content-sub" id="how-to-find">
                <h3 class="text_small" id="find_us_header">${page.find_us and page.find_us_header or "Find Us"}</h3>
                <div id="geo_address" class="gmap">${location.geo_address and location.geo_address or '34b York Way, London N1 9AB, UK'}</div>
                <div class="text_wysiwyg_small" id="find_us" py:if="not page.find_us"><p>Hub Kings Cross is based in the heart one of central London's most exciting areas. We are easily accessible by 5 different tube lines at <strong>Kings Cross St Pancras station</strong> and are located less than a 5 minute walk from the Eurostar terminal at the <strong>St Pancras International</strong> station.</p>
                <p><strong>Address:</strong> Hub Kings Cross, 34b York Way, London N1 9AB, UK</p></div>
                <div class="text_wysiwyg_small" id="find_us" py:if="page.find_us">${XML(page.find_us)}</div>
            </div>
            <div class="span-6 content-sub">
                <h3 class="text_small" id="parking_header">${page.parking_header and page.parking_header or "Parking"}</h3>
                <div class="text_wysiwyg_small" id="parking" py:if="not page.parking"><p>There are bike racks available for parking bicycles on Railway Street around the corner from the Hub Kings Cross.</p><p>For information on car parking, please download <a href="/static/files/ParkingNearHubKingsCross.pdf">this pdf</a>.</p></div>
                <div class="text_wysiwyg_small" id="parking" py:if="page.parking">${XML(page.parking)}</div>
            </div>
            <div class="span-6 last content-sub">
                <h3 class="text_small" id="opening_hours_header">${page.opening_hours_header and page.opening_hours_header or "Opening hours"}</h3>
                <div class="text_wysiwyg_small" id="opening_hours" py:if="not page.opening_hours"><p>The Hub Kings Cross is open to members from <strong>8am - 6pm, Monday-Friday</strong>, as a work and meeting space.</p><p>The Hub Kings Cross is open in the evening time from <strong>6.30pm up until midnight</strong> for private event hire and member events.</p></div>
                <div class="text_wysiwyg_small" id="opening_hours" py:if="page.opening_hours">${XML(page.opening_hours)}</div>
            </div>
        </div>
</body>
</html>

