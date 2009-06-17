<?python
    import cherrypy, datetime
    def toPromptToSave():
        return "savedreport" not in cherrypy.request.path.lower()

    def formSaveURL(save_params):
        if not save_params['start']:
            save_params['start'] = 'all'
        if not save_params['end']:
            now = datetime.datetime.now()
            save_params['end'] = now.strftime("%a, %d %B %Y")
        if not save_params['user_id']: save_params['user_id'] = 'all'
        if not save_params['r_name']: save_params['r_name'] = 'all'
        if not save_params['r_type']: save_params['r_type'] = 'all'
        return '/saveUsageReport/%(start)s/%(end)s/%(grpby)s/%(r_name)s/%(r_type)s/%(user_id)s/%(rtype)s' % save_params

?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" xmlns:py="http://purl.org/kid/ns#">
 <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>Resource Usage</title>
    <style type="text/css">@import url(/static/css/main.css);</style>
    <script type="text/javascript" language="javascript">
        var jQuery;
        if ( jQuery == undefined ) {
            var s=document.createElement('script');
            s.setAttribute('src', "/static/javascript/jquery.min.js");
            document.getElementsByTagName('head')[0].appendChild(s); }; 

    </script>
    <script type="text/javascript" src="/static/javascript/jq.noconflict.js"  language="javascript"> </script>
    <script type="text/javascript" src="/static/javascript/jquery.flot.js"  language="javascript"> </script> 
    <!--[if IE]><script language="javascript" type="text/javascript" src="/static/javascript/excanvas.pack.js"></script><![endif]-->
    <script>
        var save_report = function (evt) {
            var url = "${formSaveURL(save_params)}";
            jq.ajax({url: url, success: function(msg){ jq(".saveReport").replaceWith("This report is stored for future reference!"); }
            });
        };
        jq(document).ready(function() {
           jq('.saveReport').click(save_report);
        });

    </script>

 </head>
    <body>
    <h1>$title</h1>
    <h3 py:if="save_params['start'] != 'all'">${"Period: %(start)s - %(end)s" % save_params}</h3>
    <p py:if="toPromptToSave()">
    <a class="saveReport">
    Save parameters for future regeneration of this graph </a>
    </p>
    <table>
    <tr>
        <td>
            $y_label
        </td>
        <td>
        <div id="placeholder" style="width:${x_len}px;height:${y_len}px;"></div>
        </td>
    </tr>
    <tr>
        <td>
        </td>
        <td>
            $x_label
        </td>
    </tr>
    </table>

<script id="source" language="javascript" type="text/javascript">

    var data =  $data_str; 
    jq.plot( jq("#placeholder"), data, $options_str );


</script>

 </body>
</html>
