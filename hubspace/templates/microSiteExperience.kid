<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:py="http://purl.org/kid/ns#" py:extends="'microSiteMaster.kid'">
<head>

</head>
<body id="experience">
        <div class="span-12" id="content-intro">
            <h1 id="title" class="text_small">${page.title and page.title or "The Experience"}</h1>
            <div py:if="page.content" class="text_wysiwyg" id="content">${XML(page.content)}</div>
            <div py:if="not page.content" class="text_wysiwyg" id="content"><p>The Hub Kings Cross is situated in a strikingly elegant listed building on York Way in the heart of Kings Cross. The restoration has seen the fusion of old and new, marrying the original features of the remarkable building with contemporary, striking design to deliver an exciting and stylish finish.</p>
                <p>But the building is only the beginning of the story, it's what's happening inside it that's really exciting.</p>
                <p>During the day, The Hub Kings Cross is a dynamic members space which offers a new way of working and connecting. The traditional sterile office space is replaced with a vibrant flexible hot-desking work space which incorporates a cafe and state of the art meeting rooms. It's a place where social innovators at the forefront of the ethical economy can some to develop their ideas and connect with like-minded souls who share a passion for delivering positive social change.</p>
                <p>During the evening, The Hub Kings Cross transform into London's most innovative event spaces for lectures, debates, dinners and cultural fare, playing host to some of the most imaginative and compelling speakers and facilitators from around the UK and beyond, aligned by their reputation as amazing thinkers and doers and their desire to make the world a radically better place.</p> 
            </div>
        </div>
        <div class="span-12 last">
            <div class="span-12 last content-sub" id="features">
                <h3 id="features_header" class="text_small">${page.features_header and page.features_header or "Features of the Hub Kings Cross"}</h3>
                <div py:if="page.features_body" class="text_wysiwyg" id="features_body">${XML(page.features_body)}</div>
                <div py:if="not page.features_body" class="text_wysiwyg" id="features_body">
                    <ul id="experience">
                        <li id="spaces">inspired spaces for working, meeting and connecting with others</li>
                        <li id="evening">an evening programme of lectures, dinners, cultural events and exhibitions</li>
                        <li id="bar">a bar with a light restaurant</li>
                        <li id="network">a global network of people working at the forefront of the sustainable economy</li>
                        <li id="events">state of the art events space  </li>
                    </ul>
                </div>
            </div>
        </div>
</body>
</html>
