<?xml version="1.0" encoding="utf-8"?>
<?python
class name_attribute(dict):
    def __missing__(self, x):
        return 'name'

name_map = name_attribute({'User' : 'display_name'})
?>
<div xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
  <form id="${list_name}_form" action="${relative_path}lists/${list_mode=='add_existing' and 'append' or 'append_existing'}/${list_name}" method="Post">
    <table class="draglist" id="${list_name}_table">
        <tr>
           <th><a id="close_${list_name}"  href="#">close</a></th>
           <th>Name</th>
           <th>Type</th>
           <th>Page Type</th>
           <th>Active</th>
           <th>Delete</th>
        </tr>

        <tr id="${list_name}-${item.id}" class="active" py:for="item in list_items" >
           <td><img src="/static/images/drag.png" /></td>
           <td>${getattr(item.object, name_map[item.object_ref.object_type])}</td>
           <td>${item.object_ref.object_type}</td> 
           <td py:if="item.object_ref.object_type=='Page'">${page_types_dict[item.object_ref.object.page_type].name}</td>
           <td py:if="item.object_ref.object_type!='Page'">N/A</td> 
           <td><input class="active" name="active" type="checkbox" value="1" py:attrs="item.active and {'checked':'checked'} or {}" /></td>
           <td><a href="${relative_path}lists/${item.id}" class="delete_item">X</a></td> 
        </tr>
        <tr>
            <td>
            </td>
            <td py:if="list_mode=='add_new'" id="add"><input type="text" name="name" value="" /></td>
            <td py:if="list_mode=='add_existing'" id="add_existing"><input type="text" class="find_${list_types[0]}" id="display_name" name="get_object_id" value="" /><input type="hidden" id="object_id" name="object_id" value="0" /></td>
            <td><select name="object_type" id="object_type"><option py:for="type in list_types" value="${type}">${type}</option></select></td>
            <td><select name="page_type" id="page_type" py:if="type=='Page'"><option py:for="type in page_types" value="${type}">${page_types_dict[type].name}</option></select></td> 
            <td><input type="checkbox" checked="checked" name="active" value="1" /></td>
            <td class="add_remove"><input type="submit" value="Add" class="add_item" /></td>
        </tr>
    </table>
  </form>
</div>
