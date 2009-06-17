<?python?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">

     <div py:def="load_memberCommunities(object)" py:strip="True">
		<li py:for="cop in object.cops" py:if="cop[1]">${cop[0]}</li>
     </div>
 ${load_memberCommunities(object)}
</div>
