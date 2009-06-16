<?python
from hubspace.utilities.uiutils import oddOrEven,c2s, print_error
from hubspace.utilities.dicts import AttrDict
from hubspace.model import group_types, group_type_labels
from sqlobject import AND
tg_errors = None
kwargs = None
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">    
    <h1>${_('Add a resource group')}</h1> 
    <form id="addResourceGroupForm">
  	<div class="dataBox">
		<div class="dataBoxHeader">
			<a class="title" id="link_addResourceGroupForm"><h2>${_('Resource Group')}</h2></a>
		</div>
	    <div class="dataBoxContent">
			<table class="detailTable data"> 
				<tr>
					<td class="line">${_('Name')}</td>
					<td><input name="name" type="text" value="${kwargs and kwargs.name or ''}"/><div class="errorMessage" py:if="tg_errors">${print_error('name', tg_errors)}</div></td>
				</tr>
	                        <tr>
					<td class="line">${_('Description')}</td>
					<td><textarea name="description">${kwargs and kwargs.description or ''}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('description', tg_errors)}</div></td>
				</tr>
                                <tr>
                                    <td class="line">${_('Group Type')}</td>
                                    <td>
                                         <select name="group_type"><option py:attrs="kwargs and kwargs.group_type==type and {'selected':'selected'} or {}" py:for="type in group_types" value="${type}">${group_type_labels[type]}</option></select>
                                         <div class="errorMessage" py:if="tg_errors">${print_error('group_type', tg_errors)}</div>
                                    </td>
                                </tr>
                       </table>
           </div>
     </div>
   </form>
        <input id="submit_create_resource_group" type="image" src="/static/images/button_save.gif" alt="${_('save')}" />
        <input id="cancel_create_resource_group" type="image" src="/static/images/button_cancel.gif"  alt="${_('cancel')}" />
</div>
