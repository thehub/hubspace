<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">

<?python
from hubspace.templates.billing import genInvoiceName
message =  "\\n".join(message_dict['body'].split('\n')).replace("'", "\\'") + ' '
# ^ needs to be better
subject = message_dict['subject']
?>

<script>
$('.statuses').show();
$('.progress').text("${progress_msg}");
var html = '\
<tr id="invoicebox-${invoice.id}"> \
    <td>${sr_no}</td> \
    <td>${invoice.user.display_name}</td> \
    <td>${invoice.created.strftime("%b %-d %Y")}</td> \
    <td>${invoice.amount}</td> \
    <td> \
        <a href="#NONE" class="invoice_preview" id="preview-${invoice.id}">html</a> | \
        <a href="/pdf_invoice/${invoice.id}/${genInvoiceName(invoice)}.pdf" target="_blank">pdf</a> \
    </td> \
    <td><a href="#" id="msg-${invoice.id}">message</a></td> \
    <td><input type="checkbox" checked="1" name="invoice_ids" id="select_${invoice.id}" class="invoice_ids" value="${invoice.id}"/></td> \
    <input type="hidden" name="subject_${invoice.id}" id="subject_${invoice.id}" value="${subject}"/> \
    <input type="hidden" name="message_${invoice.id}" id="message_${invoice.id}" value="${message}"/> \
    <input type="hidden" name="ponumbers_${invoice.id}" id="ponumbers_${invoice.id}" value=""/> \
</tr> \
 ';

$('.statuses').append(html);

$('#preview-' + ${invoice.id}).click( function () {
    var invoice_id = $(this).attr('id').split('-')[1];
    invoice_preview(invoice_id);
    }
);

$('#msg-' + ${invoice.id}).click( function () {
    var html = '\
        P. O. Number<br/>\
        <div class="container">\
        <div class="span-12 last"><input type="text" id="edit-ponumbers-${invoice.id}"/></div>\
        </div> \
        <div class="container">\
        <div class="span-12 last">Message</div> \
        </div> \
        <div class="container">\
        <div class="span-12 last"><textarea id="edit-message-${invoice.id}"></textarea></div> \
        </div> \
        <div class="container">\
        <div class="span-12 last"><input id="msg_save-${invoice.id}" type="button" value="Save"/> </div> \
        </div> ';
    var dialog = $('.preview').html(html).dialog({
        autoOpen: false,
        title: 'Invoice Message Preview',
        //height: 700,
        width: 450,
        position: 'left top'
        });
    dialog.dialog('open');
    $('#edit-message-${invoice.id}').html('${message}');
    $('#msg_save-${invoice.id}').click( function () {
        $('#message_${invoice.id}').val($('#edit-message-${invoice.id}').val());
        $('#ponumbers_${invoice.id}').val($('#edit-ponumbers-${invoice.id}').val());
        dialog.dialog('close');
    });
});

</script>

</div>
