<?python
#from hubspace.templates.todos import load_todos, render_todo
from hubspace.templates.invoicing import invoicing_search
from turbogears import identity
?>		
<div id="hostContent" class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">


<!--
<c py:if="'todo' in locals()" py:strip="True">
    ${render_todo(todo)}
</c>
-->
<c py:if="'todo' not in locals()" py:strip="True">
     <div class="subBar">
	<ul>
	    <!-- <li class="selected"><a style="cursor:pointer;" id="host-0" class="subsection">Todos</a></li> -->
	    <li class="selected"><a style="cursor:pointer;" id="host-0" class="subsection">Invoicing</a></li>
	    <li><a style="cursor:pointer;" id="host-1" class="subsection">Times</a></li>
	    <li><a style="cursor:pointer;" id="host-2" class="subsection">Administration</a></li>
	    <li><a style="cursor:pointer;" id="host-3" class="subsection">Resources and Tariffs</a></li>
	    <li><a style="cursor:pointer;" id="host-4" class="subsection">Management Data</a></li>
        </ul>
     </div>
     <div class="paneContent">
       <!--
       <div id="host-todosContent" class="subsectionContent">
           ${load_todos(object)}
       </div>
       -->
       <div id="host-resourcesContent" class="subsectionContent">
       </div>
       <div id="host-openTimesContent" class="subsectionContent">
       </div>
       <div id="host-adminContent" class="subsectionContent">
       </div>
       <div id="host-invoicingContent" class="subsectionContent">
           ${invoicing_search()}
       </div>
       <div id="host-managementdataContent" class="subsectionContent" style="display:none">
        abcf
       </div>

     </div>
</c>
</div>



