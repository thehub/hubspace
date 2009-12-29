var partial =  function () {
        var func = arguments[0];
        var ori_args = [];
        for (var i = 1; i < arguments.length; i++) {
            ori_args.push(arguments[i]);
        }
        return function () {
            var new_args = [];
            for (var i = 0; i < ori_args.length; i++) {
                new_args.push(ori_args[i]);
            }
            for (var j = 0; j < arguments.length; j++) {
                new_args.push(arguments[j]);
            }
            return func.apply(this, new_args);
        };
};

var compiled = false;

//////////location tariff details//////////////
var edit_tariffs = function () {
    var selected = jq(this);
    var value = selected.val();
    selected = selected.attr('id').split('.');
    year = Number(selected[1]);
    month = Number(selected[2]);
    jq.each(jq('.tariffEdit'), function (i, ele) {
        var tariff_date = jq(ele).attr('id').split('.');
        if (year < Number(tariff_date[1]) || (year === Number(tariff_date[1]) && month < Number(tariff_date[2]))) {
            jq(ele).val(value);
        }
    });
};
var set_tariff_booking_edit = function () {
    jq('.tariffEdit').change(edit_tariffs);
    jq('#tariff_location_select-' + navigation.current_profile_id()).hide();
};
var show_tariff_switch = function (element) {
    jq('#tariff_location_select-' + navigation.current_profile_id()).show();
};
var tariff_location = function () {
    var loc = jq(this).val();
    var user = navigation.current_profile_id();
    var params = {object_id: user, object_type: 'User', location: loc, action: 'tariff_loc'};

    jq('#tariff_booking_area-' + user).load('/get_widget/mainProfile', params, select_tariff_location);
};
var select_tariff_location = function () {
    var user = navigation.current_profile_id();
    jq('#tariff_location_select-' + user).change(tariff_location);
    set_inplace_edit(user, 'User', 'tariffHistory-' + user, 'tariffHistoryEdit', null, null, {'location': jq("#tariff_location_select-" + user).val()}, show_tariff_switch, null, set_tariff_booking_edit, show_tariff_switch);

};

var download_invoices = function (evt) {
    var list_invoices = Event.element(evt).id.split('-');
    var loc_id = list_invoices[1];
    var loc_name = list_invoices[2];
    var start = jq("#start_invoice_list-" + loc_id).val();
    var end = jq("#end_invoice_list-" + loc_id).val();
    window.location = '/invoice_list/' + loc_id + '/' + start + '/' + end + '/invoice_list_' + loc_name + '.csv';
};
var gen_reports = function (evt) {
    var list_invoices = Event.element(evt).id.split('-');
    var loc_id = list_invoices[1];
    var start = jq("#start_rusage").val();
    var end = jq("#end_rusage").val();
    var r_type = jq("#r_type").children("[@selected]").val();
    var r_name = jq("#r_name").children("[@selected]").val();
    var user_id = jq("#user_id").children("[@selected]").val();
    var grpby = jq("input[@name='grpby']:checked").val();
    var g_type = jq("input[@name='g_type']:checked").val();
    window.location = '/get_usage_csv/' + loc_id + '/' + r_type + '/' + r_name + '/' + user_id + '/' + start + '/' + end + '/' + grpby + '/' + g_type + '/report.csv';
};

var show_graph = function (response) {
    jq("#plot_area").html(response);
};

var plot_reports = function (evt) {
    var list_invoices = Event.element(evt).id.split('-');
    var loc_id = list_invoices[1];
    var start = jq("#start_rusage").val();
    var end = jq("#end_rusage").val();
    var r_type = jq("#r_type").children("[@selected]").val();
    var r_name = jq("#r_name").children("[@selected]").val();
    var user_id = jq("#user_id").children("[@selected]").val();
    var grpby = jq("input[@name='grpby']:checked").val();
    var g_type = jq("input[@name='g_type']:checked").val();
    var url = '/get_usage_graph/';
    var params = {'location_id': loc_id, 'r_type': r_type, 'r_name': r_name, 'user_id': user_id, 'start': start, 'end': end, 'grpby': grpby, 'g_type': g_type};
    jq('#plot_area').load(url, params, show_graph);
};

var plot_report = function (evt) {
    var values = Event.element(evt).id.split('-');
    var loc_id = values[1];
    var r_type = values[2];
    var r_name = values[3];
    var user_id = values[4];
    var period = values[5];
    var g_type = values[6];
    var format = values[7];
    var url = '/get_quick_usage/';
    var params = {'loc_id': loc_id, 'r_type': r_type, 'r_name': r_name, 'user_id': user_id, 'period': period, 'g_type': g_type, 'format': format};
    jq('#plot_area').load(url, params, show_graph);
};

var delete_report = function (evt) {
    var id = Event.element(evt).id;
    var req = new Ajax.Request('/deleteUsageReport', {parameters: "g_id=" + id, method: 'post', onComplete: this.remove(this)});
};

var save_report = function (evt) {
    var id = Event.element(evt).id;
    var rtype, start, end, grpby, r_name, r_type, user_id = id.split('-');
    var url = [rtype, start, end, grpby, r_name, r_type, user_id].join("/");
    var req = new Ajax.Request("/saveUsageRport/" + url, {onComplete: this.remove(this)});
};

var plot_lreports = function (evt) {
    var list_invoices = Event.element(evt).id.split('-');
    var loc_id = list_invoices[1];
    var start = jq("#start_rusage").val();
    var end = jq("#end_rusage").val();
    var r_type = jq("#r_type").children("[@selected]").val();
    var r_name = jq("#r_name").children("[@selected]").val();
    var user_id = jq("#user_id").children("[@selected]").val();
    var grpby = jq("input[@name='grpby']:checked").val();
    var g_type = jq("input[@name='g_type']:checked").val();
    var url = '/get_usage_graph/' + loc_id + '/' + r_type + '/' + r_name + '/' + user_id + '/' + start + '/' + end + '/' + grpby + '/' + g_type + '/large';
    window.open(url);
};

/////////////////////Autocomplete//////////////////////
var add_alias_box = function () {
    jq("#add_more_alias").before("<input name='new_alias' type='text' class='text'/>");
};

var editMemberProfileListeners = function () {
    jq("#biz_type").autocomplete("/complete_biz_type", {width: 260, selectFirst: true, matchSubset: false});
    jq("#add_more_alias").click(add_alias_box);
};


//////////////////////Resources////////////////////////
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

//Todos //////////////////////////

