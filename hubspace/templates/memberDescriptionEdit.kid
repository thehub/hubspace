<?python
if 'tg_errors' not in locals():
    tg_errors = None
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
    <div py:def="load_memberDescriptionEdit(object, tg_errors)" class="dataBoxContent">
	<div class="dataTextBox data">
		<p>Please tell other Hub members about yourself and the projects you work on. <br />What interests you?<br /> What skills and services would you like to offer other members?</p>
	<textarea name="description" id="description">${object.description}</textarea>
	</div>
    </div>
    ${load_memberDescriptionEdit(object, tg_errors=tg_errors)}
</div>
