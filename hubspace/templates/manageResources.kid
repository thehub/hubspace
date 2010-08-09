<?python
from hubspace.utilities.uiutils import oddOrEven, c2s
from hubspace.model import Pricing, Resource, group_type_labels, group_types_descriptions
from hubspace.controllers import get_pricing, resource_groups
from docutils.core import publish_parts

odd_or_even = oddOrEven().odd_or_even

def price(resource, tariff):
    pricing = get_pricing(tariff, resource)
    return c2s(pricing) 

def order_resources(group):
    # #461
    resources_order = group.resources_order
    resources = [Resource.get(res_id) for res_id in resources_order]
    resources = resources + [resource for resource in group.resources if resource.id not in resources_order]
    return resources

def get_deletable_resources(location):
    from sqlobject.sqlbuilder import EXISTS, Select
    from sqlobject import AND, OR, DESC, NOT, IN
    from hubspace.model import RUsage
    resources_can_be_deleted = list( Resource.select(AND(Resource.q.place==location.id, NOT(IN(Resource.q.id, Select(RUsage.q.resourceID, distinct=True))))) )
    return resources_can_be_deleted
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
   <div class="dataBox" py:def="resource_table(object)"> <div class="dataBoxHeader">
   <?python
    resources_can_be_deleted = get_deletable_resources(object)
   ?>
           <a class="modify" id="addResource" href="#add_resource">Add Resource</a>
           <a class="modify" id="addResourceGroup" href="#add_resource">Add Resource Group</a>
           <a class="title" id="link_addResources"><h2>Resources</h2></a>
       </div>
       <div class="dataBoxContent" id="resource_groups_area" >
           <div><p>Order the "resource groups" listed below using the arrows.  The order determines the resource group order in the booking interface. You can also drag and drop resource between groups and reorder resources within groups</p></div>
           <table id="resource_groups" class="detailTable data">
               <tr class="header" nodrag="true" nodrop="true">
                 <th>
                   <div class="resourceName">Name</div>
                   <div class="resourceDescription">Description</div>
                   <div class="resourceType">Type</div>
                   <div class="resourceTimeBased">Time Based</div>
                   <div class="resourceVAT">Percentage VAT (0-100)</div>
                   <div class="resourceActive">Active</div>
                 </th>
               </tr>
               <tr py:for="group in resource_groups(object)">
                   <td class="updown" title="drag using arrows on the left to reorder resource groups">
                       <ul class="resource_group" id="res_group-${group.id}">
                           <li class="resource_group_header">
                             <input class="group_name" value="${group.id}" type="hidden" />
                             <div class="res_group_divs">
                               <div class="res_group_attrs">
                                   <div class="resourceGroupName"><h1 id="resourceGroupName_${group.id}">${group.name}</h1><a py:if="group.id" id="resourceGroupName_${group.id}Edit" class="button">edit</a>
                                   </div>
                                   <div title="${group_types_descriptions[group.group_type]}">(${group_type_labels[group.group_type]})</div>
                                   <div class="res_group_desc"><span class="resourceGroupDesc" id="resourceGroupDesc_${group.id}">${XML(publish_parts(group.description, writer_name="html")["html_body"])}</span><a py:if="group.id" id="resourceGroupDesc_${group.id}Edit" class="button">edit</a></div>                                                           </div>
                               <div class="res_group_actions"> 
                                   <div class="del_res_group" py:if="group.id"><a href="delete_resource_group?group_id=${group.id}" id="delete-${group.id}">Delete resource group</a></div>
                               </div>
                               <div>
                                   <div class="expand_res_group">
                                       <img src="/static/images/arrow_right_resourcetable.png" /><div>See resources in this group</div>
                                   </div>
                               </div>
                             </div>
                           </li>
                         <c py:strip="True" py:for="resource in order_resources(group)">
                           <li title="drag the resource using arrows to the left re-order it" id="item-${resource.id}" class="resource_item">
                               <div class="handle"></div>
                               <div class="resourceName"><span id="resourceName_${resource.id}">${resource.name}</span><a id="resourceName_${resource.id}Edit" class="button">edit </a>
                               <br/>
                               <a py:if="resource in resources_can_be_deleted" class="button res_delete" title="Delete Resource" id="resource_delete-${resource.id}">Delete</a>
                               </div>
                               <div class="resourceDescription"><span id="resourceDescription_${resource.id}">${resource.description}</span><a id="resourceDescription_${resource.id}Edit" class="button">edit</a></div>
                               <div class="resourceType"><span id="resourceType_${resource.id}">${resource.type}</span><a id="resourceType_${resource.id}Edit" class="button">edit</a></div>
                               <div class="resourceTimeBased">${resource.time_based and 'true' or 'false'}</div>
                               <div class="resourceVAT"><span id="resourceVAT_${resource.id}">${[resource.place.vat_default, resource.vat][type(resource.vat)==float]}</span><a id="resourceVAT_${resource.id}Edit" class="button">edit</a></div>
                               <div py:if="not resource.active" class="resourceActive">Inactive <a class="button activate" id="activeness-${resource.id}">activate</a></div>
                               <div py:if="resource.active" class="resourceActive">Active <a class="button activate" id="activeness-${resource.id}">de-activate</a></div>
                               <div py:if="resource.time_based" class="more_res_details" id="res_details-${resource.id}" title="more details"><a href="/more_res_details">more...</a> </div>
                               <div class="extra_details"></div>
                           </li>
                         </c>
                           <li class="clear_both"></li>
	               </ul>	
                   </td>
               </tr>
           </table>
       </div>
       <a name="add_resource"></a>
       <div id="tariff_resources">
       </div>
    </div>
    <c py:if="not 'resource' in locals()">${resource_table(object)}</c>
</div>