var Todos = Class.create();
Todos.prototype = {
    refresh: function () {
        var req = new Ajax.Updater($("hostContent"), '/load_tab', {method: 'get', parameters: 'object_type=User&object_id=' +  this.user_id  +  '&section=host', onComplete: new_todos});
    },
    set_inplace: function (evt) {
        $$('div#host-todosContent a.edit').each(this.listen_set_inplace.bind(this));
        $$('div#todo_content_urgent a.edit_urgent').each(this.listen_set_inplace.bind(this));
        $$('div#host-todosContent a.followup').each(this.listen_set_inplace.bind(this));
        $$('div#todo_content_urgent a.followup_urgent').each(this.listen_set_inplace.bind(this));

    },
    listen_set_inplace: function (element) {
        set_inplace_edit(element.parentNode.className, "Todo", element.parentNode.id, 'todoEdit', null, null, {"action": "edit"}, this.refresh.bind(this), null, this.set_date.bind(this));
    },
    set_date: function (element) {
        var id = element.id.split('Todo')[0];
        var date_input = jq('#due_' + id);
        var date_trigger = jq('#show_date_' + id);
        set_inplace_cal(date_trigger, date_input);
    },
    listen_todo_add: function (element) {
        Event.stopObserving(element, 'click', this.todo_add);
        Event.observe(element, 'click', this.todo_add);
    },
    listen_invoice_create: function (element) {
        Event.stopObserving(element, 'click', this.create_invoice);
        Event.observe(element, 'click', this.create_invoice);
    },
    listen_follow_up: function (element) {
        Event.stopObserving(element, 'click', this.to_user);
        Event.observe(element, 'click', this.to_user);
    },
    listen_remind: function (element) {
        Event.stopObserving(element, 'click', this.remind);
        Event.observe(element, 'click', this.remind);
    },
    listen_ignore:  function (element) {
        Event.stopObserving(element, 'click', this.ignorer);
        Event.observe(element, 'click', this.ignorer);
    },
    listen_show_closed:  function (element) {
        Event.stopObserving(element, 'click', this.show_closed);
        Event.observe(element, 'click', this.show_closed);
    },
    initialize: function () {
        this.nav = navigation;
        this.nav.addBoxExpanders();
        //this.nav.set_tab_switch();
        this.user_id = Number(navigation.current_user_id());
        this.create_invoice = this.create_invoice.bindAsEventListener(this);
        this.set_inplace();
        this.todo_add = this.todo_add.bindAsEventListener(this);
        var add_todo_bar = jq('#addTodoBar');
        this.todo_add_bar = this.todo_add_bar.bindAsEventListener(this);
        add_todo_bar.click(this.todo_add_bar);
        this.show_closed = this.show_closed.bindAsEventListener(this);
        this.ignorer = this.ignorer.bindAsEventListener(this);
        this.remind = this.remind.bindAsEventListener(this);
        this.to_user = this.to_user.bindAsEventListener(this);
        $$('div#host-todosContent a.addTodo').each(this.listen_todo_add.bind(this));
        $$('div#invoices_create a.invoice').each(this.listen_invoice_create.bind(this));
        $$('div#host-todosContent a.followup').each(this.listen_follow_up.bind(this));
        $$('div#host-todosContent a.followup_urgent').each(this.listen_follow_up.bind(this));
        $$('div#invoices_unsent a.send').each(this.listen_invoice_create.bind(this));
        $$('div#payment_reminders a.remind').each(this.listen_remind.bind(this)); //why no reminders after upload
        $$('div#payment_reminders a.ignore').each(this.listen_ignore.bind(this));
        $$('div#host-todosContent a.showClosed').each(this.listen_show_closed.bind(this));
        var that = this;
        var options = {action: function (ele) {
            that.submit_delete_bar(ele);
        },
                       message: 'Are you sure you want to delete this todo list? '};
        jq('div#host-todosContent a.deleteBar').confirm_action(options);
        Event.observe($("choose_host"), 'change', this.change_user);
    },
    submit_delete_bar: function (ele) {
        var todo_parent = jq(ele).parent().parent();
        var bar_id = todo_parent.attr('id').split('-')[1];

        var req = new Ajax.Request('/delete_todo_bar', {parameters: "bar_id=" + bar_id, method: 'post', onComplete: this.refresh.bind(this)});
    },
    ignorer: function (evt) {
        var element = Event.element(evt);
        Event.stopObserving(element, 'click', this.ignorer);
        var link_id = element.id.split('-');
        var user_id = link_id[1];

        var req = new Ajax.Request('/ignore_remind', {method: 'post', parameters: "user_id=" + user_id, onComplete: this.refresh.bind(this)});
    },
    create_invoice: function (evt) {
        this.nav.load_user(jq(Event.element(evt)), 2);
    },
    to_user: function (evt) {
        this.nav.load_user(jq(Event.element(evt)), 1);
    },
    remind: function (evt) {
        var element = Event.element(evt);
        Event.stopObserving(element, 'click', this.remind);
        var link_id = element.id.split('-');
        var user_id = link_id[1];
        var action = link_id[0];

        var req = new Ajax.Request('/get_widget/sendReminder', {method: 'get', parameters: 'object_id=' + user_id  + '&object_type=User', onComplete: partial(this.set_submit_remind.bind(this), user_id, action)});
    },
    set_submit_remind: function (user_id, action, response) {
        var mail = document.createElement('div');
        mail.id = "send_reminderarea_" + user_id;
        Element.update(mail, response.responseText);
        $('description_' + action  + '_' + user_id).appendChild(mail);
        Event.observe('submit_reminder_mail', 'click', partial(this.send_reminder.bindAsEventListener(this), mail.id));
        Event.observe('cancel_reminder_mail', 'click', partial(this.cancel_reminder.bindAsEventListener(this), mail.id));

    },
    send_reminder: function (mail_id, evt) {
        var id = mail_id.split('_')[2];
        var mail_form = "id=" + id  + '&' + Form.serialize('send_reminder_' + id);

        var req = new Ajax.Request('/send_reminder', {parameters: mail_form, onComplete: partial(this.finish_send_reminder.bind(this), mail_id)});
    },
    finish_send_reminder: function (mail_id, response) {
        if (response.getResponseHeader('X-JSON') === 'success') {
            this.refresh();
        } else {
            Element.update($(mail_id), response.responseText);
            Event.observe('submit_reminder_mail', 'click', partial(this.send_reminder.bindAsEventListener(this), mail_id));
            Event.observe('cancel_reminder_mail', 'click', partial(this.cancel_reminder.bindAsEventListener(this), mail_id));

        }
    },
    cancel_reminder: function (mail_id, evt) {
        Element.remove(mail_id);
        var element = $('remind-' + mail_id.split('_')[2]);
        Event.observe(element, 'click', this.remind);
    },
    change_user: function (evt) {
        this.user_id = Number(Event.element(evt).value);
        this.refresh();
    },
    todo_add: function (evt) {
        var add_link = Event.element(evt);
        Event.stopObserving(add_link, 'click', this.todo_add);
        var parent = add_link.parentNode.parentNode;
        var form = new Todo_form(parent, add_link, this);

        var req = new Ajax.Request('/load_tab', {method: 'get', parameters: 'object_type=Todo&object_id=' + parent.id.split('-')[1] + '&section=addTodo', onComplete: partial(this.todo_add_form.bind(this), form)});
    },
    todo_add_form: function (form, response) {
        form.create_form(response);
        set_inplace_cal(jq("#show_date"), jq("#due"));
    },
    todo_add_bar: function (evt) {
        var add_link = Event.element(evt);
        Event.stopObserving(add_link, 'click', this.todo_add_bar);
        var parent = "";
        var form = new Todo_bar(this.user, add_link, this);

        var req = new Ajax.Request('/load_tab', {method: 'get', parameters: 'object_type=User&object_id=' +  this.user_id +  '&section=addTodoBar', onComplete: form.create_form.bind(form)});
    },
    show_closed: function (evt) {
        var show_closed_link = Event.element(evt);
        var todo_parent = Event.element(evt).parentNode.parentNode;
        var todo_parent_id = todo_parent.id.split('-')[1];
        var hideClosed = document.createElement('a');
        Element.update(hideClosed, "Hide Closed");
        hideClosed.className = 'show showClosed';
        hideClosed.id = 'showClosed';
        show_closed_link.parentNode.insertBefore(hideClosed, show_closed_link);
        Element.remove(show_closed_link);
        Event.observe(hideClosed, 'click', partial(this.hide_closed.bind(this), show_closed_link));

        var req = new Ajax.Updater($('todo_content_' + todo_parent.id), '/toggle_closed_todos', {evalScripts: true, method: 'get', parameters: "show=1&bar_id=" +  todo_parent_id, onComplete: this.set_inplace.bind(this)});
    },
    hide_closed: function (show_closed_link, evt) {
        var hide_closed_link = Event.element(evt);
        var todo_parent = hide_closed_link.parentNode.parentNode;
        var todo_parent_id = todo_parent.id.split('-')[1];
        hide_closed_link.parentNode.insertBefore(show_closed_link, hide_closed_link);
        Element.remove(hide_closed_link);

        var req = new Ajax.Updater($('todo_content_' + todo_parent.id), '/toggle_closed_todos', {evalScripts: true, method: 'get', parameters: "show=0&bar_id=" +  todo_parent_id, onComplete: this.set_inplace.bind(this)});
    }
};

var Todo_bar = Class.create();
Todo_bar.prototype = {
    initialize: function (user, add_link, todos) {
        this.create_todo =  this.create_todo.bindAsEventListener(this);
        this.cancel_todo = this.cancel_todo.bindAsEventListener(this);
        this.user = user;
        this.add_link = add_link;
        this.add_list = $("add_list");
        this.todos = todos;
    },
    create_form: function (response) {
        this.add_list_form = document.createElement("div");
        Element.update(this.add_list_form,  response.responseText);
        this.add_list.appendChild(this.add_list_form);
        Event.observe($('submit_todo_bar'), 'click', this.create_todo);
        Event.observe($('cancel_todo_bar'), 'click', this.cancel_todo);
        navigation.addBoxExpanders();
        Element.hide(this.add_link);

    },
    create_todo: function (evt) {
        var form_values =  Form.serialize($('create_todo_bar'));

        var req = new Ajax.Request('/create_todo', {method: 'post', parameters: form_values, onComplete: this.prependTodo.bind(this)});
    },
    cancel_todo: function (evt) {
        Element.remove(this.add_list_form);
        Event.observe(this.add_link, 'click', this.todos.todo_add_bar);
        Element.show(this.add_link);
    },
    prependTodo: function (response) {
        if (response.getResponseHeader('X-JSON') === 'success') {
            Element.update($("hostContent"), response.responseText);
            var todos = new Todos();
        } else {
            Element.update(this.add_list_form, response.responseText);
            Event.observe($('submit_todo_bar'), 'click', this.create_todo);
            Event.observe($('cancel_todo_bar'), 'click', this.cancel_todo);
        }

    }
};

var new_todos = function () {
    var todos = new Todos();

};

var Todo_form = Class.create();
Todo_form.prototype = {
    initialize: function (parent, add_link, todos) {
        this.create_todo =  this.create_todo.bindAsEventListener(this);
        this.cancel_todo = this.cancel_todo.bindAsEventListener(this);
        this.parent = parent;
        this.todobar_id = this.parent.id.split('-')[1];
        this.add_link = add_link;
        this.todos = todos;
    },
    create_form: function (response) {
        this.todo_form = document.createElement('li');
        Element.update(this.todo_form, response.responseText);
        this.todo_content = this.parent.getElementsByTagName('UL')[0];
        this.todo_content.insertBefore(this.todo_form, this.todo_content.firstChild);
        Event.observe($('submit_todo_' + this.todobar_id), 'click', this.create_todo);
        Event.observe($('cancel_todo_' + this.todobar_id), 'click', this.cancel_todo);

    },
    create_todo: function (evt) {
        var form_values =  Form.serialize($('create_todo_' + this.todobar_id));

        var req = new Ajax.Request('/create_todo', {method: 'post', parameters: form_values, onComplete: this.prependTodo.bind(this)});
    },
    cancel_todo: function (evt) {
        Element.remove(this.todo_form);
        Event.observe(this.add_link, 'click', this.todos.todo_add);
    },
    prependTodo: function (response) {
        if (response.getResponseHeader('X-JSON') === 'success') {
            Element.update($("hostContent"), response.responseText);
            var todos = new Todos();
        } else {
            Element.update(this.todo_form, response.responseText);
            Event.observe($('submit_todo_' + this.todobar_id), 'click', this.create_todo);
            Event.observe($('cancel_todo_' + this.todobar_id), 'click', this.cancel_todo);
        }

    }
};

