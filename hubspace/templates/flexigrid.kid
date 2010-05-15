<?python
from hubspace.utilities.users import fields as user_fields

def_col_width = 120

def getGridParams(location, usercols_selection=[]):
    if usercols_selection:
        colModel = [dict(display=str(v['label']),name=str(k),sortable="true",width=def_col_width) for (k,v) in user_fields.items() if k in usercols_selection]
    else:
        colModel = [dict(display=v['label'],name=k,sortable="true",width=150) for (k,v) in user_fields.items()]
    colModel = str(colModel)

    url = "/export_users_json?" + "location=%s&" % location +  "&".join(["%s=%s" % (c,c) for c in usercols_selection])
    width = (len(usercols_selection) * def_col_width) + 50
    height = 500

    return colModel, url, height, width
?>

<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" xmlns:py="http://purl.org/kid/ns#">
 <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <link rel='stylesheet' type='text/css' href='/static/javascript/flexigrid/css/flexigrid/flexigrid.css' />
 </head>

<body>
<?python
    colModel, url, height, width = getGridParams(location, usercols_selection)
?>

<script type="text/javascript">
  jq("#flex1").flexigrid (
    {
    url: "$url" , 
    dataType: 'json',
    colModel : $colModel,
    // searchitems : [
    //   {display: 'First Name', name : 'first_name'},
    //   {display: 'Last Name', name : 'last_name'},
    // ],
    // buttons : [
    //             {name: 'Add', bclass: 'add', onpress : test},
    //             {name: 'Delete', bclass: 'delete', onpress : test},
    //             {separator: true}
    //           ],

    sortname: "$sortname",
    // sortorder: "asc",
    usepager: true,
    title: 'Users Data',
    useRp: true,
    rp: 50,
    showTableToggleBtn: true,
    width: $width,
    height: $height,
    striped: false,
    }
  );
</script>

 </body>
</html>
