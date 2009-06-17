<?python
from turbogears import identity
from hubspace.utilities.permissions import is_host
render_static = False
def non_empty_gen(gen):
    try:
        space = gen.next()
        if not space.active:
            return non_empty_gen(gen)
        return True
    except StopIteration:
        return False
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>
</head>
<body id="spaces">
    <div class="span-12" id="content-intro">
       <h1 id="title" class="text_small">${page.title and page.title or "Spaces"}</h1>
       <div py:if="page.content" class="text_wysiwyg" id="content">${XML(page.content)}</div>
       <div py:if="not page.content" class="text_wysiwyg" id="content">
           <p>The Hub Kings Cross is an inspiring contemporary environment to work, meet or host your event. Designed and built with sustainability principles in mind, our space is completely unique and encourages a creative working atmosphere.</p>
           <p>Our downstairs gallery space incorporates a cafe and is a great place for members to have informal meetings over a Fairtrade coffee or do some light working. Upstairs, our combination of tables, beanbags and benches offer an inspiring space to work.</p>
           <p>At the mezzanine levels or private meeting rooms can host meetings from 4 to 20 people. Each room is unique and has a range of conferencing tools, including plasma screens, projectors, whiteboard walls, teleconferencing and controllable lighting. Catering is available on request. All our food is Fairtrade, organic or locally sourced where possible.</p>
           <p>The Hub Kings Cross's adaptable gallery and library space is ideal for holding larger private events such as team days, product launches and formal/informal receptions.</p>
       </div>
    </div>  
    <div class="span-12 last">
        <div py:if="non_empty_gen(lists('spaces_list')) or is_host(identity.current.user, location, render_static)" class="span-12 last content-sub" id="meeting-rooms">  
            <h3 id="meeting_rooms" class="text_small">${page.meeting_rooms and page.meeting_rooms or "Meeting Rooms"}</h3>
            <ul class="hublist" id="spaces_list" >
                <li py:for="menu_item in lists('spaces_list')" py:if="menu_item.active"><a href='#' title="${menu_item.object.name}" id="PublicSpace-${menu_item.object.id}-name">${menu_item.object.name}</a></li>
            </ul>
            <div py:if="is_host(identity.current.user, location, render_static)" class="edit_list" >Edit List</div>
            <div id="meeting-room-help">
                <div py:if="page.meeting_rooms_intro" class="text_wysiwyg_small" id="meeting_rooms_intro">${XML(page.meeting_rooms_intro)}</div>
                <div py:if="not page.meeting_rooms_intro" class="text_wysiwyg_small" id="meeting_rooms_intro"><p>Please click a meeting room above to view details.</p></div>  
            </div>
            <div py:for="menu_item in lists('spaces_list')" class="meeting-room-info">
                <div py:if="menu_item.object.description" class="space_description" id="PublicSpace-${menu_item.object.id}-description">
                      ${XML(menu_item.object.description)}
                </div>
                <div py:if="not menu_item.object.description" class="space_description" id="PublicSpace-${menu_item.object.id}-description" >
                    <p>${menu_item.object.name} description</p>
                </div>
                <img height="300px" width="450px" id="PublicSpace-${menu_item.object.id}-image" src="${menu_item.object.image_name and upload_url + menu_item.object.image_name or '/static/images/micro/spaces/study.jpg'}" alt="${menu_item.object.name}"/>
            </div>
        </div>
</div>
</body>
</html>