//Notes //////////////////////////
var Notes = Class.create();
Notes.prototype = {
    initialize: function (user_id, type) {
        this.type = type;
        this.user_id = user_id;
        this.add_note_form = jq("#add_" + type + "_" + this.user_id);
        var that = this;
        this.add_note_form.one('click', function () {
            that.add_note();
        });
        this.refresh();
    },
    refresh: function () {
        var that = this;
        this.notes = [];
        jq.each(jq("div#user_" + this.type + "s-" + this.user_id + " div." + this.type), function (i, ele) {
            that.existing(ele);
        });

    },
    existing: function (element) {
        var i = this.notes.length;
        var note_id = element.id.split(this.type.charAt(0).toUpperCase())[0];
        this.upper_type = this.type.charAt(0).toUpperCase().concat(this.type.substring(1));
        this.notes[i] = new Note(this, note_id);
    },
    add_note: function () {
        var that = this;

        jq.get('/load_tab', {object_type: 'User', object_id: this.user_id, section: this.type + 's'}, function (response) {
            that.new_note_form(response);
        });
    },
    new_note_form: function (response) {
        var that = this;
        var note_form_html = '<div id="note_form_' + this.user_id + '">' + response + '</div>';
        var test = jq('#' + this.type + 's_area_' + this.user_id).prepend(note_form_html);
        jq('#submit_create_' + this.type).one('click', function () {
            that.create_note();
        });
        jq('#' + 'cancel_create_' + this.type).one('click', function () {
            that.cancel_note();
        });

    },
    create_note: function () {
        var that = this;
        var form_values =  jq('#create_' + this.type).serializeArray();

        jq.post('/create_' + this.type, form_values, function (response) {
            that.updateNote(response);
        });
    },
    updateNote: function (response) {
        var that = this;
        var notes_area = jq('#' + this.type + 's_area_' + this.user_id);
        notes_area.html(response);
        this.add_note_form.one('click', function () {
            that.add_note(jq(this));
        });
        this.refresh();
    },
    cancel_note: function () {
        var that = this;
        jq("#note_form_" + this.user_id).remove();
        this.add_note_form.one('click', function () {
            that.add_note();
        });
    }
};

var Note = Class.create();
Note.prototype = {
    initialize: function (notes, note_id) {
        this.notes = notes;
        this.note_id = note_id;
        var del = $(this.note_id + this.notes.upper_type + 'Delete');
        this.delete_note = this.delete_note.bind(this);
        if (del) {
            Event.observe(del, 'click', this.delete_note);
        }
        this.view_action = this.view_action.bind(this);
        this.show_add_action = this.show_add_action.bind(this);
        this.add_action = this.add_action.bind(this);
        this.renew();
        this.set_inplace();
    },
    renew: function () {
        this.show_note_action();
        this.view_note_action();
    },
    set_inplace: function () {
        set_inplace_edit(this.note_id, 'Note', this.note_id + this.notes.upper_type, null, null, null, null, this.renew.bind(this));
        set_inplace_cal(jq('#show_due_' + this.note_id), jq('#due_' + this.note_id));
    },
    show_note_action: function () {
        var noteAddAction = $(this.note_id + this.notes.upper_type + "AddAction");
        if (noteAddAction) {
            Event.observe(noteAddAction, 'click', this.show_add_action, false);
        }
    },
    view_note_action: function () {
        var viewNoteAction = $(this.note_id + this.notes.upper_type + "Action");
        if (viewNoteAction) {
            Event.observe(viewNoteAction, 'click', this.view_action, false);
        }
    },
    view_action: function (evt) {
        var action_disp = $(this.note_id + this.notes.type + "ActionDisplay");
        if (action_disp.style.display === 'none') {
            action_disp.style.display = "block";
        } else {
            action_disp.style.display = "none";
        }
        Event.stop(evt);
    },
    show_add_action: function (evt) {
        var action_disp = $(this.note_id + this.notes.type + "ActionDisplay");
        if (action_disp.style.display === 'none') {
            action_disp.style.display = "block";
        } else {
            action_disp.style.display = "none";
        }
        Event.stop(evt);
        Event.observe($(this.note_id + this.notes.type + "SubmitAction"), 'click', this.add_action, false);
    },
    add_action: function (evt) {
        Event.stop(evt);
        var form = $(this.note_id + this.notes.type + "createAction");
        var params = Form.serialize(form);
        params += "&note=" + this.note_id;
        var req = new Ajax.Updater($(this.note_id + this.notes.upper_type), "/add_action", {method: 'get', parameters: params, onComplete: this.view_note_action.bind(this)});
    },
    delete_note: function (evt) {

        var req = new Ajax.Request('/delete_' + this.notes.type + '/', {parameters: "id=" + this.note_id, method: 'post', onComplete: nd()});
        Element.remove($(this.note_id + this.notes.upper_type).parentNode);
    }
};
///////////////////////MEMBER LIST/////////////////////////////
var set_members_listeners = function () {
    jq('ul#membersContent a.load_user').click(function () {
        navigation.load_user(jq(this));
        return false;
    });
    jq('ul#membersContent a.box').click(function () {
        toggleDetails(Number(jq(this).attr('id').split('-')[1]));
        return false;
    });
};
var search_results_listeners = function () {
    jq('ul#results a.user_link').click(function () {
        navigation.load_user(jq(this));
        return false;
    });
};
var append_members = function (response) {
    jq(response).appendTo('#membersContent');
    set_members_listeners();
    var scroll = new ScrollObj(10, 12, 322, "track", "up", "down", "drag", "memberList", "membersContent");

};

//////////////////////////SEARCH//////////////
var Search = Class.create();
Search.prototype = {
    initialize: function () {
        var that = this;
        this.member_search_element = jq('#member_search');
        this.member_search_element.focus(function () {
            that.remove_default_text();
        });
        this.member_search_element.delayedObserver(1, function () {
            that.filter_members();
        }, {event: 'keyup'});
        jq('#search_locality').change(function () {
            that.filter_members();
        });
        jq('#search_type .radio_button').click(function () {
            that.switch_search_type();
        });
        this.start = 0;
        this.end = 80;
        this.value = "";
        this.loc = 0;
        this.search_type = "member_search";
        this.incremental_load();
        this.search_type_map = {'member_search': this.update_members,
                                'fulltext_member_search': this.display_search,
                                'rfid_member_search': this.load_rfid_member};
    },
    filter_members: function (val) {
        this.loc = jq('#search_locality').val();
        this.search_type = jq('#search_type .radio_button:checked').val();
        this.value = jq('#member_search').val();
        this.update = this.search_type_map[this.search_type];
        var that = this;
        jq('#search_type label').each(function () {
           if(that.value === jq(this).html()) {
               that.value = '' ;
           }
        });
        this.start = 0;
        this.end = 80;
        this.get_members();
    },
    get_members: function () {
        var that = this;
        var search_type = this.search_type;
        jq.ajax({type: "GET",
                 url: "/filter_members",
                 success: function (response) {
            if (search_type == that.search_type) {
                that.update(response, that.value);
            }
        },
                 data: {text_filter: this.value, location: this.loc, type: this.search_type, start: this.start, end: this.end}
        });
    },
    incremental_load: function () {
        var that = this;
        jq('#down').mousedown(function () {
            that.start_timed_check();
        }).mouseup(function () {
            that.stop_timed_check();
        });
    },
    start_timed_check: function () {
        /*every x seconds while the mouse button is held down, do a timed_event which checks the amount of names loaded in and compares to the top offset of the unordered list.
           if we are more than 50 items from the top call get_members and append */
        var that = this;
        jq('body').everyTime("1s", "load_users", function () {
            that.check_userlist();
        });
    },
    check_userlist: function () {
        var offset = parseInt(jq('#membersContent').css("top"), 10);
        if (this.end - 60 < Math.abs(offset / 20)) {
            this.start = this.end;
            this.end += 80;
            this.update = append_members;
            this.get_members();
        }
    },
    stop_timed_check: function () {
        jq('body').stopTime("load_users");
    },
    switch_search_type: function () {
        if (!this.reset_default_text()) {
            this.filter_members();
        }
        if (this.search_type === 'rfid_member_search') {
            jq('#member_search').focus();
        }
    },
    reset_default_text: function () {
        this.search_type = jq('#search_type .radio_button:checked').val();
        this.search_label = jq('#search_type .radio_button:checked').next().html();
        this.value = jq('#member_search').val();
        var that = this;
        jq('#search_type label').each(function () {
           if (that.value === jq(this).html()) {
               jq('#member_search').val(that.search_label);
               return true;
           }
        });
        if (this.value === '') {
           jq('#member_search').val(this.search_label);
           return true;
        }
        return false;
    },
    remove_default_text: function () {
        jq('#search_type label').each(function () {
            if (jq(this).html() == jq('#member_search').val()) {
                jq('#member_search').val('');
            }
        });
    },
    update_members: function (response, value) {
        if (value && value !== jq('#member_search').val() || this.search_type !== 'member_search') {
            return;
        }
        var content = jq('#membersContent');
        content[0].setTop(0);
        content.html(response);
        set_members_listeners();
        var scroll = new ScrollObj(10, 12, 322, "track", "up", "down", "drag", "memberList", "membersContent");
    },
    display_search: function (response, value) {
        if (!value || this.search_type !== 'fulltext_member_search') {
            return;
        }
        navigation.switch_tab(0, 3);
        jq('#network-fulltextsearchContent').html(response);
        navigation.addBoxExpanders();
        search_results_listeners();
    },
    load_rfid_member: function (data, value) {
        if (!value || this.search_type !== 'rfid_member_search') {
            return;
        }
        var id = parseInt(data, 10);
        if (id) {
            navigation.load_user_from_id(id);
        } else {
            jq('#network-mainProfileContent').html(data);
            navigation.switch_tab(0, 1);
        }
        jq("#member_search").focus();
    }
};

