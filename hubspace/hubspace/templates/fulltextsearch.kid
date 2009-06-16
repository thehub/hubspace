<?python
from hubspace.utilities.uiutils import get_freetext_metadata
def user_link(user, subsection=''):
    if not subsection:
       return "/members/" + user.user_name
    return "/members/" + user.user_name + "/" + subsection 
?>

<div xmlns:py="http://purl.org/kid/ns#" py:strip="True">
    <h1>Search</h1>
    <div class="dataBoxHeader">
           <a class="title" id="link_search_results"><h2>Search Results</h2></a>
    </div>
    <div class="dataBoxContent" id="fulltextSearch">
    <p py:if="len(results)==0 and query">
        Sorry, no users matched 
        "<span py:replace="query">Query goes here</span>".
    </p>
    <ul py:if="len(list(results))" id="results">
        <li py:for="user in results" py:if="user">
            <div>
                <a href="${user_link(user, 'subsection' in locals() and subsection or '')}" class="user_link" id="user-${user.id}" py:content="user.display_name">display name</a>
            </div>
            <div class="description"><span>Organisation: </span><span py:content="user.organisation or 'unknown'"> </span></div>
            <div class="description"><span>Business Type: </span><span py:content="get_freetext_metadata(user, 'biz_type') or 'unknown'"> </span></div>

        </li>
    </ul>
    </div>
</div>
