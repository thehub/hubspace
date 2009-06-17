<?python
from hubspace.utilities.uiutils import oddOrEven,c2s
odd_or_even = oddOrEven().odd_or_even
?>
<div id="addResourcesContent" class="pane" xmlns:py="http://purl.org/kid/ns#" py:strip="True">    
  	<h1>Resources and Tariffs</h1>
  	<div class="dataBox">
		<div class="dataBoxHeader">
			<a class="modify">Add new resource</a><a class="title" id="link_addResources"><h2>Resources</h2></a>
		</div>
	    <div class="dataBoxContent">
	    	<table class="detailTable data">
				<tr class="odd">
					<td class="line">Resource 1</td>
					<td>Description goes here</td>
					<td><a href="#">edit</a></td>
				</tr>
				<tr class="even">
					<td class="line">Resource 2</td>
					<td>Description goes here</td>
					<td><a href="#">edit</a></td>
				</tr>
				<tr class="odd">
					<td class="line">Resource 3</td>
					<td>Description goes here</td>
					<td><a href="#">edit</a></td>
				</tr>
				<tr class="even">
					<td class="line">Resource 4</td>
					<td>Description goes here</td>
					<td><a href="#">edit</a></td>
				</tr>
			</table>	
	    </div>
     </div>
  	<div class="dataBox">
		<div class="dataBoxHeader">
			<a class="modify">Add new tariff</a><a id="link_addTariff" class="title"><h2>Tariffs</h2></a>
		</div>
	    <div class="dataBoxContent">
			<table class="detailTable data">
				<tr class="odd">
					<td class="line">Tariff 1</td>
					<td>Description goes here</td>
					<td><a href="#">edit</a></td>
				</tr>
				<tr class="even">
					<td class="line">Tariff 2</td>
					<td>Description goes here</td>
					<td><a href="#">edit</a></td>
				</tr>
				<tr class="odd">
					<td class="line">Tariff 3</td>
					<td>Description goes here</td>
					<td><a href="#">edit</a></td>
				</tr>
				<tr class="even">
					<td class="line">Tariff 4</td>
					<td>Description goes here</td>
					<td><a href="#">edit</a></td>
				</tr>
			</table>	
	    </div>
     </div>
  	
  	
  	
  	
  	
  	<h1>Add a resource</h1>
  	<div class="dataBox">
		<div class="dataBoxHeader">
			<a class="title" id="link_addResourceForm"><h2>Resource details</h2></a>
		</div>
	    <div class="dataBoxContent">
			<table class="detailTable data">
				<tr class="odd">
					<td class="line">Name</td>
					<td><input type="text" /></td>
				</tr>
				<tr class="even">
					<td class="line">Location</td>
					<td><select><option>London</option><option>Bristol</option></select></td>
				</tr>
				<tr class="odd">
					<td class="line">Type</td>
					<td><select><option>hotdesk</option><option>room</option><option>phone</option><option>printer</option><option>tariff</option><option>other</option></select></td>
				</tr>
				<tr class="even">
					<td class="line">Description</td>
					<td><textarea></textarea></td>
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
					<td class="line">Tariff</td>
					<td>Cost</td>
				</tr>
				<tr class="odd">
					<td class="line">Tariff 1</td>
					<td><input type="text" /></td>
				</tr>
				<tr class="even">
					<td class="line">Tariff 2</td>
					<td><input type="text" /></td>
				</tr>
				<tr class="odd">
					<td class="line">Tariff 3</td>
					<td><input type="text" /></td>
				</tr>
				<tr class="even">
					<td class="line">Tariff 4</td>
					<td><input type="text" /></td>
				</tr>
			</table>	
	    </div>
     </div>
     <input type="image" src="/static/images/button_save.gif" alt="save" />
     <input type="image" src="/static/images/button_cancel.gif" alt="cancel" />
     
	<h1>Add a Tariff</h1>
  	<div class="dataBox">
		<div class="dataBoxHeader">
			<a id="link_addTariff" class="title"><h2>Tariff details</h2></a>
		</div>
	    <div class="dataBoxContent">
			<table class="detailTable data">
				<tr class="odd">
					<td class="line">Name</td>
					<td><input type="text" /></td>
				</tr>
				<tr class="even">
					<td class="line">Location</td>
					<td><select><option>London</option><option>Bristol</option></select></td>
				</tr>
				<tr class="even">
					<td class="line">Description</td>
					<td><textarea></textarea></td>
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
				<tr class="odd">
					<td class="line">Resource 1</td>
					<td><input type="text" /></td>
				</tr>
				<tr class="even">
					<td class="line">Resource 2</td>
					<td><input type="text" /></td>
				</tr>
				<tr class="odd">
					<td class="line">Resource 3</td>
					<td><input type="text" /></td>
				</tr>
				<tr class="even">
					<td class="line">Resource 4</td>
					<td><input type="text" /></td>
				</tr>
			</table>	
	    </div>
     </div>		
     <input type="image" src="/static/images/button_save.gif" alt="save" />
     <input type="image" src="/static/images/button_cancel.gif" alt="cancel" />

</div>