//////////////////////////SEARCH INVOICES//////////////
var search_invoices = function (evt) {
    var form = jq('#invoices_search_form').serializeArray();

    jq('#search_results').load('/uninvoiced_users', form, search_results_listeners);
    return false;
};
var get_usage_summary = function (evt) {
    var form = jq('#usage_summary').serializeArray();
    var params = jQuery.param(form);
    window.open('/usage_report.csv?' + params);
};
var get_users_csv = function (evt) {
    var form = jq('#users_export').serializeArray();
    var params = jQuery.param(form);
    window.open('/export_users.csv?' + params);
};
var get_report = function (evt) {
    var form = jq('#report_conf').serializeArray();
    var params = jQuery.param(form);
    window.open('/generate_report?' + params);
};
var show_users_grid = function (evt) {
    var form = jq('#users_export').serializeArray();

    jq('#users_grid').remove();
    jq('#flex1').empty();
    jq('#flex1').load('/users_grid', form);
    return false;
};
var init_search_invoices = function () {
    set_inplace_cal(jq('#display_search_from_date'), jq('#search_from_date'));
};
////////////////TABS & NAVIGATION///////////////////////
var Tabs = function () {
    var current_user_id = jq('#current_user_id').attr('class');
    var current_profile_id = current_user_id;
    var sections = ['network', 'profile', 'space', 'host'];
    var subsections = {'network': ['addMember', 'mainProfile', 'billing', 'fulltextsearch'],
                       'profile': ['mainProfile', 'billing'],
                       'space': ['booking'],
                       'host': ['todos', 'invoicing', 'openTimes', 'admin', 'resources', 'managementdata']};
    var subsection_defaults = {'network': 1,
                               'profile': 0,
                               'host': 0,
                               'space': 0};
    var data_expandors = {'network': {1: {}, 2: {}, 3: {}},
                          'profile': {0: {}, 1: {}},
                          'host': {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5:{}},
                          'space': {0: {}}};
    var make_section_switch = false;
    var edited_subsection = 0;
    if (jq("#profileContent").attr("class") === 'pane_selected') {
        var section_name = "profile";
        var section_no = 1;
    } else if (jq("#networkContent").attr("class") === 'pane_selected') {
        var section_name = "network";
        var section_no = 0;
    }
    var current_subsections = subsections[section_name];
    var subsection_no = subsection_defaults[section_name];
    var subsection_name = current_subsections[subsection_no];

    var clear_html = function () {
        jq(this).html('');
        cleared = 1;
    };
    var load_section = function () {
        cleared = 0;
        change_section(jq(this).attr('id'));
        jq('#' + section_name + 'Content').load('/load_tab', {'section': section_name, 'object_id': current_user_id, 'object_type': 'User'}, switch_section);
    };
    var change_section = function (new_section_no, new_subsection_no) {
        section_no = new_section_no;
        section_name = sections[section_no];
        current_subsections = subsections[section_name];
        if (!new_subsection_no) {
            subsection_no = subsection_defaults[section_name];
        }
        subsection_name = current_subsections[subsection_no];
    };
    var switch_section = function (response) {
        jq(sections).each(function (i, ele) {
            if (i == section_no) {
                jq('#' + sections[i] + 'Content').show();
                jq('#' + sections[i] + 'But').attr('class', 'selected');
            } else {
                jq('#' + sections[i] + 'Content').hide();
                jq('#' + sections[i] + 'But').attr('class', 'deselected');
            }
        });
        set_tab_events();
    };
    var load_subsection = function (new_subsection) {
        subsection_no = new_subsection;
        subsection_name = current_subsections[subsection_no];
        var tabContent = jq('#' + section_name + "-" + subsection_name + 'Content');
        if (subsection_name === 'invoicing' || subsection_name === 'todos') {
            init_search_invoices();
        }
        if (subsection_name === 'fulltextsearch' || subsection_name === 'invoicing') {
            switch_subsection();
        } else {
            jq('#' + section_name + '-' + subsection_name + 'Content').html("");
            var params =  {'section': subsection_name, 'object_id': current_profile_id, 'object_type': 'User'};
            tabContent.load('/load_tab', params, switch_subsection);
        }
    };
    var switch_subsection = function (response) {
        if (make_section_switch !== false) {
            change_section(section_no, subsection_no);
            switch_section();
            make_section_switch = false;
        } else {
            set_tab_events();
        }
        jq(current_subsections).each(function (i, ele) {
            if (i  ==  subsection_no) {
                jq('#' + section_name + "-" + subsection_name + 'Content').css('display', 'block');
                jq('#' + section_name + "-" + subsection_no).parent().attr('class', 'selected');
            } else {
                jq('#' + section_name + "-" + current_subsections[i] + 'Content').css('display', 'none');
                jq('#' + section_name + "-" + i).parent().attr('class', '');
            }
        });
    };
    var set_tab_events = function () {
        if (section_name === "profile") {
            current_profile_id = current_user_id;
        }
        jq("div#" + section_name + "Content a.subsection").unbind('click').click(function () {
            load_subsection(jq(this).attr('id').split('-')[1]);
        });
        o.tab_specifics();
    };
    var add_member = function () {
        var xhr = jq.post('/create_user', jq('#add_member').serializeArray(), function (response) {
            goto_new_member(response, xhr);
        }); //necessary extra function nesting?
    };
    var goto_new_member = function (response, xhr) {
        if (xhr.getResponseHeader('X-JSON') === 'success') {
            current_profile_id = response;
            load_subsection(1);
        } else {
            jq('#network-addMemberContent').html(response);
            jq("#submit_add_member").click(function () {
                add_member();
            });
        }

    };
    var load_admin = function () {
        jq.get('/load_tab', {'object_type':'Location', 'object_id':jq(this).val(), 'section':'locationAdmin'}, complete_load_admin);
    };
    var complete_load_admin = function (data) {
        jq('#resource_location').html(data);
        admin_listeners();
    };
    var admin_listeners = function () {
        jq('.listInvoices').click(download_invoices);
        jq('.genReports').click(gen_reports);
        jq('.plotReports').click(plot_reports);
        jq('.plotLReports').click(plot_lreports);
        jq('.plotReport').click(plot_report);
        jq('.deleteReport').click(delete_report);
        jq('.deleteReport').confirm();
        jq('.saveReport').click(save_report);
        o.addBoxExpanders();
        var loc = jq('#admin_location').attr('class');
        set_inplace_edit(loc, 'Location', 'locationProfile-' + loc, 'locationProfileEdit');
	image_upload('upload_invlogo', 'invlogo_image', 'invlogo');
        image_upload('upload_homelogo', 'homelogo_image', 'homelogo');
	image_upload('upload_logo', 'logo_image', 'logo');
    };

    var image_upload = function(trigger_id, img_id, attr_name) {
        var trigger = jq('#' + trigger_id);
        var location_id = jq('#admin_location').attr('class');
        var img = jq('#' + img_id + location_id).get(0);
        if (trigger && img) {
            delete uploaded_image;
            uploaded_image = new Upload(location_id, 'Location', attr_name, img, trigger.get(0), {'edit_event':'click'});
        }
    };
    var dataBoxContract = function (datalink) {
        var dataBox = datalink.parent().parent();
        var modifylink = dataBox.find(".show");
        if (modifylink.length === 0) {
            modifylink = dataBox.find(".modify");
        }
        var contentNode = dataBox.find(".dataBoxContent");
        if (contentNode.css('display') !== "none") {
            modifylink.hide();
            var up = jq(contentNode).hide("blind", {direction:"vertical"}, 1000);
            datalink.parent().attr('class', "dataBoxHeaderCollapse");
            data_expandors[section_name][subsection_no][datalink.attr('id')][1] = 0;
        }
        datalink.one('click', function () {
            dataBoxExpand(jq(this));
        });
    };
    var dataBoxExpand = function (datalink) {
        var dataBox = datalink.parent().parent();
        var modifylink = dataBox.find(".show");
        if (modifylink.length === 0) {
            modifylink = dataBox.find(".modify");
        }
        var contentNode = dataBox.find(".dataBoxContent");
        if (contentNode.css('display') === "none") {
            modifylink.show();
            var down = jq(contentNode).show("blind", {direction:"vertical"}, 1000);
            datalink.parent().attr('class', "dataBoxHeader");
            data_expandors[section_name][subsection_no][datalink.attr('id')][1] = 1;
        }
        datalink.one('click', function () {
            dataBoxContract(jq(this));
        });
    };
    var setLinkState = function (data, link) {
        link = jq(link);
        var id = link.attr('id');
        if (id && !data[id]) {
            if (id === 'link_todobar_urgent' || id === 'link_todobar_today' || id === 'link_addTodobar') {
                data[id] = [link, 1];
            } else if (section_name === 'host' && subsection_name === 'todos') {
                data[id] = [link, 0];
            } else if (id.substring(0, 4) === 'help') {
                data[id] = [link, 0];
            } else {
                data[id] = [link, 1];
            }
        }
        if (id) {
            if (data[id][1] == 1) {
                dataBoxExpand(link);
            } else {
                dataBoxContract(link);
            }
        }
    };
    var o = {
        section_name: function () {
            return section_name;
        },
        current_profile_id: function () {
            return current_profile_id;
        },
        current_user_id: function () {
            return current_profile_id;
        },
        addBoxExpanders: function () {
            if (subsection_no !== undefined) {
                var data = data_expandors[section_name][subsection_no];
                jq('div#' + section_name + '-' + subsection_name + 'Content a.title').each(function (i, ele) {
                    setLinkState(data, ele);
                });
                data_expandors[section_name][subsection_no] = data;
            }
        },
        load_user_from_id: function (id, subsection) {
            current_profile_id = id;
            make_section_switch = false;
            if (section_name !== 'network') {
                section_no = 0;
                make_section_switch = true;
            } else if (current_user_id == current_profile_id && section_name === 'network') {
                //switch back to the profile tab when we select the currently logged in user
            	section_no = 1;
            	make_section_switch = true;
            }
            section_name = sections[section_no];
            current_subsections = subsections[section_name];
            if (subsection) {
                subsection_no = subsection;
            } else if ((subsection_no == 1 || subsection_no == 2) && section_name == 'network') {
                subsection_no = subsection_no;
            } else {
                subsection_no = subsection_defaults[section_name];
            }
            subsection_name = current_subsections[subsection_no];
            load_subsection(subsection_no);
            return false;
        },
        load_user: function (ele, subsection) {
            var id = ele.attr('id').split('-')[1];
	    o.load_user_from_id(id, subsection);
        },
        image_listeners: function () {
            var prof_trigger = jq('#upload_image' + current_profile_id);
            var prof_img = jq('#profile_image' + current_profile_id);
            if (prof_trigger.length && prof_img.length) {
                var up = new Upload(current_profile_id, 'User', 'image', prof_img.get(0), prof_trigger.get(0), {'edit_event':'click'});
            }
        },
	switch_tab: function (new_section_no, new_subsection_no) {
            section_no = new_section_no;
            subsection_no = new_subsection_no;
            section_name = sections[section_no];
            current_subsections = subsections[section_name];
            subsection_name = current_subsections[subsection_no];
            make_section_switch = true;
            switch_subsection();
        },
	tab_specifics: function () {
            if (subsection_name === "addMember") {
               jq("#submit_add_member").click(function () {
                    add_member();
               });
            }
            if (section_name === 'space') {
                set_space_listeners();
            }
            if (subsection_name === 'mainProfile') {
                set_inplace_edit(current_profile_id, 'User', 'memberProfile_' + current_profile_id, null, null, null, null, o.image_listeners, null, editMemberProfileListeners, null);
                set_inplace_edit(current_profile_id, 'User', 'memberDescription_' + current_profile_id, 'memberDescriptionEdit');
                set_inplace_edit(current_profile_id, 'User', 'memberServices_' + current_profile_id, 'memberServicesEdit');
                set_inplace_edit(current_profile_id, 'User', 'relationshipStatus_' + current_profile_id, 'relationshipStatusEdit');
                set_inplace_edit(current_profile_id, 'User', 'bristolData_' + current_profile_id);

                o.addBoxExpanders();
                var notes = new Notes(current_profile_id, 'note');
                jq('#addCard_' + current_profile_id).click(addCardForm);
                removeCard();
                o.image_listeners();
                select_tariff_location();
            }
            if (subsection_name === 'billing') {
                o.addBoxExpanders();
                set_billing_listeners();
            }
            if (section_name === 'host' && subsection_name === 'todos') {
                var todo = new Todos();
            }
            if (section_name === 'host' && subsection_name === 'admin') {
               jq('#select_admin_location').change(load_admin);
	       admin_listeners();
            }
            if (section_name === 'host' && subsection_name === 'invoicing') {
               jq('#invoices_search').click(search_invoices);
            }
            if (section_name === 'host' && subsection_name === 'managementdata') {
               jq('#usage_summary_csv').click(get_usage_summary);
               jq('#users_grid').click(show_users_grid);
               jq('#users_csv').click(get_users_csv);
               jq('#generate_report').click(get_report);
               o.addBoxExpanders();
            }
            if (section_name === 'host' && subsection_name === 'resources') {
               var res = new Resources();
            }
            if (section_name === 'host' && subsection_name === 'openTimes') {
               var ot = openTimes();
            }
        }
    };
    navigation = o;
    jq("ul#nav a.load_section").click(load_section);
    set_tab_events();
    return o;
};


