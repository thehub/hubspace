<?python
relative_path = '/'
height = None
width = None
page_name = None
?>
<div py:strip="True" xmlns:py="http://purl.org/kid/ns#">
<div style="width:850px;background-color:#ffffff;">
<form action='${relative_path}uploadImage/${id}/${type}/${attr}' enctype="multipart/form-data"  method="POST">
<div py:if="height or width">Images will be cropped to <c py:if="width" py:strip="True">a width of ${width}px</c><c py:if="width and height" py:strip="True"> and</c> <c py:if="height" py:strip="True">a height of ${height}px - for best results upload an image of these proportions</c></div>
<input py:if="width" name="width" type="hidden" value="${width}"  />
<input py:if="height" name="height" type="hidden" value="${height}"  /><br />
<input py:if="page_name" name="page_name" type="hidden" value="${page_name}"  /><br />
<input name="image" type="file" id="auto_browse" />
<input style="display:none;" value="submit" id="submit_iframe" type='submit' />
<input value="cancel" id="cancel_iframe" type='button' />
</form>
</div>
</div>
