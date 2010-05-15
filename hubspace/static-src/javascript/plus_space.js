var section_no = 2
var section_name = 'space';
var subsection_name = 'booking';
var subsection_no = 0;

var set_space_listeners = function (response) {
    jq.datepicker.setDefaults({firstDay: 1, dateFormat: 'D, dd MM yy'});
    // jq.datepicker.setDefaults({firstDay: 1, dateFormat: 'D, dd MM yy', showButtonPanel: true});
    jq('.view_switch').click(function () {
        update_space_display(null, null, jq(this).attr('name'));
    });
    jq('.space_switch').change(function () {
        //pass 'location' or 'res_group' depending on what we are switching
        update_space_display(null, null, jq(this).attr('name'));
    });
    // jq('#bookingDateRange #space_date_field').datepicker({rangeSelect: true, onSelect: select_week, changeFirstDay: false});
    jq('#bookingDateRange #space_date_field').datepicker({onSelect: select_week});
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
    range = start_week + ' - ' + end_week;
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

