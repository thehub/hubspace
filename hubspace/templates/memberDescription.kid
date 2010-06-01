<?python
from docutils.core import publish_parts
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
     <div  py:def="load_memberDescription(object)" py:strip="True">
           <div  py:if="object.description" py:strip="True">
                <?python
                    description = object.description
                    if 'class=dataBoxContent' in description and 'dataTextBox' in description:
                        content = description
                    else:
                        content = publish_parts(description, writer_name="html")["html_body"]
                ?>
                ${XML(content)}
           </div>
       </div>
       ${load_memberDescription(object)}
</div>
