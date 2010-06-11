<?python
from hubspace.utilities.image_helpers import image_src
from docutils.core import publish_parts
from hubspace.utilities.uiutils import get_freetext_metadata
from hubspace.utilities.uiutils import sanitize_input
user = None
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>
</head>
<body id="members">
    <div py:if="not user" class="span-12" id="content-intro">
       <h1 id="title" class="text_small">${page.title and page.title or "Our Members"}</h1>
       <div py:if="page.content" class="text_wysiwyg" id="content">${XML(page.content)}</div> 
       <div id="content" py:if="not page.content" class="text_wysiwyg">
          <p><strong>Social Innovators from within and beyond the public, private and third sectors are establishing a new form of commerce for the 21st Century. The Hub Kings Cross is becoming the place they call home.</strong></p>
          <p>Our members are what make the Hub. So we take care to ensure that we have a diverse membership mix representing an array of sectors, industries and professions. What unites our membership is a passion to make a positive difference, with a strong motivation to deliver enterprising solutions that provide social and environmental as well as economic value.</p>
          <p>If you were to drop into a Hub today, these are some of the people you might bump into:</p>
          <ul>
            <li>John Bird - Founder of the Big Issus</li>
            <li>Liam Black - Co-founder of Fifteen</li>
            <li>Lisa Stockton - Co-founder Happy Kitchen</li>
            <li>Dominic Campbell - Co-founder Enabled by Design</li>
            <li>Lawrence Corbett - CEO Virgin Unite</li>
            <li>Justin Dekoszmovszky - SC Johnson</li>
            <li>Grant Lang - Founder, Mozzo coffee</li>
          </ul>
       </div>
    </div>
    <div py:if="user" class="span-12">
	<div id="hubHomeContent" class="clearfix">
		<div id="main" class=" content-sub">
                    <div class="update_item" id="pub_profile">
			<h3 class="text_small">${user.display_name}</h3>
                        <div class="profileTop">
                          <img class="profileimg" src="${image_src(user, 'image', '/static/images/shadow.png')}" />                          
                          <div class="profileDetails">
                               <div py:if="user.organisation" class="property"><div class="propertyTitle">Organisation:</div>
							   <div class="propertyValue"> ${user.organisation}</div></div>
                               <div py:if="get_freetext_metadata(user, 'biz_type')" class="property"><div class="propertyTitle">Type of Business:</div><div class="propertyValue"> ${get_freetext_metadata(user, 'biz_type')}</div>
                               </div>
                          </div>
                        </div>
                            <?python
                                description = user.description
                                if '<br>' in description or '<br >' in description or '</b>' in description or '</div>' in description or '</p>' in description:
                                    content = sanitize_input(description)
                                else:
                                    content = publish_parts(description, writer_name="html")["html_body"]
                            ?>
                            ${XML(content)}
				<a class="backLink" href="../members.html">back to Members Page</a><br clear="all" />
                     </div>
		</div>
	</div>
    </div>  
    <div class="span-12 last">
        <div class="span-12 last content-sub" id="recent-profiles">
            <h3 id="profiles_header" class="text_small">${page.profiles_header and page.profiles_header or "Recently Updated Profiles"}</h3>
				<ul id="members-profiles">
				  <li class="member" py:for="member in profiles">
                                      <a href="${relative_path}members/${member.user_name}" title="Click for full bio">
				      <span><img class="profileimg" src="${image_src(member, 'image', '/static/images/shadow.png')}"/></span>
				      <span class="member-name">${member.display_name}</span>
				      <span class="member-company">${member.organisation}</span>
					</a>
				  </li>
				</ul>
		</div>
		<div id="rss"><a href="/feed/rss2_0/profiles/${location.id}"><img src="/static/images/micro/page/rss-icon.gif" alt="rss feed" /></a></div>
    </div>
</body>
</html>











