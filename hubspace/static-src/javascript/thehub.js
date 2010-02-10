var addthis_pub="benalexander";  //for addthis.com
var widget_map = {'PublicSpace':{'description':'text_wysiwyg_small',
                                 'image':'image'},
                  'PublicPlace':{'description':'text_wysiwyg_small',
                                 'image':'image'},
                  'Page':{'image':'image',
                          'description': 'text_wysiwyg',
                          'content': 'text_wysiwyg'},
                  'Location':{'micrologo':'image'}
};
var event_map = {'Location':{'micrologo': 'contextmenu'},
                 'Page': {'name': 'contextmenu',
                          'subtitle': 'contextmenu'},
                 'PublicSpace':{'name':'contextmenu'}
                };

var space_overlays = function () {
    jq('.meeting-room-info').hide();
    jq('#meeting-rooms ul li').click(function(event){
        jq('#meeting-rooms ul li').removeClass('selected');
        jq(this).addClass('selected');
        jq('#meeting-room-help').hide();
        jq('.meeting-room-info').hide();
        var id = jq(this).find('a').attr('id').split('-')[1];
        jq('#PublicSpace-' + id + '-description').parent().show();
        event.preventDefault();
    });
};


var plot_point = function(map, point) {
    map.setCenter(point, 15);
    var marker = new GMarker(point);
    map.addOverlay(marker);
};


var create_map = function (map_ele, callback) {
    if (GBrowserIsCompatible()) {
        location_str = map_ele.html();
        map_ele.html("");
        var map = new GMap2(map_ele.get(0));
        var geocoder = new GClientGeocoder();
        geocoder.getLatLng(location_str, function (point) {
           callback(map, point);
        });
    }
};


