<?python
relative_path = '/'
height = None
width = None
page_name = None
?>
<div py:strip="True" xmlns:py="http://purl.org/kid/ns#">
<div style="width:850px;">
<form action='${relative_path}uploadImage/${id}/${type}/${attr}' enctype="multipart/form-data"  method="POST">
<div py:if="height and width">Images will be cropped to ${width}px by ${height}px - for best results upload and image of these proportions</div>
<input py:if="width" name="width" type="hidden" value="${width}"  />
<input py:if="height" name="height" type="hidden" value="${height}"  /><br />
<input py:if="page_name" name="page_name" type="hidden" value="${page_name}"  /><br />
<input name="image" type="file" id="auto_browse" />
<input value="submit" id="submit_iframe" type='submit' />
<input value="cancel" id="cancel_iframe" type='button' />
</form>
</div>
</div>
