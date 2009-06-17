<?python
from hubspace.utilities.uiutils import oddOrEven,c2s, print_error
from hubspace.utilities.dicts import AttrDict
odd_or_even = oddOrEven().odd_or_even
from hubspace.model import Resource
from sqlobject import AND
args = None
tg_errors = None
def resources(location):
    return Resource.select(AND(Resource.q.placeID==location.id,
                               Resource.q.type!='tariff'))

def print_resource_error(tg_errors, no):
    if tg_errors:
        if 'resources' in tg_errors:
            error = tg_errors['resources'].error_list[no]
            if error:
                 return str(error)
    return ""  

def resource_cost(args, resource):
    if args and args['resources']: 
        for res in args['resources']:
            if int(res['id'])==resource.id:
                try:
                    return c2s(res['cost'])
                except:
                    return res['cost']
    return c2s(0)

def this_tariff_cost(object):
    if isinstance(object, AttrDict):
        if object.tariff_cost:
            try:
                return c2s(object.tariff_cost)
            except:
                return object.tariff_cost
    return c2s(0)
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">    
      
     <h1>Add a Tariff</h1>
     <form id="addTariffForm">
  	<div class="dataBox">
		<div class="dataBoxHeader">
			<a id="link_addTariff" class="title"><h2>Tariff details</h2></a>
		</div>
	    <div class="dataBoxContent">
			<table class="detailTable data">	
                                <tr class="${odd_or_even()}">
					<td class="line">Name</td>
					<td><input name="name" type="text" value="${args and args.name or ''}"/><div class="errorMessage" py:if="tg_errors">${print_error('name', tg_errors)}</div></td>
				</tr>
	                        <tr class="${odd_or_even()}">
					<td class="line">Description</td>
					<td><textarea name="description">${args and args.description or ''}</textarea><div class="errorMessage" py:if="tg_errors">${print_error('description', tg_errors)}</div></td>
				</tr>
                                <tr class="${odd_or_even()}">
					<td class="line">Active</td>
					<td><select name="active"><option value="True">Active</option><option value="False">Inactive</option></select></td>
                                </tr>
                                <tr class="${odd_or_even()}">
					<td class="line">Tariff Price</td>
					<td><input name="tariff_cost" value="${this_tariff_cost(args)}" /><div class="errorMessage" py:if="tg_errors">${print_error('tariff_cost', tg_errors)}</div></td>
				</tr>
			</table>	
	    </div>
     </div>
     
     <div class="dataBox">
		<div class="dataBoxHeader">
			<a id="link_tariffAddRes" class="title"><h2>Resource costs</h2></a>
		</div>
	    <div class="dataBoxContent">
			<table class="detailTable data">
				<tr class="header">
					<td class="line">Resource</td>
					<td>Cost</td>
				</tr>
                                <?python
                                no = 0
                                ?>       
				<tr class="${odd_or_even()}" py:for="resource in resources(object)">
					<td class="line">${resource.name}</td>
					<td><input type="text" name="resources-${resource.id}.cost" value="${resource_cost(args, resource)}" />
                                            <input type="hidden" name="resources-${resource.id}.id" value="${resource.id}" />
                                            <div class="errorMessage" py:if="tg_errors">${print_resource_error(tg_errors, no)}</div>
                                        </td>
                                   <?python
                                   no += 1
                                   ?>
				</tr>
			</table>	
	    </div> 
     </div>		
     </form>
	     <input id="submit_create_tariff" type="image" src="/static/images/button_save.gif" alt="${_('save')}" />
	     <input id="cancel_create_tariff" type="image" src="/static/images/button_cancel.gif" alt="${_('cancel')}" />
</div>
