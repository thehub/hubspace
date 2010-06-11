<?python
from docutils.core import publish_parts
from hubspace.utilities.uiutils import sanitize_input
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
     <div  py:def="load_memberDescription(object)" py:strip="True">
           <div  py:if="object.description" py:strip="True">
                <?python
                    description = object.description
                    if '<br>' in description or '<br >' in description or '</b>' in description or '</div>' in description or '</p>' in description:
                        content = sanitize_input(description)
                    else:
                        content = publish_parts(description, writer_name="html")["html_body"]
                ?>
                ${XML(content)}
           </div>
       </div>
       ${load_memberDescription(object)}
</div>
