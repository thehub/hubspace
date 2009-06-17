<?python
from hubspace.utilities.uiutils import oddOrEven, c2s
from hubspace.model import Pricing, Resource
from hubspace.controllers import get_pricing, resource_groups
from hubspace.utilities.image_helpers import image_src
odd_or_even = oddOrEven().odd_or_even

def add_req_resources(resource):
   return [res for res in resource.place.resources if res.time_based and res not in [resource]+resource.requires] 

def add_sug_resources(resource):
   return [res for res in resource.place.resources if res.type!='tariff' and res not in [resource]+resource.suggestions] 

def price(resource, tariff):
    pricing = get_pricing(tariff, resource)
    return c2s(pricing) 

from docutils.core import publish_parts
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
   <div py:def="requirements(resource)"  py:strip="True">
      <h2>Containment</h2>
      <p>Add resources which are contained by this one. In this case, if the container is booked the other will be unavailable. Also if the contained resource is booked the container will be unavailable. This also works for multiple levels of containment</p>
      <ul>
          <li py:if="not resource.requires">Nothing Contained</li>
          <li py:for="res in resource.requires"><span>${res.name} </span><a id="removereq-${resource.id}-${res.id}" class="removeRequirement button">Remove</a></li>
      </ul>
      <div py:if="add_req_resources(resource)">
      <select id="chooserequirement-${resource.id}">
          <option py:for="res in add_req_resources(resource)" value="${res.id}">${res.name}</option>
      </select>
      <a class="addRequirement button" id="addreq-${resource.id}">Add Contained Resource</a>
      </div>
   </div>
   <div py:def="suggestions(resource)" py:strip="True">
       <h2>Suggestions</h2>
       <p>Add suggestions so that when a user books a resource they are prompted to book associated extras. e.g. when booking a meeting room people might often also require a projector, tea, coffee, or lunch</p>
       <ul>
           <li py:if="not resource.suggestions">No Suggestions</li>
           <li py:for="res in resource.suggestions"><span>${res.name} </span><a id="removesug-${resource.id}-${res.id}" class="removeSuggestion button">Remove</a></li>
       </ul>
       <div py:if="add_sug_resources(resource)">
           <select id="choosesuggestion-${resource.id}">
               <option py:for="res in add_sug_resources(resource)" value="${res.id}">${res.name}</option>
           </select>
           <a class="addSuggestion button" id="addsug-${resource.id}">Add Suggestion</a>
       </div>
   </div>
    <div py:if="not 'resource' in locals()" id="extra_details" class="big_popup" title="Extra details">
        <a class="close_popup" title="close popup">X</a>
        <div class="popup_section" py:if="object.time_based">
           <h2>Resource Image</h2>
           <p>Optionally, an image will appear when a user tries to book a resource. If you want that to happen for this resource, replace the image below. Images will be scaled to 150px by 230px, please upload images of equivalent proportions.</p>
           <div class="imgwrap">
               <span id="upload_resimage" class="replace_image">replace image</span>
               <img id="resimage-${object.id}" src="${image_src(object, 'resimage', '/static/images/header.gif')}" /> 
           </div>
        </div>
        <div id="requirements-${object.id}" class="popup_section" py:if="object.time_based">
            ${requirements(object)}
        </div>
        <div id="suggestions-${object.id}" class="popup_section" py:if="object.time_based">
            ${suggestions(object)}
        </div>
    </div>
        <c py:if="'suggestion' in locals()" py:strip="True">           
            <li><span>${suggestion.name} </span><a id="removesug-${resource.id}-${suggestion.id}" class="removeSuggestion button">Remove</a></li>
        </c>
        <c py:if="'requirement' in locals()" py:strip="True">
            <li><span>${requirement.name} </span><a id="removesug-${resource.id}-${requirement.id}" class="removeRequirement button">Remove</a></li>
        </c>
</div>
