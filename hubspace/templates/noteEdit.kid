
<?python
from hubspace.utilities.uiutils import print_error
if 'tg_errors' not in locals():
    tg_errors = None
?>
<div xmlns:py="http://purl.org/kid/ns#"  py:strip="True">
  <div py:def="edit(note, tg_errors)">
    <div class="noteHeader">Name of note: <input type="text" name="title" id="title" value="${note.title}" /><div class="errorMessage" py:if="tg_errors">${print_error('title', tg_errors)}</div></div>
    <div class="noteBody">
      <textarea name="body" id="body">${note.body}</textarea>
<div class="errorMessage" py:if="tg_errors">${print_error('body', tg_errors)}</div>
    </div>
  </div>
  ${edit(object, tg_errors=tg_errors)}
</div>
