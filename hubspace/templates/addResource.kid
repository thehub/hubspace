<?python
from hubspace.utilities.uiutils import oddOrEven,c2s, print_error
from hubspace.utilities.dicts import AttrDict
odd_or_even = oddOrEven().odd_or_even
from hubspace.model import resource_types, Resource

res_types = [type for type in resource_types if type not in ['calendar', 'tariff']]

from sqlobject import AND
tg_errors = None
args = None

def print_tariff_error(tg_errors, no):
    if tg_errors:
        if 'tariffs' in tg_errors:
            error = tg_errors['tariffs'].error_list[no]
            if error:
                 return XML(str(error))
    return ""         


def tariffs(location):
    return Resource.select(AND(Resource.q.placeID==location.id,
                               Resource.q.type=='tariff'))

def tariff_cost(args, tariff):
    if args and args['tariffs']:
        for tar in args['tariffs']:
             if int(tar['id'])==tariff.id:
                 try:
                     return c2s(tar['cost'])
                 except:
                     return tar['cost']
    return c2s(0)
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">    
    <h1>${_('Add a resource')}</h1> 
    <form id="addResourceForm">
  	<div class="dataBox">
		<div class="dataBoxHeader">
			<a class="title" id="link_addResourceForm"><h2>${_('Resource details')}</h2></a>
		</div>
	    <div class="dataBoxContent">
			<table class="detailTable data"> 
				<tr class="${odd_or_even()}">
					<td class="line">${_('Name')}</td>
					<td><input name="name" type="text" value="${args and args.name or ''}"/><div class="errorMessage" py:if="tg_errors">${print_error('name', tg_errors)}</div></td>
				</tr>
	                        <tr class="${odd_or_even()}">
					<td class="line">${_('Description %s'%(args and args.description or ''))}</td>
					<td><textarea name="description">${args and args.description or ''}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('description', tg_errors)}</div></td>
				</tr>
				<tr class="${odd_or_even()}">
					<td class="line">Time-Based</td>
					<td><select name="time_based"><option value="True">Time-Based</option><option value="False">Quantity-Based</option></select></td>
				</tr>
                                <tr class="${odd_or_even()}">
					<td class="line">Active</td>
					<td><select name="active"><option value="True">Active</option><option value="False">Inactive</option></select></td>
				</tr>
				<tr class="${odd_or_even()}">
					<td class="line">Type</td>
					<td><select name="type"><option py:attrs="args and args.type==type and {'selected':'selected'} or {}" py:for="type in res_types" value="${type}">${type}</option></select></td>
				</tr>
			
			</table>	
	    </div>
     </div>

     <div class="dataBox">
		<div class="dataBoxHeader">
			<a id="link_resAddTariffs" class="title"><h2>Tariff costs</h2></a>
		</div>
	    <div class="dataBoxContent">
			<table class="detailTable data">
				<tr class="header">
					<td class="line">${_('Tariff')}</td>
					<td>Cost</td>
				</tr>
                                <?python
                                no = 0
                                ?>
				<tr class="${odd_or_even()}" py:for="tariff in tariffs(object)">
  
					<td class="line">${tariff.name}</td>
					<td><input type="text" name="tariffs-${tariff.id}.cost" value="${tariff_cost(args, tariff)}"/>
                                            <input type="hidden" name="tariffs-${tariff.id}.id" value="${tariff.id}" />
                                           <div class="errorMessage" py:if="tg_errors">${print_tariff_error(tg_errors, no)}</div></td>
                               <?python
                                no += 1
                                ?>
				</tr>
			</table>	
	    </div>
     </div>
    
   </form>
     <input id="submit_create_resource" type="image" src="/static/images/button_save.gif" alt="${_('save')}" />
     <input id="cancel_create_resource" type="image" src="/static/images/button_cancel.gif"  alt="${_('cancel')}" />
</div>