jq(document).ready(function () {
    if (window.set_ajax_globals) {
        set_ajax_globals();
    }

    jq("#places_list div").each(function (i, ele) {
        if (window.YAHOO) {
            var dot = new YAHOO.util.DD(ele.id);
            dot.on('endDragEvent', function (evt) {
                var ele = this.getEl();
                var raw = YAHOO.util.Dom.getXY(ele);
                var region = YAHOO.util.Dom.getRegion("worldmap");
                var left = raw[0] - region.left;
                var top = raw[1] - region.top;
                var page = jq('#page_path_name').attr('class');
                jq.post(relative_url + 'edit/attribute_edit', [{name: 'object_id', value: ele.id.split('-')[1]},
                                                               {name: 'value', value: top},
                                                               {name: 'page_name', value: page},
                                                               {name: 'property', value: 'top'},
                                                               {name: 'object_type', value: 'PublicPlace'}]);
                jq.post(relative_url + 'edit/attribute_edit', [{name: 'object_id', value: ele.id.split('-')[1]},
                                                               {name: 'value', value: left},
                                                               {name: 'page_name', value: page},
                                                               {name: 'property', value: 'left'},
                                                               {name: 'object_type', value: 'PublicPlace'}]);
            }, dot, true);
        }
    });

   window.source_no = 0;
   if (jq('#meeting-rooms').length) {
       space_overlays();
   }
   // members page
   // rollovers for members info
    
    jq(".bigpic").mouseover(function(){
        jq(this).next('span.member-bio span').css('opacity',0.9);
        jq(this).next('span.member-bio span').css('cursor', 'pointer');
        jq(this).next('span.member-bio span').fadeIn(350);
        jq(".member-bio").mouseover(function(){
            jq(this).show();
            return false;
        });
    });
    
    jq(this).mouseout(function () {
        jq("a.member-bio").hide();
        jq(".bigpic").css('opacity',1);
        return false;
    });
    
    //experience page slide show
    // add images to div
    if (jq('#experience #content-highlight').length) {
        //start the plugin
        jq('#experience #content-highlight').cycle();
        //remove background image so it doesn't show through when images fade
    }

        // initialise hub selector
    jQuery(function(){
        jQuery('ul.sf-menu').superfish();
    });
    
    jq('#z').css('z-index','100000');

    var object_id = null;
    var relative_url = jq('#relative_url').attr('class');
    var this_list = null;
    var list_manage = function () {
            this_list = jq(this);
            var list_name = jq(this).prev().attr('id');
            jq(this).after('<div id="'+ list_name + '_overlay"></div>');
            var load_area = jq(this).next();
            load_area.load(relative_url + 'lists/render_as_table/' + list_name, function () {activate(list_name, jq(this))});
    };

    //entry point for editing lists
    jq('.edit_list').one('click', list_manage);
    
    if (window.Upload) {
        object_id = jq('#location_id').attr('class');
        var image_url = '/static/{location_folder}/uploads/{attr_name}';
        jq('.file_upload').each(function () {
            var uploaded_image = new Upload(object_id, 'Location', jq(this).attr('id'), jq(this).get(0), jq(this).get(0), {'relative_url': relative_url +'edit/'});
        });
    }
    
    jq('#contact #geo_address').css({'width': '630px', 'height': '288px', 'float':'left', 'margin': '0', 'background-color':'#F4F4F4'});
    
    jq('#index #geo_address').css({'width': '220px', 'height': '200px', 'float':'left', 'margin': '0px 10px 10px 10px'});
    
    if (window.inplace_editor) {
        //new approach
        jq("[id^='PublicSpace-'], [id^='Page-'], [id^='PublicPlace-'], [id^='Location-']").each(function () { //substitute any type
            var element_id = jq(this).attr('id');
            var prop_data = element_id.split('-');
            var object_type = prop_data[0];
            var object_id = prop_data[1];
            var object_prop = prop_data[2];
            try {
                var widget_type = widget_map[object_type][object_prop];
            } catch(e) {
                var widget_type = 'text_small';
            }
            try {
                var edit_event = event_map[object_type][object_prop];
                if (!edit_event) {
                    edit_event = 'click';
                }
            } catch(e) {
                edit_event = 'click';
            }
            var clickToEdit = "Click To Edit";
            if (edit_event == 'contextmenu') {
                clickToEdit = "Right Click To Edit";
            }

            if (widget_type == 'image') {
                var options = {};
                if (object_type == 'PublicSpace') {
                    options = {'height':'300', 'width':'450'};
                }
                if (object_prop == 'micrologo') {
                    options['height'] = '70';
                }
                options['edit_event'] = edit_event;
                options['title'] = clickToEdit;
                options['relative_url'] = relative_url + 'edit/'
                new Upload(object_id, object_type, object_prop, jq(this).get(0), jq(this).get(0), options);
                return;
            }
            var page_name = jq('#page_path_name').attr('class');
            inplace_editor(element_id, relative_url + 'edit/attribute_edit', 
                           {callback: function (form, val) {
                                        return [{name: 'object_id', value: object_id},
                                                {name: 'value', value: val},
                                                {name: 'page_name', value: page_name},
                                                {name: 'property', value: object_prop},
                                                {name: 'object_type', value: object_type}];
                            },
                            object_type: object_type,
                            object_id: object_id,
                            ui_type: widget_type,
                            edit_event: edit_event,
                            clickToEditText: clickToEdit,
                            widget_id: element_id + '_widget',
                            widget_name: element_id,
                            property: object_prop,
                            value: jq('#' + element_id).html(),
                            loadTextURL: relative_url + 'edit/attribute_load?object_type=' + object_type +'&object_id=' + object_id + '&property=' + object_prop + '&default=' + encodeURIComponent(jq(this).html())} );
        });

       //old approach
               
        jq('.text_small, .text_large, .text_wysiwyg, .text_wysiwyg_small, .gmap').each(function () {
            var field_classes = jq(this).attr('class').split(' ');
            var widget_type = field_classes[field_classes.length - 1];
            var element_id = jq(this).attr('id');
            var edit_event = 'click';
            var clickToEdit = "Click To Edit";
            if (jq(this).parents().filter('#menu-top').length) {
               edit_event = 'contextmenu';
               clickToEdit = "Right Click To Edit";
            }
            
            if (jq(this).hasClass('gmap')) {
               var object_type = 'Location';
               var object_id = jq('#location_id').attr('class');
            } else {
               var object_type = 'Page';
               var object_id = jq('#page_id').attr('class');
            }
                       
            var page_name = jq('#page_path_name').attr('class');
            inplace_editor(element_id, relative_url + 'edit/attribute_edit', {
                           callback: function (form, val) {
                            return [{name: 'object_id', value: object_id},
                                    {name: 'object_type', value: object_type},
                                    {name: 'value', value: val},
                                    {name: 'page_name', value: page_name},
                                    {name: 'property', value: element_id}];
                            },
                            object_type: object_type,
                            object_id: object_id,
                            ui_type: widget_type,
                            edit_event: edit_event,
                            clickToEditText: clickToEdit,
                            widget_id: element_id + '_widget',
                            widget_name: element_id,
                            property: element_id,
                            value: jq('#' + element_id).html(),
                            loadTextURL: relative_url + 'edit/attribute_load?object_type=' + object_type + '&object_id=' + object_id + '&property=' + element_id + '&default=' + encodeURIComponent(jq(this).html())

            });
        });
    }

    if (jq('.gmap').length) {
        create_map(jq('#geo_address'), plot_point);
    }
    
    var activate = function (list_name, load_area) {
        activate_list(list_name);
        //autocomplete the object_id field from a search on a different property which is a string
        var object_type = jq('#object_type option:selected').val();
        var autocomplete_property = jq('.find_' + object_type).attr('id');
        jq("#display_name").autocomplete(relative_url + 'edit/auto_complete/' + object_type + '/' + autocomplete_property, {width: 260,
                                                                                                                            selectFirst: true,
                                                                                                                            matchSubset: false});
        jq("#display_name").result(function (event, data, formatted) {
            jq('#object_id').val(data[1]);
        });
        
        jq('a#close_' + list_name).click(function () {
            jq('div#'+ list_name + '_overlay').remove();
            //this_list.one('click', list_manage);
            window.location.reload();
        });

        var options = {'action': function (ele) {
            var method = 'remove';
            if (jq('td#add_existing').length) {
                var method = 'remove_existing';
            }
            
            load_area.load(relative_url + 'lists/' + method + '/'  + list_name + '/' + jq(ele).parent().parent().attr('id').split('-')[1], function () {
                activate(list_name, load_area);
            });
        },
        'message': "Really delete this page?"
        };
        
        jq('table#' + list_name + '_table .delete_item').confirm_action(options);
        
        jq('table#' + list_name + '_table input.add_item').click(function () {
            if (jq('#add').length) {
                var append_method = 'append';
            } else if (jq('#add_existing').length) {
                var append_method = 'append_existing';
            }
            load_area.load(relative_url + 'lists/' + append_method + '/'  + list_name, jq('form#' + list_name + '_form tr:last :input').serializeArray(), function () {activate(list_name, load_area);});
                return false;
        });
        
        jq('table#' + list_name + '_table input.active').click(function () {
            if (jq(this).parent().find(':checked').length) {
                var active_data = [{'name':'active', 'value': jq(this).val()}];
            } else {
                var active_data = [];
            }
            load_area.load(relative_url + 'lists/toggle_active/'  + list_name + '/' + jq(this).parent().parent().attr('id').split('-')[1], active_data, function () {
                activate(list_name, load_area);
            });
            return false;
        });
    };
});

