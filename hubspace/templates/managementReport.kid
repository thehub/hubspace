<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" >
<head>
        <link rel="stylesheet" href="/static/css/micro/blueprint/screen.css" type="text/css" media="screen, projection"/>
    	<link rel="stylesheet" href="/static/css/micro/blueprint/print.css" type="text/css" media="print"/>
   	 <!--[if IE]>
    	<link rel="stylesheet" href="/static/css/micro/blueprint/ie.css" type="text/css" media="screen, projection"/>
    	<![endif]-->
    	<link rel="stylesheet" href="/static/css/micro/blueprint/typography.css" type="text/css" media="print"/>
          
        <!--
        <link rel="stylesheet" href="http://bluetrip.org/sites/bluetrip.org/themes/starkish/demo/css/screen.css" type="text/css" media="screen, projection" /> 
        <link rel="stylesheet" href="http://bluetrip.org/sites/bluetrip.org/themes/starkish/demo/css/print.css" type="text/css" media="print" /> 
        <link rel="stylesheet" href="http://bluetrip.org/sites/bluetrip.org/themes/starkish/demo/css/style.css" type="text/css" media="screen, projection" /> 
        -->

</head>

<body style="width:${len(locations) * 450}px">  

<table border="1">
<tr>
<?python
from hubspace.model import Location
?>
<td py:for="loc in locations" width="470px"><h2>Hub ${Location.get(loc).name}</h2><em>${start.strftime ("%b %d %Y")} - ${end.strftime ("%b %d %Y")}</em></td>
</tr>
<tr py:if="'member_summary' in report_types" title="Member Summary">
    <td py:for="loc in locations" >
        <table >
         <caption>Member Summary</caption>
           <?python
           from decimal import Decimal, getcontext, Context, Inexact
           active_members = report[loc]['member_summary']['loc_members_active']
           not_active_members = report[loc]['member_summary']['loc_members_not_active']
           perc_active_members = Decimal(str(100 * (float(active_members) / report[loc]['member_summary']['total_members_active']))).quantize(Decimal('0.01'))
           new_members = report[loc]['member_summary']['new_members']
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
        </table>
    </td>
</tr>
<tr py:if="'revenue_summary' in report_types" title="Revenue Summary">
    <td py:for="loc in locations">
        <table>
           <?python
           invoiced, uninvoiced, total, currency = report[loc]['revenue_summary']
           ?>
         <caption class="thin">Revenue Summary (<em> ${currency} </em>)</caption>
            <tr> <td>Invoiced:</td> <td> ${invoiced}</td> </tr>
            <tr> <td>Not Invoiced:</td> <td> ${uninvoiced}</td> </tr>
            <tr> <td>Total:</td> <td> ${total}</td> </tr>
        </table>
    </td>
</tr>
<div py:if="'revenue_by_resourcetype' in report_types">
    <tr> <td py:for="loc in report"><h3>Revenue by Resource types</h3></td> </tr>
    <tr> <td py:for="loc in report"><img src="/report_image/${report[loc]['revenue_by_resourcetype']}" /> </td> </tr>
</div>
<div py:if="'revenue_by_resource' in report_types">
    <tr> <td py:for="loc in report"><h3>Revenue by Resource </h3></td> </tr>
    <tr> <td py:for="loc in report"><img src="/report_image/${report[loc]['revenue_by_resource']}" /> </td> </tr>
</div>
<div py:if="'revenue_stats' in report_types">
    <tr> <td py:for="loc in report"><h3>Revenue Report</h3></td> </tr>
    <tr> <td py:for="loc in report"><img src="/report_image/${report[loc]['revenue_stats']}"/> </td></tr>
</div>
<div py:if="'churn_stats' in report_types">
    <tr> <td py:for="loc in report"><h3>Churn Rate</h3></td> </tr>
    <tr> <td py:for="loc in report"><img src="/report_image/${report[loc]['churn_stats']}"/> </td></tr>
</div>
<div py:if="'members_by_tariff' in report_types">
    <tr> <td py:for="loc in report"><h3>Members on Tariffs</h3></td> </tr>
    <tr> <td py:for="loc in report"><img src="/report_image/${report[loc]['members_by_tariff']}" /> </td> </tr> 
</div>
<div py:if="'revenue_by_tariff' in report_types">
    <tr> <td py:for="loc in report"><h3>Revenue by Tariffs</h3></td> </tr>
    <tr> <td py:for="loc in report"><img src="/report_image/${report[loc]['revenue_by_tariff']}"/> </td> </tr>
</div>
<div py:if="'usage_by_tariff' in report_types">
    <tr> <td py:for="loc in report"><h3>Usage by Tariffs</h3></td> </tr>
    <tr> <td py:for="loc in report">
        <table>
        <tr py:for="r_type, imgpath in report[loc]['usage_by_tariff']">
            <td> <h4> Usage by Tariffs: ${r_type} </h4> <br/> <img src="/report_image/${imgpath}"/></td>
        </tr>
        </table>
        </td>
    </tr>
</div>
</table>
</body>

</html>