//////////////CARD REGISTRAION////////////////////////////////////////
var removeCard = function() {
    var user_id = navigation.current_profile_id();
    var remove_button = jq('#removeCard_' + user_id);
    if (!remove_button.length) {
        return;
    }
    var complete_remove = function () {
        jq('#addCard_' + user_id).show().click(addCardForm);
        return false;
    };
    var rfid_area = jq('#memberRFID_' + user_id);
    var options = {action: function () {
        rfid_area.load("/rfid/unregister_card", {user_id: user_id}, complete_remove);
    },
                   message: 'Are you sure you want remove the card from this user? '
    };
    remove_button.confirm_action(options);
};
var addCardForm = function () {
    var add_button = jq(this);
    add_button.hide();
    var id = add_button.attr('id').split('_')[1];
    var rfid_area = jq('#memberRFID_' + id);
    var user_id = navigation.current_profile_id();
    rfid_area.html('<div><p>Please swipe the card to register it to this user</p><form id="add_card_form{user}" action="add_card"><input name="rfid" type="text" /></form></div>'.supplant({user: user_id}));
    var rfid_form = rfid_area.find('form');
    var submit_addCard = function () {
       rfid_area.load("/rfid/add_card", {user_id: user_id, rfid: rfid_input.val()}, function () {
           removeCard();
       });
       return false;
    };
    rfid_form.submit(submit_addCard);
    var rfid_input = rfid_area.find('input');
    rfid_input.focus();
};
//////////////INITIALISATION//////////////////////////////////////////

var loc = {};
var navigation = {};
loc.init = function (event) {
    jq.datepicker.setDefaults({firstDay: 1, dateFormat: 'D, dd MM yy'});
    this.img = new Image();
    this.img.src = "/display_image/Location/0/logo";
    jq('#header').css('backgroundImage', "url(" + this.img.src + ")").css('backgroundPosition', 'top left');
    window.source_no = 0;
    var tab = new Tabs();
    var search = new Search();
    set_members_listeners();
    draw();
    window.onresize = draw;
    set_ajax_globals();
};
jq(document).ready(loc.init);

