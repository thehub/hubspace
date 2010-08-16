<?python
from hubspace.utilities.permissions import user_locations
from hubspace.utilities.uiutils import select_home_hub
?>

<c xmlns:py="http://purl.org/kid/ns#" py:strip="True">
<div py:def="locationselect(user, perms, inptype='checkbox', classname='')" py:strip="True">
    <?python
    locations = user_locations(user, perms)
    ?>
    <select py:if="inptype=='select'" name="location_id" class="${classname}">
        <option py:for="location in locations" py:attrs="select_home_hub(location)" value="${location.id}">${location.name}</option>
    </select>
    <c py:if="inptype=='checkbox'" py:for="loc in locations" py:strip="True">
        <input type="checkbox" name="location_id" value="${loc.id}" classname="${classname}" py:attrs="select_home_hub(loc,'checked')"/>${loc.name}
    </c>
</div>
</c>
