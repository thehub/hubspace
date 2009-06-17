function create_sortables(parent_obj){
    var loc = parent_obj.location;
    var sortable_sublist = function(id){
        var group = jq(id);
        var other_groups = jq.map(groups, function (n) {
           if (n===id) {
               return;
           } else {
               return n;
           }   
        });
        var obj = {
           element: group[0],
           create_sortable_group: function(){
              var that = this;
              group.sortable({containment: '#resource_groups_area', items: '> li.resource_item', connectWith: other_groups, update: function(){that.update()}, handle:'> .handle', over: that.expand_elements});
           },
           expand_elements: function (ev, ui) {
              parent_obj.open_res_group(jq(this).find('.expand_res_group'));
           },
           update: function () {
              if(lock){return}
              lock=true;
              serialize_all();
           }
        }
        obj.create_sortable_group();
        return obj
    }
    var order_saved = function () {
        overlib("order saved");
        lock=false;
        jq('body').oneTime("1s", function(){nd()});
    }
    var groups = jq('.resource_group');
    groups = jq.map(groups, function(ele){return '#'+ele.id});
    var lists = {};
    var lock = false;
    var sort = function(){
        jq.each(groups, function(n, id){
            lists[id] = sortable_sublist(id);
        });
        jq('#resource_groups').tableDnD({onDragClass:'dragClass', onDrop:serialize_all});
    };
    var serialize_all = function(){
        var params = {};
        var params_string = [];
        jq.each(lists, function(id, list){
            params[id] = jq(list.element).sortable('toArray');
            var hidden_input = jq(id + ' input.group_name');
            var name = 'res_group.' + hidden_input.val();
            jq.each(params[id], function(list_id, val){
                   var list_id = String(list_id+1);
                   params_string[params_string.length] = name +'-'+list_id +'='+val.split('-')[1];
            });
        });
        var groups_order = jq('.resource_group');
        groups_order = jq.map(groups_order, function(element, i){return 'group-'+String(i+1)+'='+element.id.split('-')[1]});
        params_string = params_string.concat(groups_order);
        params_string = params_string.concat('loc='+loc);
        params_string = params_string.join('&');
        jq.post('/save_res_groups', params_string, function () {
		order_saved();
        });
        return params_string
    }
    sort();
    return lists
}
