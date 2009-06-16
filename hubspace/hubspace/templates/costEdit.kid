
<?python
from hubspace.utilities.uiutils import print_error
tg_errors = None
from hubspace.utilities.uiutils import c2s
def cost(rusage):
   try:
      return c2s([rusage.customcost,rusage.cost][rusage.customcost == None])
   except:
      return rusage.customcost
?>
<div xmlns:py="http://purl.org/kid/ns#"  py:strip="True">
  <div py:def="edit(rusage, tg_errors)">
      <input name="customcost" value="${cost(rusage)}" />
      <div class="errorMessage" py:if="tg_errors">${print_error('customcost', tg_errors)}</div>
  </div>
  ${edit(object, tg_errors=tg_errors)}
</div>
