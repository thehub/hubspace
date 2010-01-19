<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" >
<head>
        <link rel="stylesheet" href="/static/css/micro/blueprint/screen.css" type="text/css" media="screen, projection, print"/>
    	<link rel="stylesheet" href="/static/css/micro/blueprint/print.css" type="text/css" media="print"/>
   	 <!--[if IE]>
    	<link rel="stylesheet" href="/static/css/micro/blueprint/ie.css" type="text/css" media="screen, projection"/>
    	<![endif]-->
    	<link rel="stylesheet" href="/static/css/micro/blueprint/typography.css" type="text/css" media="print"/>
          
        <script type="text/javascript" src="/static/javascript/jquery.min.js"></script>

</head>

<body style="width:${len(stats) * 550}px">  
<table border="1">
<?python
def_height = 700 if len(stats) == 1 else 600
def_width = 600 if len(stats) == 1 else 550
import hubspace.reportutils as reportutils
?>
<tr>
<td py:for="loc in stats" ><h1>Hub ${loc}</h1><em>${start.strftime ("%b %d %Y")} - ${end.strftime ("%b %d %Y")}</em></td>
</tr>
<tr py:if="'summary' in report_types" title="Dashboard">
    <td py:for="loc in stats" >
        <table >
         <caption>Dashboard</caption>
           <?python
           from decimal import Decimal
           data = stats[loc]['summary']
           active_members = data['loc_members_active']
           not_active_members = data['loc_members_not_active']
           perc_active_members = Decimal(str(100 * (float(active_members) / data['total_members_active']))).quantize(Decimal('0.01'))
           new_members = data['new_members']
           revenue = data['revenue']
           currency = data['currency']
           ?>
            <tr>
                <td>Active members:</td> <td>${active_members} <em>(${perc_active_members} % across locations)</em></td>
            </tr>
            <tr>
                <td>Not Active members:</td> <td>${not_active_members}</td>
            </tr>
            <tr>
                <td>New members:</td> <td>${new_members}</td>
            </tr>
            <tr> <td>Revenue:</td> <td> ${revenue}</td> </tr>
            <tr> <td>Currency:</td> <td> ${currency}</td> </tr>
        </table>
    </td>
</tr>

<?python
report_type = 'revenue_stats'
?>
<div py:if="report_type in report_types">
    <tr> <td py:for="loc in stats"> 
        <?python
        loc_id = loc.replace(' ','_')
        report = stats[loc][report_type]
        data = report.data
        report.data = [report.data]
        ?>
        <label for="toggle-${report_type}-${loc_id}">Visualize</label>
        <input type="checkbox" id="toggle-${report_type}-${loc_id}" class="toggle-${report_type}" checked="checked"/>
        <table id="table-${report_type}-${loc_id}" class="table-${report_type}">
        <caption>${report.options['title']}</caption>
        <tr>
            <th>Month</th>
            <th>Revenue</th>
        </tr>
        <tr py:for="row in data[1]">
            <th>${report.options['axis']['x']['ticks'][row[0]]['label']}</th> 
            <td>${row[1]}</td>
        </tr>
        </table>
        <img class="canvas-${report_type}" id="canvas-${report_type}-${loc_id}" src="/report_image/${report.draw_vbars_chart()}"/>
        <script>
        $('.table-${report_type}').hide();
        $('.canvas-${report_type}').show();
        $('.toggle-${report_type}').click( function () {
            if ($(this).attr('checked')) {
                $('.table-${report_type}').hide();
                $('.canvas-${report_type}').show(); }
            else {
                $('.table-${report_type}').show();
                $('.canvas-${report_type}').hide(); }
            });
        </script>

    </td></tr>
</div>

