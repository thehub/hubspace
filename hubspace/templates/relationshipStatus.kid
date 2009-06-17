<?python
from hubspace.utilities.uiutils import oddOrEven, attr_not_none, get_freetext_metadata
oddness = oddOrEven()
?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
          <div py:def="load_relationship_status(object)" py:strip="True">
	       <table class="servicesTable data" cellpadding="" cellspacing="0">
                   <tr> 
                       <td class="line">Introduced By</td>
                       <td py:if="get_freetext_metadata(object, 'introduced_by')" >${get_freetext_metadata(object, 'introduced_by')}</td>
                       <td py:if="not get_freetext_metadata(object, 'introduced_by')" >Unknown</td>
                   </tr>
                   <tr>
                       <td class="line">Signed Up By</td>
                       <td py:if="attr_not_none(object, 'signedby')">${object.signedby.user_name}</td>
                       <td py:if="not attr_not_none(object, 'signedby')">Unknown</td>
                   </tr>
                   <tr>
                       <td class="line">Host Contact</td>
                       <td py:if="attr_not_none(object, 'hostcontact')">${object.hostcontact.user_name}</td>
                       <td py:if="not attr_not_none(object, 'hostcontact')">Unknown</td>
                   </tr>
	   </table>
     </div>
${load_relationship_status(object)}	
</div>
