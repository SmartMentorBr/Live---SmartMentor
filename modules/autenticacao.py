from gluon.http import HTTP
from gluon.contrib.login_methods.oauth20_account import OAuthAccount

import hashlib
import random
from gluon import current

try:
    from linkedin.linkedin import LinkedInApplication
except ImportError:
    raise HTTP(400, "linkedin module not found")


LK_KEY = '78sv675i7fub3q'
LK_SECRET = '3o6DnEbVprdNhBmP'
LK_RETURN_URL = current.url_linkedin

class LinkedInAccount(OAuthAccount):
    TOKEN_URL="https://www.linkedin.com/uas/oauth2/accessToken"
    AUTH_URL="https://www.linkedin.com/uas/oauth2/authorization"
 
    def __init__(self):
        OAuthAccount.__init__(self, 'linkedin', LK_KEY, LK_SECRET,
                              self.AUTH_URL, self.TOKEN_URL,
                              scope='r_emailaddress',
                              state=self._make_new_state())
 
    def _make_new_state(self):
        return hashlib.md5(
            '%s%s' % (random.randrange(0, 2 ** 63), LK_SECRET)).hexdigest()
 
    def get_user(self):
        if not self.accessToken():
            return None
        app = LinkedInApplication(token=self.accessToken())
        profile = app.get_profile(selectors=['firstName', 'lastName', 'pictureUrl','emailAddress'])

        return dict(
            first_name = profile['firstName'],
            last_name=profile['lastName'],
            avatar_linkedin=profile['pictureUrl'],
            email = profile['emailAddress']
        )