//////////////////////SPACE//////////////////////////////////////
var update_space_display = function (datetext, callback, switch_type) {
    if (datetext && typeof(datetext) === 'string') {
        jq("#space_date").html(datetext + '<img src="/static/images/booking_down.png" />');
    }

    var params = jq("#space_loc_time").serializeArray();
    if (switch_type) {
        params[params.length] = {'name': 'switch', 'value': switch_type};
    }
    if (!callback) {
        callback = set_space_listeners;
    }
    jq('#space-bookingContent').load('/load_make_booking', params, callback);
};
var date_left_right = function (evt) {
    Event.stopObserving(Event.element(evt), 'click', date_left_right);
    var date = Event.element(evt).parentNode.className;
    jq('#space_date_field').val(date);
    update_space_display(null);
};
var select_week = function (date, inst) {
    var selected_date = jq.datepicker.parseDate('D, dd MM yy', date);
    var start_week = new Date(selected_date.getTime() - (((selected_date.getDay() + 6) % 7) * 1000 * 60 * 60 * 24));
    jq.datepicker._stayOpen = false;
    inst._rangeStart = start_week;
    var end_week = new Date(selected_date.getTime() + (((7 - selected_date.getDay()) % 7) * 1000 * 60 * 60 * 24));
    jq('#space_date_field').datepicker('setDate', start_week, end_week);
    var range = jq('#space_date_field').datepicker('getDate');
    range = jq.datepicker.formatDate('D, dd MM yy', range[0]) + ' - ' + jq.datepicker.formatDate('D, dd MM yy', range[1]);
    jq('#space_date_field').val(range);
    jq("#space_date").html(range + '<img src="/static/images/booking_down.png" />');
    var params = jq("#space_loc_time").serializeArray();

    jq('#space-bookingContent').load('/load_make_booking', params, set_space_listeners);
};
jq.fn.check = function () {
    return this.each(function () {
        this.checked = true;
    });
};
var select_room = function (room_id, room_no) {
    jq('#room_selector_group a.label_selected').removeClass('label_selected');
    jq('#room_selector_group #room_selector-' + room_id + ' a.label').addClass('label_selected').next().find('input:not(:checked)').check().click().check(); /*nasty hack seems to work*/
    jq('#bookspacedate .day_group .' + room_no).addClass('room_selected');
    jq('#bookspacedate .day_group div:not(.' + room_no + ')').removeClass('room_selected');
    jq('#room_selected').val(room_id);
};
var set_space_listeners = function (response) {
    jq('.view_switch').click(function () {
        update_space_display(null, null, jq(this).attr('name'));
    });
    jq('.space_switch').change(function () {
        //pass 'location' or 'res_group' depending on what we are switching
        update_space_display(null, null, jq(this).attr('name'));
    });
    jq('#bookingDateRange #space_date_field').datepicker({rangeSelect: true, onSelect: select_week, changeFirstDay: false});
    jq('#bookingDate #space_date').click(function () {
        jq('#space_date_range_field').datepicker('show');
    });
    jq('#space_date_field').datepicker({onSelect: function () {
        update_space_display(null);
    }
    });
    jq('#space_date').click(function () {
        jq('#space_date_field').datepicker('show');
    });
    jq('#rightArrow').click(date_left_right);
    jq('#leftArrow').click(date_left_right);
    jq('.day_group .day_marker').click(goto_day);
    jq('.day_group .event, .day_group .unavailable').click(function () {
        var room_no = jq(this).attr('id').split("-");
        room_no = room_no[room_no.length - 1];
        jq('#room_selector_group div.' + room_no + ' a.label').click();
    });
    jq('#room_selector_group a.label').click(function () {
        var room_no = jq(this).parent().attr('class').split(" ")[1];
        select_room(jq(this).parent().attr('id').split("-")[1], room_no);
    });
    jq('#room_selector_group input').click(function () {
        var room = jq(this).parent().parent().attr('class').split(" ")[1];
        if (this.checked) {
            jq('#bookspacedate .day_group .' + room).removeClass('resource_off').addClass('resource_on');
        } else {
            jq('#bookspacedate .day_group .' + room).removeClass('resource_on').addClass('resource_off');
        }
    });
    jq('#only_my_bookings').click(function () {
        if (this.checked) {
            jq('.event:not(.mybooking), .unavailable').removeClass('other_booking').addClass('other_booking_off');
        } else {
            jq('.event:not(.mybooking), .unavailable').removeClass('other_booking_off').addClass('other_booking');
        }
    });
    jq('.bigcal_day').click(function (e) {
        try_day_book(e, jq(this));
    });
    jq('.bigcal_week').click(function (e) {
        try_week_book(e, jq(this));
    });
    set_space_expanders(response);

};
var try_day_book = function (event, listener) {
    var hit = jq(event.target);
    var date_str = listener.children().attr('className');
    var booking = create_booking(date_str);
    var rusage_id = 0;
    var resource_id = 0;
    if (hit.hasClass('event')) {
        rusage_id = hit.attr('id').split('-')[1];
        booking.edit_booking(event, listener, rusage_id);
    } else if (hit.hasClass('unavailable')) {
        rusage_id = hit.attr('id').split('-')[1];
        resource_id = hit.attr('id').split('-')[2];
        booking.explain_unavailable(event, listener, rusage_id, resource_id);
    } else if (hit.hasClass('room_group')) {
        resource_id = hit.attr('id').split('-')[1];
        booking.start_booking(event, listener, resource_id);
    }
};
var try_week_book = function (event, listener) {
    var hit = jq(event.target);
    var day_group = hit;
    if (!day_group.hasClass('day_group')) {
        day_group = day_group.parent();
    }
    if (hit.parents('#booking_popup').length) {
        return;
    }
    var date_str = day_group.find('.day_marker').attr('id');
    var booking = create_booking(date_str);
    var rusage_id = 0;
    var resource_id = 0;
    if (hit.hasClass('event')) {
        rusage_id = hit.attr('id').split('-')[1];
        booking.edit_booking(event, listener, rusage_id);
    } else if (hit.hasClass('unavailable')) {
        rusage_id = hit.attr('id').split('-')[1];
        resource_id = hit.attr('id').split('-')[2];
        booking.explain_unavailable(event, listener, rusage_id, resource_id);
    } else if (hit.hasClass('day_group')) {
        resource_id = jq('#room_selector_group a.label_selected').attr('id');
        if (!resource_id) {
            resource_id = jq('#room_selector_group a.label').attr('id');
        }
        resource_id = resource_id.split('-')[1];
        booking.start_booking(event, listener, resource_id);
    }
};
var create_booking = function (date_str) {
    var data = null;
    var date = jq.datepicker.parseDate('D, dd MM yy', date_str);
    var rusage_id = null;
    var start_time = null;
    var pos = null;
    var pix_per_hour = 36;
    var start_rounding = 30;
    var re_edit = false;
    var event_node = null;
    var event_height = null;
    var booking_popup = jq('#booking_popup');
    var round_popup_offset = function (pos) {
        var temp = pos + parseInt((Math.round(start_rounding / 2) * pix_per_hour / 60), 10);
        var rounding_pix = pix_per_hour * start_rounding / 60;
        return parseInt((temp / rounding_pix), 10) * rounding_pix;
    };
    var get_clicked_day_start_time = function (listener, pos) {
        pos = round_popup_offset(pos);
        var hour_offset = parseInt(listener.children().attr('id').split('-')[1], 10);
        var start_hour = parseInt((pos / pix_per_hour), 10) + hour_offset;
        var start_minute = parseInt(((pos % pix_per_hour) * (60 / pix_per_hour)), 10);
        start_minute = start_minute + (Math.round(start_rounding / 2));
        if (start_minute >= 60) {
            start_minute = start_minute - 60;
            start_hour = start_hour + 1;
        }
        start_minute = parseInt((start_minute / start_rounding), 10) * start_rounding;
        return format_start_datetime(date, start_hour, start_minute);
    };
    var edit_booking_listen = function (response) {
        if (re_edit) {
            booking_popup.show();
            jq('table#meetingBooking').parent().html(response);
        } else {
            booking_popup.show().children('div').html(response);
        }
        booking_listen(response);
        jq('#booking_popup #resource_id').one('change', function () {
            re_edit_booking(pos, start_time);
        });
        jq('#booking_popup .start_time').one('change', function () {
            pos = offset_from_start_time(jq('#start_hour').val(), jq('#start_minute').val());
            re_edit_booking(pos, format_start_datetime(date, jq('#start_hour').val(), jq('#start_minute').val(), date));
        });
        jq('#booking_popup .end_time').change(function () {
            var hour_diff = data.end_hour - jq('#end_hour').val();
            var min_diff = data.end_minute - jq('#end_minute').val();
            var total_hours_diff = hour_diff + (min_diff / 60);
            var total_pix_diff = parseInt((total_hours_diff * pix_per_hour), 10);
            data.end_hour = jq('#end_hour').val();
            data.end_minute = jq('#end_minute').val();
            if (!data.old_height) {
                data.old_height = data.height;
                data.event_height = event_node.height();
                event_height = data.event_height;
                data.event_end = event_node.find('.display_end').html();
            }
            data.height -= total_pix_diff;
            booking_popup.css('top', data.height + 5);
            event_height -= total_pix_diff;
            event_node.height(event_height);
            event_node.find('.display_end').html(data.end_hour + ':' + data.end_minute);
            booking_popup.find('.cancel, .close_popup').click(function () {
                data.height = data.old_height;
                event_node.height(data.event_height);
                event_node.find('.display_end').html(data.event_end);
                delete data.old_height;
            });
        });
    };
    var add_booking_listen = function (response) {
        booking_popup.show().children('div').html(response);
        booking_listen(response);
        window.location.hash = '#booking_popup';
        jq('#booking_popup #resource_id').one('change', function () {
            do_start_booking(pos, start_time, end_time, jq(this).val());
        });
        jq('#booking_popup .start_time').one('change', function () {
            pos = offset_from_start_time(jq('#start_hour').val(), jq('#start_minute').val());
            end_time = format_start_datetime(date, jq('#end_hour').val(), jq('#end_minute').val(), date);
            do_start_booking(pos, format_start_datetime(date, jq('#start_hour').val(), jq('#start_minute').val(), date), end_time, jq('#booking_popup #resource_id').val());
        });
        jq('#submit_add_booking').click(function () {
            add_booking();
        });
    };
    var booking_listen = function (response) {
        jq('#booking_popup .close_popup').one('click', function () {
            booking_popup.hide();
            window.location.hash = '#';
        });
        /*jq('#date_field').datepicker({onSelect:function (datetext) {
            jq('#date_field').val(datetext);
        }});
        jq('#date_display').click(function () {
            jq('#date_field').datepicker('show');
        });*/
        jq("#booking_for").autocomplete("/filter_book_for", {width: 260,
                                                             selectFirst: true,
                                                             matchSubset: false});
        jq("#booking_for").result(function (event, data, formatted) {
            jq('#booking_for_id').val(data[1]);
        });

    };
    var add_booking = function () {

        var params = jq('#add_booking').serializeArray();
        var xhr = jq.post('/add_booking', params, function (response) {
            finish_booking(response, xhr);
        });
    };
    var finish_booking = function (response, xhr) {
        if (xhr.getResponseHeader('X-JSON') !== 'success') {
            add_booking_listen(response);
        } else {
            booking_popup.hide();
            update_space_display(null);
        }

    };
    var re_edit_booking = function (pos, start_time) {
        re_edit = true;
        booking_popup.css('top', pos + 100); //pos+height
        booking_popup.hide();

        var params = jq('#meetingBooking-inplaceeditor').serializeArray();
        params[params.length] = {'name': 'id', 'value': rusage_id};
        jq.post('/edit_booking', params, function (response) {
            edit_booking_listen(response, true);
        });
    };
    var reload_booking_details = function (data) {
        set_space_listeners();
        rusage_id = JSON.parse(data).rusage_id;
        jq('#day_rusage-' + rusage_id).click();
    };
    var load_booking_details = function (rusage_data, event, listener) {
        event_node = jq(event.target);
        data = rusage_data;
        booking_popup.css('top', data.height + 5).show().children('div').html(data.render);
        jq('#booking_popup .close_popup').one('click', function () {
            booking_popup.hide();
            window.location.hash = '#';
        });
        start_time = data.start_time;
        rusage_id = data.rusage_id;
        set_inplace_edit(rusage_id, 'RUsage', 'meetingBooking', 'meetingBookingEdit', null, null, null, function (data) {
            booking_popup.hide();
            update_space_display(null, function () {
                reload_booking_details(data);
            });
        }, null, function (data) {
            edit_booking_listen(data.render);
        });
        var options = {action: function (ele) {
            confirm_delete_rusage(ele);
        },
                       message: 'Are you sure you want to cancel this booking? '};
        jq("#del_booking").confirm_action(options);
        jq('.notify_on_available').click(function (evt) {
            var r_id = Event.element(evt).id.split('-')[1];
            var req = new Ajax.Request('/addToResourceQueue', {parameters: "rusage_id=" + r_id, method: 'post', onComplete: jq(this).remove()});
        });
        jq('.confirmBooking').click(function (evt) {
            var r_id = Event.element(evt).id.split('-')[1];
            var req = new Ajax.Request('/confirmBooking', {parameters: "rusage_id=" + r_id, method: 'post', onComplete: jq(this).val("Confrmed.")});
            var params = jq("#space_loc_time").serializeArray();
            booking_popup.hide();
            jq('#space-bookingContent').load('/load_make_booking', params, set_space_listeners);
        });

    };
    var do_start_booking = function (pos, start_time, end_time, resource_id) {
        booking_popup.css('top', round_popup_offset(pos));
        booking_popup.hide();

        var form_params = jq('#add_booking').serializeArray();
        var params = {};
        jq.each(form_params, function() {
               params[this.name] = this.value;
        });
        params['resource_id'] = resource_id;
        params['start_datetime'] = start_time;
        params['end_datetime'] = end_time;

        jq.post('/start_booking', params, function (response) {
            add_booking_listen(response);
        });
    };
    var do_explain_unavailable = function (data, event, listener) {
        booking_popup.show();
        booking_popup.css('top', data.height + 5).show().children('div').html(data.render);
        jq('#booking_popup .close_popup').one('click', function () {
            booking_popup.hide();
            window.location.hash = '#';
        });

    };
    var o = {
        start_booking: function (event, listener, resource_id) {
            pos = event.pageY - listener.offset().top;
            start_time = get_clicked_day_start_time(listener, pos);
            end_time = get_clicked_day_start_time(listener, pos);
            do_start_booking(pos, start_time, end_time, resource_id);
        },
        edit_booking: function (event, listener, rusage_id) {

            jq.ajax({
                type: "GET",
                url: '/get_rusage?rusage=' + rusage_id + '&date=' + date_str,
                success: function (data) {
                    load_booking_details(data, event, listener);
                },
		error: function(XMLHttpRequest, textStatus, errorThrown) {
		    var data = JSON.parse(XMLHttpRequest.responseText);	//jquery's json parser doesn't always work
 		    load_booking_details(data, event, listener);
		},
		dataType: "json"
            });
        },
        explain_unavailable: function (event, listener, rusage_id, resource_id) {

            jq.getJSON('/explain_unavailable', {resource_id: resource_id, rusage_id: rusage_id, date: date_str}, function (data) {
                do_explain_unavailable(data, event, listener);
            });
        }
    };
    return o;
};
var offset_from_start_time = function (hour, min) {
    var pix_per_hour = 36;
    var hour_offset = parseInt(jq('#bookspacedate').children().attr('id').split('-')[1], 10);
    hour -= hour_offset;
    return (hour + min / 60) * pix_per_hour;
};
var format_start_datetime = function (date, start_hour, start_minute) {
    return jq.datepicker.formatDate('D, dd MM yy', date) + ' ' + start_hour + ':' + start_minute + ':00';
};
var goto_day = function (evt) {
    jq('#space_date_field').val(evt.target.id);
    jq('#day_view_switch').trigger('click').trigger('change');
};
var set_space_expanders = function () {
    navigation.addBoxExpanders();

};
/////////////////////////////////Open Times //////////////////////
var openTimes = function () {
    jq.each(jq('#OpenTimes .openTime'), function (i, ele) {
        var attrs = ele.id.split('_');
        var date = attrs[1];
        var loc = attrs[2];
        var save_func = '/save_openTime/' + loc + '/' + date.replace(/-/, ', ').replace(/-/g, ' ');
        var load_func = '/load_openTime/' + loc + '/' + date.replace(/-/, ', ').replace(/-/g, ' ');
        set_inplace_edit(0, 'Open', ele.id, 'time_range_select', save_func, load_func, null, null, 'cal');
    });
};
///////////////////////////////// billing  ///////////////////////
var set_billing_listeners = function () {
    var section_name = navigation.section_name();
    jq('table.invoice_history a.view_invoice').unbind('click');
    jq('table.invoice_history a.view_invoice').click(view_invoice);
    jq('table.invoice_history a.pdf_invoice').unbind('click');
    jq('table.invoice_history a.pdf_invoice').click(pdf_invoice);
    var user = navigation.current_profile_id();
    jq('#create_invoice_' + user).unbind('click');
    jq('#create_invoice_' + user).one('click', create_new_invoice);
    jq('table.invoice_history a.remove_invoice').unbind('click');
    jq('table.invoice_history a.remove_invoice').one('click', remove_invoice);
    jq('td.resent_' + user + ' a, a#unsent_invoice_' + user).unbind('click');
    jq('td.resent_' + user + ' a, a#unsent_invoice_' + user).click(send_invoice_template);
    jq('#' + section_name + '-billingContent table a.view_sub_usages').one('click', view_sub_usages);
    jq('#' + section_name + '-billingContent table a.add_to_invoice').unbind('click');
    jq('#' + section_name + '-billingContent table a.add_to_invoice').click(add_rusage_to_invoice);
    var options = {action: function (ele) {
        confirm_delete_rusage(ele);
    },
                   message: 'Are you sure you want to delete this usage? '};
    jq('#' + section_name + '-billingContent table a.del_rusage').confirm_action(options);
    jq.each(jq('#' + section_name + '-billingContent table div.custom_cost'), function (i, ele) {
        listen_custom_costs(ele);
    });
    jq('#redirect_billed_to').unbind('click');
    jq('#redirect_billed_to').one('click', function () {
        navigation.load_user_from_id(jq(this).attr('class'));
        return false;
    });
    jq('#' + user + '_resource').unbind('change');
    jq('#' + user + '_resource').change(switch_resource);
    set_inplace_edit(user, 'User', 'billingDetails_' + user, 'billingDetailsEdit', null, null, null, reload_billing, null, edit_billing);
};
var edit_billing = function () {
    var options = jq('#billto .bill_options');
    var form = jq("#billingDetails_{user}-inplaceeditor".supplant({user: navigation.current_profile_id()}));
    var disable = function () {
        var select = jq(this);
        var to_profile = jq('#bill_to_profile');
        var option = select.find(':selected');
        if (option.attr('id') != 'self') {
            disable_other_form_fields(form, select);
        } else if (to_profile.attr('checked') == 'true') {
            to_profile.parent().parent().show();
            to_profile.attr('disabled', 'false');
        } else {
             enable_form_fields(form);
        }
    };
    jq('#billto').change(disable);
    var disable_address = function () {
        var checkbox = jq(this);
        if (checkbox.attr('checked')) {
            // disable_other_form_fields(form, checkbox); // commented to solve #493 #490 need a close look later
        } else {
            enable_form_fields(form);
        }
    };
    jq('#bill_to_profile').click(disable_address);
};
var disable_other_form_fields = function (form, current_field) {
    jq('#' + form.attr('id') + ' :input:not(:image):not(select)[@id!=' + current_field.attr('id') + ']').attr('disabled', 'disabled').parent().parent().hide();
};
var enable_form_fields = function (form) {
    jq('#' + form.attr('id') + ' :input:disabled').removeAttr('disabled').parent().parent().show();
};
var listen_custom_costs = function (element) {
    set_inplace_edit(element.id.split('-')[1], 'RUsage', element.id, 'costEdit', '/save_costEdit', null, null, reload_billing);
};
var switch_resource = function () {
    var user = navigation.current_profile_id();
    var resource = jq(this).val();
    if (resource === 0) {
        jq('#' + user + '_resource_form').html("");
        return;
    }
    var params = {'object_type': 'Resource', 'object_id': resource, 'user': user};

    jq('#' + user + '_resource_form').load('/get_widget/addRusage', params, function (response) {
        set_add_rusage_listeners();
    });
};
var set_inplace_cal = function (trigger, input) {
    input.datepicker({onSelect: function (datetext) {
        trigger.html(datetext + '<img src="/static/images/booking_down.png" />');
    }});
    trigger.click(function () {
        input.datepicker('show');
        input.blur();
    });
};
var set_add_rusage_listeners = function () {
    var user = navigation.current_profile_id();
    set_inplace_cal(jq('#display_rusage_date'), jq('#date'));
    jq('#' + user + '_submit_add_rusage').one('click', submit_add_rusage_form);
    jq('#' + user + '_cancel_add_rusage').one('click', remove_add_rusage_form);

};
var remove_add_rusage_form = function () {
    var user = navigation.current_profile_id();
    jq('#' + user + '_resource_form').html('');
};
var submit_add_rusage_form = function () {
    var page_user = navigation.current_profile_id();
    var parameters = jq('#' + page_user + '_add_rusage_form').serializeArray();
    parameters[parameters.length] = {'name': 'pagetype', 'value': 'billing'};
    parameters[parameters.length] = {'name': 'pageuser', 'value': page_user};

    var xhr = jq.post('/add_booking', parameters, function (response) {
        finish_add_rusage(response, xhr);
    });
};
var finish_add_rusage = function (response, xhr) {
    if (xhr.getResponseHeader('X-JSON') === 'success') {
        jq('#' + navigation.current_profile_id() + '_uninvoiced').html(response);
        refresh_billing(response);
    } else {
        jq('#' + navigation.current_profile_id() + '_resource_form').html(response);
        var user = navigation.current_profile_id();
        jq('#' + user + '_submit_add_rusage').one('click', submit_add_rusage_form);
        jq('#' + user + '_cancel_add_rusage').one('click', remove_add_rusage_form);
    }

};
var create_new_invoice = function () {
    var user_id = navigation.current_profile_id();
    var params = jq('#' + user_id + '_change_create_invoice_dates').serializeArray();
    var cannot = jq('#' + user_id + "_cannot_create").css('display', 'block');
    if (cannot.length > 0) {
        return;
    }

    jq('#' + navigation.section_name() + "-billingContent").load('/create_invoice', params, function (response) {
        refresh_billing(response);
    });
};
var remove_invoice = function () {

    jq.post("/remove_invoice", 'invoiceid=' + jq(this).attr('id').split('_')[1], function () {
        reload_billing();
    });
};
var refresh_billing = function (response, message) {
    if (typeof(message) === 'string') {//when the invoice has been sent
        jq('#send_invoice_' + navigation.current_profile_id()).html(message);
    }
    navigation.addBoxExpanders();
    set_billing_listeners();

};
var reload_billing = function (message) {
    jq('#' + navigation.section_name() + "-billingContent").load('/load_tab', {'object_type': 'User', 'object_id': navigation.current_profile_id(), 'section': 'billing'}, function (resp) {
        refresh_billing(resp, message);
    });
};

