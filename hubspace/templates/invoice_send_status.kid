<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
<?python
send_status_class = 'success' if 'success' in send_status else 'warning'
?>
<script>
var html = ' \
<tr> \
    <td>${sr_no}</td> \
    <td>${invoice.user.display_name}</td> \
    <td>${invoice.number}</td> \
    <td>${invoice.amount}</td> \
    <td><a href="#" class="invoice_preview" id="preview-${invoice.id}">view</a></td> \
    <td class="success">${send_status}</td> \
</tr> \
';

$('.statuses').append(html);

$('#preview-' + ${invoice.id}).click( function () {
    var invoice_id = $(this).attr('id').split('-')[1];
    invoice_preview(invoice_id);
    }
);

</script>

</div>
