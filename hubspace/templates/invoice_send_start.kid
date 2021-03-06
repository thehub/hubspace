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
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/jquery-ui.min.js"></script>

</head>

<body>  

<script>
var invoice_preview = function (invoice_id) {
    var url = '/show_invoice/' + invoice_id;
    var html = '<iframe src="' + url + '" width="900" height="900"/>';
    var dialog = $('.preview').html(html).dialog({
        autoOpen: false,
        title: 'Invoice Preview',
        //height: 700,
        width: 880,
        position: 'top'
        });
    dialog.dialog('open');
};
$('.invoice_preview').click( function () {
    var invoice_id = $(this).attr('id').split('-')[1];
    invoice_preview(invoice_id);
});
</script>

<div id="status_area">

<table class="statuses container">

<thead>
<tr>
<th></th>
<th class="span-5">To</th>
<th>Number</th>
<th>Amount</th>
<th>Preview</th>
<th>Status</th>
</tr>
</thead>

</table>
</div>

<div class="preview"/>

</body>  
</html>  
