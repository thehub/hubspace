<?python
from docutils.core import publish_parts
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
     <div  py:def="load_memberDescription(object)" py:strip="True">
           <div  py:if="object.description" py:strip="True">
                    ${XML(publish_parts(object.description, writer_name="html")["html_body"])}
           </div>
       </div>
       ${load_memberDescription(object)}
</div>
