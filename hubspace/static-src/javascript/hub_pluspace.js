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
var get_report = function (evt) {
    var form = jq('#report_conf').serializeArray();
    var params = jQuery.param(form);
    window.open('/generate_report?' + params, "_blank");
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
var Tabs = function (section_no, section_name, subsection_no, subsection_name) {
    var current_user_id = jq('#current_user_id').attr('class');
    var current_profile_id = current_user_id;
    var sections = ['network', 'profile', 'space', 'host'];
    var subsections = {'network': ['addMember', 'mainProfile', 'billing', 'fulltextsearch'],
                       'profile': ['mainProfile', 'billing'],
                       'space': ['booking'],
                       'host': ['invoicing', 'openTimes', 'admin', 'resources', 'managementdata']};
    var subsection_defaults = {'network': 1,
                               'profile': 0,
                               'host': 0,
                               'space': 0};
    var data_expandors = {'network': {1: {}, 2: {}, 3: {}},
                          'profile': {0: {}, 1: {}},
                          'host': {0: {}, 1: {}, 2: {}, 3: {}, 4: {}},
                          'space': {0: {}}};
    var make_section_switch = false;
    var edited_subsection = 0;
    var current_subsections = subsections[section_name];
    // var subsection_no = subsection_defaults[section_name];
    // var subsection_name = current_subsections[subsection_no];
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
            jq('.change_avatar').click( function () {
                // http://plus.the-hub.net/avatar/shon/change/
                var url = 'http://plus.the-hub.net/avatar/' + jq(this).attr('id').split('-')[1] + '/change/';
                var html = '<iframe src="' + url + '" width="700" height="700"/>';
                var dialog = jq('<div></div>').html(html).dialog({
                    autoOpen: false,
                    title: 'Change Avatar',
                    height: 700,
                    width: 700,
                    position: 'top',
                    resizable: true,
                    });
                dialog.dialog('open');
                });
           
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
            // if (section_name === 'host' && subsection_name === 'todos') {
            //    var todo = new Todos();
            // }
            if (section_name === 'host' && subsection_name === 'admin') {
               jq('#select_admin_location').change(load_admin);
	       admin_listeners();
            }
            if (section_name === 'host' && subsection_name === 'invoicing') {
               jq('#invoices_search').click(search_invoices);
            }
            if (section_name === 'host' && subsection_name === 'managementdata') {
               jq('#users_grid').click(show_users_grid);
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
    jq.datepicker.setDefaults({firstDay: 1, dateFormat: 'D, dd MM yy'}); //, showButtonPanel: true});
    this.img = new Image();
    this.img.src = "/display_image/Location/0/logo";
    jq('#header').css('backgroundImage', "url(" + this.img.src + ")").css('backgroundPosition', 'top left');
    window.source_no = 0;
    var tab = new Tabs(section_no, section_name, subsection_no, subsection_name);
    // var search = new Search();
    // set_members_listeners();
    // draw();
    window.onresize = draw;
    set_ajax_globals();
};

jq(document).ready(loc.init);

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
    // draw();
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
var draw = function () {};

var display_meeting_name = function (data) {
    if (data) {
        overlib(data);
    }
};
