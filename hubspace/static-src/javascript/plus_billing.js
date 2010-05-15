var section_no = 1;
var section_name = 'profile';
var subsection_name = 'billing';
var subsection_no = 1;

var set_billing_listeners = function () {
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
    jq("#for_billto").autocomplete("/filter_book_for", {width: 260,
                                                         selectFirst: true,
                                                         matchSubset: false});
    jq("#for_billto").result(function (event, data, formatted) {
        jq('#billto_id').val(data[1]);
    });
    set_billing_details();
    jq("input[name='billing_mode']").click( function () {
        set_billing_details();
    });
};

var set_billing_details = function () {
    var billing_mode = jq("input[name='billing_mode']:checked").val();
    if (billing_mode != 1) {
        jq('.billing_details').attr('disabled', 'disabled');
    } else {
        jq('.billing_details').removeAttr('disabled');
    };
};

