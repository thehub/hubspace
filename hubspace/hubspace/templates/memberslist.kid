<?python
from hubspace.utilities.uiutils import oddOrEven, get_multiselected, all_hosts
from hubspace.model import User
from sqlobject import AND
oddness = oddOrEven()
from turbogears import identity


class Color(object):
    def __init__(self):
        self.all_hosts = all_hosts()
        self.user = identity.current.user
        self.inactive()
        self.host_managed()

    def color(self, member):
        highlight_class = self.highlighted(member)
        if highlight_class:
            return highlight_class
        return oddness.odd_or_even()

    def highlighted(self, member):
        className = ""
        if member in self.managed:
            className += "host_managed "
        if member in self.inactive_users:
            className += "inactive"
        return className

    def inactive(self):
        inactive_users = User.select(AND(User.q.active==0))
        if self.user in self.all_hosts:
            self.inactive_users = [mem for mem in inactive_users]
        else:
            self.inactive_users = []

    def host_managed(self):
        if self.user in self.all_hosts:
            self.managed = [mem for mem in User.select(AND(User.q.hostcontactID==self.user.id))]
        else:
            self.managed = []
?>

   <ul id="memberList" xmlns:py="http://purl.org/kid/ns#" py:strip="True">
      <c py:strip="True" py:def="member_list(members)">

          <?python
              coloration = Color()
          ?>
          <li py:for="member in members" class="${coloration.highlighted(member)}"><a style="cursor:pointer;" class="box" id="box-${member.id}"><img src="/static/images/memberDetailBox.gif" alt="display quick member details" /></a><a style="cursor:pointer;" class="load_user" id="user-${member.id}">${member.display_name.strip() or "No Name"}</a></li>

      </c>
      ${member_list(members)}
   </ul>