var send_invoice_template = function () {
    var user = navigation.current_profile_id();
    var invoice_id = jq(this).attr('class');

    jq('#invoice_area_' + user).html("");
    jq('#send_invoice_' + user).load('/load_tab', {'object_type': 'Invoice', 'object_id': invoice_id, 'section': 'send_invoice'}, send_invoice_listen);
    window.location = "#send_it";
};
var send_invoice_listen = function () {
    jq('#submit_invoice_mail').one('click', send_invoice);
    jq('#cancel_invoice_mail').one('click', cancel_send_invoice);

};
var send_invoice = function () {
    var email_params = jq("#send_invoice_form").serializeArray();

    jq.post("/send_invoice", email_params, function (response) {
        reload_billing(response);
    }); //ensure correct
    window.location = "#";
};
var cancel_send_invoice = function (evt) {
    var user = navigation.current_profile_id();
    jq("#send_invoice_" + user).html("");
    window.location = "#";
};
var view_invoice = function () {
    var invoice_id = jq(this).attr('id').split('_')[1];
    var user = navigation.current_profile_id();

    cancel_send_invoice();
    jq('#send_invoice_' + user).html("");
    jq('#invoice_area_' + user).load("/display_invoice", {'invoiceid': invoice_id}, on_view_invoice);
};

