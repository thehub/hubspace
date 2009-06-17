<?python
from hubspace.controllers import permission_or_owner
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"  py:extends="'master.kid'">
<head py:match="item.tag=='head'">
</head>
<body py:match="item.tag=='body'" py:attrs="item.items()">
    <div id="current_user_id" class="${object.id}" style='display:none' />
    <div id="current_user_class" class="User" style='display:none' />
    <div id="networkContent" py:attrs="{'class':'area' in locals() and area=='network' and 'pane_selected' or 'pane'}">
            <c py:strip="True" py:if="'area' not in locals() or ('area' in locals() and area!='network')" >
                <?python
                    from hubspace.templates.network import network_skeleton
                ?>
                ${network_skeleton()}
            </c>
            <c py:if="'area' in locals() and area=='network'" py:replace="item[:]" py:strip="True" />
    </div>
    <div id="profileContent" py:attrs="{'class':'area' in locals() and area=='profile' and 'pane_selected' or 'pane'}">  
        <c py:if="'area' in locals() and area=='profile'" py:replace="item[:]" py:strip="True" />
    </div>
    <div id="spaceContent" class="pane">
    </div>
    <div id="hostContent" class="pane">
    </div>
    </body>
</html>
