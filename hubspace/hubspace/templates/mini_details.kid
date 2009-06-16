<?python?>
<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
	<div class="name">${user.display_name}</div>
	<div class="company">${user.organisation}</div>
	<div class="phone">${user.mobile}</div>
	<div class="email"><a href="mailto:${user.email_address}">${user.email_address}</a></div>
	<div class="www"><a href="${user.website}">${user.website}</a></div>
	<a href="#" onclick="closeDetails()" class="closeDetails">x</a>
</div>

