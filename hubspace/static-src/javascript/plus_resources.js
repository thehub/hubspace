var section_no = 3
var section_name = 'host';
var subsection_name = 'resources';
var subsection_no = 3;

var Resources = Class.create();
Resources.prototype = {
    initialize: function () {
        this.location = jq("#select_location").val();
        that = this;
        jq('#select_location').change(function () {
	            that.update_location();
        });
        jq('#resources_or_tariffs').change(function () {
            that.update_location();
        });
        this.manage_tariff_listeners();
    },
    load_add_resource: function (type) {
        var that = this;

        jq('#tariff_resources').load('/load_tab', {'object_type': 'Location', 'object_id': this.location, 'section': 'add' + type}, function () {
            that.listen_add();
        });
    },
    listen_add: function (response) {
        var that = this;
        navigation.addBoxExpanders();
        if (jq('#addTariffForm')) {
            jq('#submit_create_tariff').click(function () {
                that.add_tariff();
            });
            jq('#cancel_create_tariff').click(function () {
                that.cancel_add();
            });
        }
        if (jq('#addResourceForm')) {
            jq('#submit_create_resource').click(function () {
                that.add_resource();
            });
            jq('#cancel_create_resource').click(function () {
                that.cancel_add();
            });
        }
        if (jq('#addResourceForm')) {
            jq('#submit_create_resource_group').click(function () {
                that.add_resource_group();
            });
            jq('#cancel_create_resource_group').click(function () {
                that.cancel_add();
            });
        }

    },
    add_tariff: function () {
        var that = this;
        var params = jq('#addTariffForm').serializeArray();
        params[params.length] = {'name': 'place', 'value': this.location};

        var xhr = jq.post('/create_tariff', params, function (response) {
            that.complete_add('tariff', response, xhr);
        });
        return false;
    },
    add_resource: function () {
        var that = this;
        var params = jq('#addResourceForm').serializeArray();
        params[params.length] = {'name': 'place', 'value': this.location};

        var xhr = jq.post('/create_resource', params, function (response) {
            that.complete_add('resource', response, xhr);
        });
        return false;
    },
    add_resource_group: function () {
        var that = this;
        var params = jq('#addResourceGroupForm').serializeArray();
        params[params.length] = {'name': 'location', 'value': this.location};

        var xhr = jq.post('/create_resource_group', params, function (response) {
            that.complete_add('resource', response, xhr);
        });
        return false;
    },
    cancel_add: function () {
        jq('#tariff_resources').html("");
        return false;
    },
    complete_add: function (type, response, xhr) {
        if (xhr.getResponseHeader('X-JSON') === 'success') {
            jq('#resource_location').html(response);
            if (type === 'resource') {
                this.manage_resources_listeners();
            } else if (type === 'tariff') {
                this.manage_tariff_listeners();
            }
        } else {
            jq('#tariff_resources').html(response);
            this.listen_add(response);
        }

    },
    update_location: function () {
        var that = this;
        this.location = jq("#select_location").val();
        this.res_or_tariff = jq("#resources_or_tariffs").val();
        if (this.res_or_tariff === 'Tariffs') {
            this.callback = this.manage_tariff_listeners;
        } else if (this.res_or_tariff === 'Resources') {
            this.callback = this.manage_resources_listeners;
        }

        jq('#resource_location').load('/load_management_page', {'object_type': 'Location', 'object_id': this.location, 'res_or_tariff': this.res_or_tariff}, function () {
            that.callback();
        });
    },
    manage_tariff_listeners: function () {

        navigation.addBoxExpanders();
        var that = this;
        jq('table#tariff_management .managePrices').click(function () {
            that.manage_pricing(jq(this));
        });
        jq.each(jq('table#tariff_management div.resourceVAT'), function (i, ele) {
            that.edit_detail('vat', 'text_small', ele, '/save_resource_property', 'Resource', true);
        });
        var options = {action: function (ele) {
            that.default_tariff(ele);
        },
                       message: 'Are you sure you want to set this as the guest tariff? '
                       };
        jq('table#tariff_management .defaultTariff').confirm_action(options);
        jq('table#tariff_management a.activate').click(function () {
            that.toggle_activation(jq(this));
        });
        jq('#addTariff').click(function () {
            that.load_add_resource('Tariff');
        });
        jq.each(jq('table#tariff_management div.resourceName'), function (i, ele) {
            that.edit_detail('name', 'text_small', ele, '/save_resource_property', 'Resource');
        });
        jq.each(jq('table#tariff_management div.resourceDescription'), function (i, ele) {
            that.edit_detail('description', 'text_large', ele, '/save_resource_property', 'Resource');
        });
    },
    manage_resources_listeners: function () {
        var that = this;
        jq('#addResource').click(function () {
            that.load_add_resource('Resource');
        });
        jq('#addResourceGroup').click(function () {
            that.load_add_resource('ResourceGroup');
        });
        navigation.addBoxExpanders();
        jq.each(jq('table#resource_groups .resourceGroupName h1'), function (i, ele) {
            that.edit_detail('name', 'text_small', ele, '/save_resource_group_property', 'Resourcegroup');
        });
        jq.each(jq('table#resource_groups span.resourceGroupDesc'), function (i, ele) {
            that.edit_detail('description', 'text_large', ele, '/save_resource_group_property', 'Resourcegroup');
        });
        jq.each(jq('table#resource_groups div.resourceName span'), function (i, ele) {
            that.edit_detail('name', 'text_small', ele, '/save_resource_property', 'Resource');
        });
        jq.each(jq('table#resource_groups div.resourceDescription span'), function (i, ele) {
            that.edit_detail('description', 'text_large', ele, '/save_resource_property', 'Resource');
        });
        jq.each(jq('table#resource_groups div.resourceVAT span'), function (i, ele) {
            that.edit_detail('vat', 'text_small', ele, '/save_resource_property', 'Resource', true);
        });
        jq.each(jq('table#resource_groups div.resourceType span'), function (i, ele) {
            that.edit_detail('type', 'select', ele, '/save_resource_property', 'Resource');
        });
        jq('table#resource_groups a.activate').click(function () {
            that.toggle_activation(jq(this));
        });
        jq('.expand_res_group').one('click', function () {
            that.open_res_group(jq(this));
        });
        jq('.more_res_details').one('click', function () {
            that.load_extra(jq(this));
            return false;
        });
        that.set_delete_dialog();
        this.load_create_sortable();
    },
    default_tariff: function (tariff_cell) {
        var that = this;
        this.tariff_id = tariff_cell[0].id.split('_')[1];

        jq("#resource_location").load("/set_default_tariff", {'tariff_id': this.tariff_id}, function () {
            that.manage_tariff_listeners();
        });
    },
    manage_pricing: function (ele) {
        var that = this;
        this.tariff_id = ele[0].id.split('_')[1];

        jq('#tariff_resources').load("/load_tab", {'object_type': 'Resource', 'object_id': this.tariff_id, 'section': 'managePricing'}, function () {
            that.pricing_list_listeners();
        });
    },
    pricing_list_listeners: function () {
        var that = this;
        navigation.addBoxExpanders();
        jq('.schedule').click(function () {
            that.manage_schedule(jq(this));
        });

    },
    manage_schedule: function (ele) {
        var that = this;
        var ids = ele.attr('id').split('_');
        this.tariff = ids[2];
        this.resource = ids[1];

        jq('#schedule_area').load("/get_widget/pricingSchedule", {'object_type': 'Resource', 'object_id': this.resource, 'tariff': this.tariff}, function (response) {
            that.pricing_schedule_listeners(response);
        });
    },
    pricing_schedule_listeners: function () {
        navigation.addBoxExpanders();
        var that = this;
        jq('#add_pricing').click(function () {
            that.show_add_pricing();
        });
        jq('#submit_add_pricing').click(function () {
            that.add_pricing();
        });
        var options = {action: function (ele) {
            that.delete_pricing(ele);
        },
                       message: 'Are you sure you want to delete this pricing? '};
        jq('.delete_pricing').confirm_action(options);
    },
    delete_pricing: function (ele) {
        var that = this;
        var pricing = ele.attr('id').split('_')[1];

        jq('#schedule_area').load('/delete_pricing/' + pricing, function () {
            that.pricing_schedule_listeners();
        });
    },
    add_pricing: function () {
        var that = this;
        var params = jq('#add_pricing_form').serializeArray();
        params[params.length] = {'name': 'tariff', 'value': this.tariff};
        params[params.length] = {'name': 'resource', 'value': this.resource};

        var xhr = jq.post('/add_pricing', params, function (response) {
            that.append_pricing(response, xhr);
        });
    },
    append_pricing: function (response, xhr) {
        if (xhr.getResponseHeader('X-JSON') === 'success') {
            jq('#schedule_area').html(response);
        } else {
            jq("#add_pricing_divider").html(response);
        }
        this.pricing_schedule_listeners();

    },
    show_add_pricing: function () {
        jq('#add_pricing').css('display', 'none');
        jq('#add_pricing_form').css('display', 'inline');
        jq('#submit_add_pricing').css('display', 'inline');
    },
    edit_detail: function (prop_name, widget_type, element, url, object_type, load_locally) {
        var load_func = "";
        if (!load_locally) {
            load_func = ["/load_prop?prop_name=", prop_name, "&object_type=", object_type, "&id=", element.id.split('_')[1]].join("");
        }
        set_inplace_edit(element.id.split('_')[1], object_type, element.id, widget_type, url, load_func, null, null, prop_name);
    },
    load_extra: function (trigger) {
        var that = this;
        trigger.next().load('/load_tab', {object_id: trigger.attr('id').split('-')[1], object_type: 'Resource', section: 'moreResDetails'}, function () {
            that.view_res_details(trigger.next());
        });
    },
    view_res_details: function (popup) {
        var that = this;
        var trigger = popup.prev();
        trigger.click(function () {
            return false;
        });
        popup.find('a.close_popup').click(function () {
            popup.html("");
            trigger.unbind('click');
            trigger.one('click', function () {
                that.load_extra(jq(this));
                return false;
            });
        });
        this.requirements_listeners();
        this.suggestions_listeners();
        var img = jq('#extra_details div.imgwrap img');
        var img_trigger = img.prev();
        this.image = new Upload(img.attr('id').split('-')[1], 'Resource', 'resimage', img.get(0), img_trigger.get(0), {'edit_event':'click'});
    },
    set_delete_dialog: function () {
        var that = this;
        var options = {action: function (ele) {
            that.delete_res_group(ele);
        }};
        jq('.del_res_group a').confirm_action(options);
    },
    delete_res_group: function (ele) {
        that = this;
        var group_id = ele.attr('id').split('-')[1];
        jq('#resource_location').load('/delete_resource_group', {'group_id': group_id}, function () {
            that.manage_resources_listeners();
        });
        return false;
    },
    open_res_group: function (trigger) {
        var that = this;
        var children = trigger.children();
        children.slice(1, 2).html("Hide the resources in this group");
        children.slice(0, 1)[0].src = "/static/images/arrow_down_resourcetable.png";
        trigger.parent().parent().parent().nextAll().css('display', 'block');
        trigger.one('click', function () {
            that.close_res_group(trigger);
        });
    },
    close_res_group: function (trigger) {
        var that = this;
        var children = trigger.children();
        children.slice(1, 2).html("See the resources in this group");
        children.slice(0, 1)[0].src = "/static/images/arrow_right_resourcetable.png";
        trigger.parent().parent().parent().nextAll().css('display', 'none');
        trigger.one('click', function () {
            that.open_res_group(trigger);
        });
    },
    load_create_sortable: function () {
        var that = this;
        if (!compiled) {
            jq.getScript('/static/javascript/ui.core.js', function () {
                jq.getScript('/static/javascript/ui.sortable.js', function () {
                     jq.getScript('/static/javascript/jquery.tablednd.js', function () {
                         jq.getScript('/static/javascript/my.sortable.js', function () {
                             that.create_sortable();
                         });
                     });
                });
            });
        } else {
            jq.getScript('/static/javascript/admin' + jq('input#admin_js_no').val() + '.js', function () {
                that.create_sortable();
            });
        }
    },
    create_sortable: function () {
        create_sortables(this);
    },
    requirements_listeners: function () {
        var that = this;
        jq('table#resource_groups a.removeRequirement').click(function () {
            that.remove_suggestion(jq(this), 'requirement');
        });
        jq('table#resource_groups a.addRequirement').click(function () {
            that.add_suggestion(jq(this), 'requirement');
        });

    },
    suggestions_listeners: function () {
        var that = this;
        jq('table#resource_groups a.removeSuggestion').click(function () {
            that.remove_suggestion(jq(this), 'suggestion');
        });
        jq('table#resource_groups a.addSuggestion').click(function () {
            that.add_suggestion(jq(this), 'suggestion');
        });

    },
    toggle_activation: function (activator) {
        var that = this;
        var req = new Ajax.Updater(activator.parent()[0], '/toggle_resource_activate', {method: 'post', parameters: 'resourceid=' + activator[0].id.split('-')[1], onComplete: function () {
            that.new_activator(activator[0].id);
        }});
    },
    new_activator: function (activator_id) {
        var that = this;
        jq('#' + activator_id).click(function () {
            that.toggle_activation(jq(this));
        });

    },
    add_suggestion: function (ele, type) {
        var that = this;
        var resourceid = ele.attr('id').split('-')[1];
        var form_field = jq('#choose' + type + '-' + resourceid);
        var suggestedid = form_field.val();
        form_field.find('option[value=' + suggestedid + ']').remove();

        jq.post('/add_' + type + '/' + resourceid + '/' + suggestedid, function (response) {
            jq(response).appendTo(ele.parent().prev());
            ele.parent().prev().find('a').click(function () {
                that.remove_suggestion(jq(this), type);
            });

        });
    },
    remove_suggestion: function (ele, type) {
        var that = this;
        var ids = ele.attr('id').split('-');
        var resourceid = ids[1];
        var suggestedid = ids[2];
        jq('#choose' + type + '-' + resourceid).append(jq('<option value=' + suggestedid + '>' + ele.prev().text() + '</option>'));

        jq.post('/remove_' + type + '/' + resourceid + '/' + suggestedid, function () {
            ele.parent().remove();
            ele.unbind();
        });
    }
};


