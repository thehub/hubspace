<?python
def next_cop(object, cop):
    try:
        return object.cops[object.cops.index(cop)+1]
    except:
        return None
def checked(cop):
    if cop[1] ==1: 
        return {'checked':'checked'}
    else:
        return {}
?>
<div py:strip="True" xmlns:py="http://purl.org/kid/ns#">
   <div py:def="load_memberCommunitiesEdit(object)" class="dataBoxContent">
        <p>Knowledge clusters are communities of people who share similiar interests, practices and questions. Which of these email groups would you like to participate in?</p>
	<table class="copTable data" cellpadding="" cellspacing="0">
		<tr py:for="cop in object.cops" py:if="object.cops.index(cop)%2==0">
			<td><input type="checkbox" name="${cop[0]}" py:attrs="checked(cop)" value="1" /></td>
			<td>${cop[0]}</td>
			<td py:if="next_cop(object, cop)"><input type="checkbox" name="${next_cop(object, cop)[0]}" py:attrs="checked(next_cop(object,cop))" value="1" /></td>
			<td py:if="next_cop(object, cop)">${next_cop(object, cop)[0]}</td>
		</tr>
	</table>
   </div>
 ${load_memberCommunitiesEdit(object)}
</div>