<div py:def="draw_pies(stats, report_type, def_width=500, def_height=550, title=None)">
<div py:if="report_type in report_types">
    <tr> <td py:for="loc in stats"> 
        <?python
        title = title or report_type.replace('_', " ").capitalize()
        loc_id = loc.replace(' ','_')
        report = stats[loc][report_type]
        report.data = tuple(report.data)
        ?>
        <label for="toggle-${report_type}-${loc_id}">Visualize</label>
        <input type="checkbox" id="toggle-${report_type}-${loc_id}" class="toggle-${report_type}" checked="checked"/>

        <table class="table-${report_type}" id="table-${report_type}-${loc_id}">
        <caption>${title}</caption>
        <tr py:for="res_name, revenue in report.data">
            <th>${res_name}</th>
            <td>${revenue[0][1]}</td>
        </tr>
        </table>

        <img class="canvas-${report_type}" id="canvas-${report_type}-${loc_id}" src="/report_image/${report.draw_pie_chart()}"/>

        <script>
        $('.table-${report_type}').hide();
        $('.canvas-${report_type}').show();
        $('.toggle-${report_type}').click( function () {
            if ($(this).attr('checked')) {
                $('.table-${report_type}').hide();
                $('.canvas-${report_type}').show(); }
            else {
                $('.table-${report_type}').show();
                $('.canvas-${report_type}').hide(); }
            });
        </script>

    </td></tr>
</div>
</div>

${draw_pies(stats, "revenue_by_resourcetype", def_width, def_height)}
${draw_pies(stats, "revenue_by_resource", def_width, def_height)}

<?python
report_type = 'churn_stats'
?>
<div py:if="report_type in report_types">
    <tr> <td py:for="loc in stats"> 
        <?python
        loc_id = loc.replace(' ','_')
        report = stats[loc][report_type]
        data = report.data
        ?>
        <label for="toggle-${report_type}-${loc_id}">Visualize</label>
        <input type="checkbox" id="toggle-${report_type}-${loc_id}" class="toggle-${report_type}" checked="checked"/>
        <table id="table-${report_type}-${loc_id}" class="table-${report_type}">
        <caption>Churn Rate</caption>
        <tr>
            <th></th>
            <th>Members left</th>
            <th>Members came back</th>
        </tr>
        <tr py:for="row in data">
            <th>${row[0]}</th> 
            <td>${row[1][0][1]}</td>
            <td>${row[1][1][1]}</td>
        </tr>
        </table>
        <img class="canvas-${report_type}" id="canvas-${report_type}-${loc_id}" src="/report_image/${report.draw_multiline_chart()}"/>

        <script>
        $('.table-${report_type}').hide();
        $('.canvas-${report_type}').show();
        $('.toggle-${report_type}').click( function () {
            if ($(this).attr('checked')) {
                $('.table-${report_type}').hide();
                $('.canvas-${report_type}').show(); }
            else {
                $('.table-${report_type}').show();
                $('.canvas-${report_type}').hide(); }
            });
        </script>

    </td></tr>
</div>

${draw_pies(stats, "members_by_tariff", def_width, def_height)}
${draw_pies(stats, "revenue_by_tariff", def_width, def_height)}

<div py:if="'usage_by_tariff' in report_types">
<?python
report_type = 'usage_by_tariff'
resource_types = stats[loc][report_type].keys()
?>
    <tr py:for="resource_type in resource_types">
    <td py:for="loc in stats"> 
        <?python
        loc_id = loc.replace(' ','_')
        report = stats[loc][report_type][resource_type]
        table_cls = "table-%s-%s" % (report_type, resource_type)
        table_id = table_cls + loc_id
        canvas_cls = "canvas-%s-%s" % (report_type, resource_type)
        canvas_id = canvas_cls + loc_id
        toggle_cls = "toggle-%s-%s" % (report_type, resource_type)
        toggle_id = toggle_cls + loc_id
        ?>
        <label for="${toggle_id}">Visualize</label>
        <input type="checkbox" id="${toggle_id}" class="${toggle_cls}" checked="checked"/>

        <table id="${table_id}" class="${table_cls}">
        <caption>${report.options['title']}</caption>
        <tr>
            <th></th>
            <th py:for="tick in report.options['axis']['x']['ticks']">${tick['label']}</th>
        </tr>
        <tr py:for="res,t_data in report.data">
            <td>${res}</td>
            <td py:for="cell in t_data">${cell[1]}</td>
        </tr>
       </table>

        <img class="${canvas_cls}" id="${canvas_id}" src="/report_image/${report.draw_hsbars_chart()}" />
        </td>
        <script>
        $('.${table_cls}').hide();
        $('.${canvas_cls}').show();
        $('.${toggle_cls}').click( function () {
            if ($(this).attr('checked')) {
                $('.${table_cls}').hide();
                $('.${canvas_cls}').show(); }
            else {
                $('.${table_cls}').show();
                $('.${canvas_cls}').hide(); }
            });
        </script>
    </tr>
</div>
</table>
</body>

</html>