// This is not required if default encoding is utf-8
var pdf_invoice = function () {
    var invoice_id = jq(this).attr('id').split('_')[1];
    var invoice_name = escape(jq(this).attr('id').split('_')[2]);

    invoice_url = '/pdf_invoice/' + invoice_id + '/' + invoice_name + '.pdf'
    window.open(invoice_url, "_blank");

};

var on_view_invoice = function (response) {
    var section_name = navigation.section_name();
    jq('#' + section_name + '-billingContent table a.remove_from_invoice').one('click', remove_rusage_from_invoice);
    jq('#' + section_name + '-billingContent table a.view_sub_usages').one('click', view_sub_usages);

};
var add_rusage_to_invoice = function () {

    jq.post('/add_rusage_to_invoice', {'invoiceid': jq('#open_invoice').attr('class'), 'rusageid': jq(this).attr('id').split('-')[1]}, reload_billing);
};
var remove_rusage_from_invoice = function () {
    var invoice_id = jq('#open_invoice').attr('class');
    var rusage = jq(this).attr('id').split('-')[1];

    jq.post('/remove_rusage_from_invoice', {'invoiceid': invoice_id, 'rusageid': rusage}, reload_billing);
};
var confirm_delete_rusage = function (ele) {
    var rusage = ele.attr('id').split('-')[1];
    page = 'billing';
    if (!rusage) {
        rusage = ele.attr('class');
        page = 'space';
    }
    var complete = complete_delete_rusage;
    if (page === 'billing') {
        complete = function (response) {
            remove_row(ele, response);
        };
    }

    var req = new Ajax.Request('/delete_rusage', {method: 'post', parameters: 'rusage=' + rusage, onComplete: complete});
};

var confirm_cancel_rusage = function (ele) {
    var rusage = ele.attr('id').split('-')[1];
    page = 'billing';
    if (!rusage) {
        rusage = ele.attr('class');
        page = 'space';
    }
    var complete = complete_delete_rusage;
    if (page === 'billing') {
        complete = function (response) {
            remove_row(ele, response);
        };
    }

    var req = new Ajax.Request('/cancel_rusage', {method: 'post', parameters: 'rusage=' + rusage, onComplete: complete});
};


var complete_delete_rusage = function (response) {
    jq('#booking_popup').hide();
    update_space_display(null);

};
var remove_row = function (ele, response) {
    ele.parent().parent().parent().remove();
    reload_billing(ele[0]);

};
var change_rusages_date = function (start_or_end, datetext) {
    var user = navigation.current_profile_id();
    jq('#create_invoice_' + start_or_end + '_' + user).val(datetext);
    jq('#display_create_invoice_' + start_or_end + '_' + user).html(datetext + ' <img src="/static/images/booking_down.png"> ');
    update_rusages();
};
var update_rusages = function () {
    var user_id = navigation.current_profile_id();
    var params = jq('#' + user_id + '_change_create_invoice_dates').serializeArray();

    jq('#rusage_area_' + user_id).load("/update_resource_table", params, refresh_billing);
};
var hide_sub_usages = function () {
    var link = jq(this);
    var table = link.parent().parent().parent().parent();
    link.attr('class', "view_sub_usages");
    link.one('click', view_sub_usages);
    jq("table#" + table.attr('id') + " tr.sub_" + link.attr('id').replace(' ', '')).hide();
};
var view_sub_usages = function () {
    var link = jq(this);
    var ids = link.parent().attr('id').split('_');
    var table = link.parent().parent().parent().parent();
    link.attr('class', 'sub_usages_open');
    link.one('click', hide_sub_usages);
    var current = navigation.current_profile_id();
    var earliest = jq("#create_invoice_start_" + current).val();
    var latest = jq("#create_invoice_end_" + current).val();
    var params = {'billed_user_id': current, 'ruse_user_id': ids[0], 'invoice_id': ids[1], 'resource_id': ids[2], 'earliest': earliest, 'latest': latest};
    var sub_resources = jq("table#" + table.attr('id') + " tr.sub_" + link.attr('id').replace(' ', ''));
    if (sub_resources.length === 0) {

        jq.getJSON('/insert_sub_usages', params, function (data) {
            insert_sub_usages(link, data);
        });
    } else {
        for (var i = 0; i < sub_resources.length; i++) {
            if (navigator.appName === "Microsoft Internet Explorer") {
                sub_resources[i].style.display = 'block';
            } else {
                sub_resources[i].style.display = 'table-row';
            }
        }
    }
};
var insert_sub_usages = function (link, json) {
    var top_table_row = link.parent().parent();
    var row_index = next_row(top_table_row)[0].rowIndex;
    var tbody = top_table_row.parent();
    var table = tbody.parent();
    var rows = json.rows;
    for (var i = 0; i < rows.length; i++) {
        var row = table[0].insertRow(row_index);
        row_index += 1;
        for (var j = 0; j < top_table_row[0].cells.length; j++) {
            var cell = row.insertCell(j);
            jq(cell).html(String(json.rows[i][j]));
        }
        row.className = "sub_usage sub_" + link.attr('id').replace(' ', '');
        if (navigator.appName === "Microsoft Internet Explorer") {
            row.style.display = 'block';
        }
    }
    var ids = link.parent().attr('id').split('_');
    var invoice_id = ids[1];
    if (invoice_id == '0') {
        jq.each(jq('table#' + table.attr('id') + ' div.custom_cost'), function (i, ele) {
            listen_custom_costs(ele);
        });
        var options = {action: function (ele) {
            confirm_delete_rusage(ele);
        },
                       message: 'Are you sure you want to delete this usage? '};
        jq('table#' + table.attr('id') + ' a.del_rusage').confirm_action(options);
        if (jq('#send_invoice_' + ids[3])) {
            jq('#' + table.attr('id') + ' a.add_to_invoice').click(add_rusage_to_invoice);
        }
    }
    if (invoice_id != '0' && jq('#send_invoice_' + ids[3])) {
        jq('table#' + table.attr('id') + ' a.remove_from_invoice').one('click', remove_rusage_from_invoice);
    }

};
var next_row = function (cell) {
    var cell2 = cell.next();
    if (cell2[0].tagName === 'TR') {
        return cell2;
    } else {
        return next_row(cell2);
    }
};
var toggleDetails = function (id) {
    jq('#memberDetails').show().load('/mini_user_detail', {'id': id}, draw);
};
var closeDetails = function() {
    jq('#memberDetails').html('').hide();
    draw();
};
var draw = function () {
    var members = jq('#members');
    var memberList = jq('#memberList');
    var pos = members.position();
    var doc_height = jq(window).height();
    var members_height = doc_height - pos.top;
    members.height(members_height + 'px');
    var details_height = jq('#memberDetails:visible').outerHeight();
    if(typeof(details_height) !== "number") {
       details_height = 0;
    }
    memberList.height(members_height - 128 - details_height);
    var scroll = new ScrollObj(10, 12, 322, "track", "up", "down", "drag", "memberList", "membersContent");

};
var display_meeting_name = function (data) {
    if (data) {
        overlib(data);
    }
};
