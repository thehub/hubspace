<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" >
<head>
        <link rel="stylesheet" href="/static/css/micro/blueprint/screen.css" type="text/css" media="screen, projection, print"/>
   	 <!--[if IE]>
    	<link rel="stylesheet" href="/static/css/micro/blueprint/ie.css" type="text/css" media="screen, projection"/>
    	<![endif]-->
    	<link rel="stylesheet" href="/static/css/micro/blueprint/typography.css" type="text/css" media="screen, projection, print"/>
    	<link rel="stylesheet" href="/static/css/micro/blueprint/print.css" type="text/css" media="print"/>
        
        <STYLE type="text/css" media="print">
        .dontprint {
            display: none;
        }
        </STYLE>
        <STYLE type="text/css" media="screen">
        .clicker {
	    font-size:95%;
	    padding:1px;
	    font-family:helvetica, arial, verdana, sans-serif;
	    margin:1;
	    border: 1px solid #3F3F3F;
            cursor:pointer;
            text-decoration: none;
        }
        </STYLE>
          
        <script type="text/javascript" src="/static/javascript/jquery.min.js"></script>

</head>

<body style="width:${len(stats) * 550}px">  
<?python
locs = sorted(stats)
switch_graph_label = "Switch to Graph view"
switch_table_label = "Switch to Table view"
?>
<table border="1">
<tr>
<td py:for="loc in locs" ><h1>${loc}</h1><em>${start.strftime ("%b %d %Y")} - ${end.strftime ("%b %d %Y")}</em></td>
</tr>
<tr py:if="'summary' in report_types" title="Dashboard">
    <td py:for="loc in locs" >
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
    <tr><td py:for="loc in locs"> 
        <?python
        loc_id = loc.replace(' ','_')
        report = stats[loc][report_type]
        nodata = not any(row[1] for row in stats[loc][report_type].data[0][1])
        title = "Revenue Stats"
        ?>
        <h3>${title}</h3>
        <div py:if="nodata">No Data</div>
        <div py:if="not nodata">

        <div class="dontprint">
        <a id="toggle-${report_type}-${loc_id}" class="toggle-${report_type} clicker">${switch_table_label}</a>
        </div>

        <table id="table-${report_type}-${loc_id}" class="table-${report_type}">
        <caption>${title}</caption>
        <tr>
            <th>Month</th>
            <th>Revenue</th>
        </tr>
        <tr py:for="row in report.data[0][1]">
            <th>${report.options['axis']['x']['ticks'][row[0]]['label']}</th> 
            <td>${row[1]}</td>
        </tr>
        </table>
        <img class="canvas-${report_type}" id="canvas-${report_type}-${loc_id}" src="/report_image/${report.draw_vbars_chart()}"/>

        </div>

        </td>
        ${script_toggle_switch(report_type)}
        </tr>
</div>

<div py:def="script_toggle_switch(report_type)">
<?python
switch_graph_label = '"Switch to Graph view"'
switch_table_label = '"Switch to Table view"'
?>
    <script>
    $('.table-${report_type}').hide();
    $('.canvas-${report_type}').show();
    $('.toggle-${report_type}').click( function () {
        // alert($(this).text());
        if ($(this).text() == ${switch_graph_label}) {
            $('.table-${report_type}').hide();
            $('.canvas-${report_type}').show();
            $('.toggle-${report_type}').text(${switch_table_label}); }
        else {
            $('.table-${report_type}').show();
            $('.canvas-${report_type}').hide();
            $('.toggle-${report_type}').text(${switch_graph_label}); }
        });
    </script>
</div>

<div py:def="draw_pies(stats, report_type, title=None)">
<div py:if="report_type in report_types">
    <tr> <td py:for="loc in sorted(stats)"> 
        <?python
        title = title or report_type.replace('_', " ").title()
        loc_id = loc.replace(' ','_')
        report = stats[loc][report_type]
        nodata = not bool(report.data and any(x[1][0][1] for x in report.data))
        switch_graph_label = "Switch to Graph view"
        switch_table_label = "Switch to Table view"
        ?>
        <h3>${title}</h3>

        <div py:if="nodata">No Data</div>
        <div py:if="not nodata">

        <div class="dontprint">
        <a id="toggle-${report_type}-${loc_id}" class="toggle-${report_type} clicker ">${switch_table_label}</a>
        </div>

        <br/>
        <table class="table-${report_type}" id="table-${report_type}-${loc_id}">
        <caption>${title}</caption>
        <tr py:for="res_name, revenue in report.data">
            <th>${res_name}</th>
            <td>${revenue[0][1]}</td>
        </tr>
        </table>

        <img class="canvas-${report_type}" id="canvas-${report_type}-${loc_id}" src="/report_image/${report.draw_pie_chart()}"/>

        </div>

        </td>
        ${script_toggle_switch(report_type)}
        </tr>

</div>
</div>

${draw_pies(stats, "revenue_by_resourcetype")}
${draw_pies(stats, "revenue_by_resource")}

<?python
report_type = 'churn_stats'
?>
<div py:if="report_type in report_types and stats[loc][report_type]">
    <tr> <td py:for="loc in locs"> 
        <?python
        loc_id = loc.replace(' ','_')
        report = stats[loc][report_type]
        data = report.data
        nodata = not any(row[1][0][1] and row[1][1][1] for row in report.data)
        ?>
        <h3>Churn Rate</h3>

        <div py:if="nodata">No Data</div>
        <div py:if="not nodata">

        <div class="dontprint">
        <a id="toggle-${report_type}-${loc_id}" class="toggle-${report_type} clicker ">${switch_table_label}</a>
        </div>

        <br/>
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
        </div>
        </td>
    ${script_toggle_switch(report_type)}
    </tr>
</div>

${draw_pies(stats, "members_by_tariff")}
${draw_pies(stats, "revenue_by_tariff")}

<div py:if="'usage_by_tariff' in report_types">
<?python
report_type = 'usage_by_tariff'
?>
<tr>
    <td py:for="loc in locs" style="vertical-align:top"> 
    <table>
    <tr py:for="resource_type in sorted(stats[loc][report_type])">
        <td>
        <?python
        loc_id = loc.replace(' ','_')
        report = stats[loc][report_type][resource_type]
        table_cls = "table-%s-%s" % (report_type, resource_type)
        table_id = table_cls + loc_id
        canvas_cls = "canvas-%s-%s" % (report_type, resource_type)
        canvas_id = canvas_cls + loc_id
        toggle_cls = "toggle-%s-%s" % (report_type, resource_type)
        toggle_id = toggle_cls + loc_id
        nodata = not bool(report.data)
        title = "Usage By Tariff (%s)" % resource_type
        ?>
        <h3>${title}</h3>

        <div py:if="nodata">No Data</div>
        <div py:if="not nodata">

        <div class="dontprint">
        <a id="${toggle_id}" class="${toggle_cls} clicker ">${switch_table_label}</a>
        </div>

        <table id="${table_id}" class="${table_cls}">
        <caption>${title}</caption>
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

        </div>
        </td>
        ${script_toggle_switch(report_type + '-' + resource_type)}

    </tr>
    </table>
    </td>
</tr>
</div>

</table>
</body>

</html>
