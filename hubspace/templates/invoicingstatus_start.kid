<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>


    <link rel="stylesheet" href="/static/css/micro/blueprint/screen.css" type="text/css" media="screen, projection, print"/>
    <!--[if lt IE 8]> 
    <link rel="stylesheet" href="/static/css/micro/blueprint/ie.css" type="text/css" media="screen, projection"/>
    <![endif]-->
    <link rel="stylesheet" href="/static/css/micro/typography.css" type="text/css" media="screen, projection, print"/>

    <link rel="stylesheet" type="text/css" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.1/themes/base/jquery-ui.css"/>

    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/jquery-ui.min.js"></script>
    <!-- <script type="text/javascript" src="/static/javascript/jquery.confirm-1.3.js"/> -->

    <script type="text/javascript">
    $(document).ready(function() {
        $('.progress').text("Invoice processing complete");
        $('.actions').show();
        $('#select_all').click( function () {
            var checked_status = this.checked;
            $("input[name='invoice_ids']").each(function() {
                this.checked = checked_status;
            });
        });                         
        var delete_invoice = function (invoice_id) {
            var invoicebox = $('#invoicebox-' + invoice_id);
            $('#select_' + invoice_id).hide();
            $.post("/remove_invoice/" + invoice_id, {}, function (data) {
                invoicebox.remove();
            });
        };
        $('.remove_selected').click( function () {
            $("input[name='invoice_ids']:checked").each(function() {
                var invoice_id = $(this).attr('id').split('_')[1];
                delete_invoice(invoice_id);
            });
        });
    });
    </script>
</head>

<body>  

<div class="container">
    <div class="progress success span-8 last">processing..</div>
</div>

<div id="status_area container">

<form id="invoice_approval" action="/send_invoices" method="post">

<div class="actions container">
    <div class="span-5">
    <input type="submit" class="send_approved" value="Send selected"/>
    </div>
    <div class="span-5 last">
    <input type="button" class="remove_selected" value="Remove selected"/>
    </div>
</div>
<br/>

<table class="statuses span-15">

<thead>
<tr>
<th></th>
<th class="span-4">To</th>
<th>Created on</th>
<th>Amount</th>
<th>Preview</th>
<th>Message</th>
<th class="span-2 last"><input type="checkbox" id="select_all" checked="checked"/></th>
</tr>
</thead>

</table>

<div class="actions container">
    <div class="span-5">
    <input type="submit" class="send_approved" value="Send selected"/>
    </div>
    <div class="span-5 last">
    <input type="button" class="remove_selected" value="Remove selected"/>
    </div>
</div>

</form>

<div class="preview"/>

<script>
$('.statuses').hide();
$('.actions').hide();

var invoice_preview = function (invoice_id) {
    var url = '/show_invoice/' + invoice_id;
    var html = '<iframe src="' + url + '" width="900" height="900"/>';
    var dialog = $('.preview').html(html).dialog({
        autoOpen: false,
        title: 'Invoice Preview',
        //height: 700,
        width: 880,
        position: 'left'
        });
    dialog.dialog('open');
};
$('.invoice_preview').click( function () {
    var invoice_id = $(this).attr('id').split('-')[1];
    invoice_preview(invoice_id);
});
</script>
</div>


</body>  

</html>  
