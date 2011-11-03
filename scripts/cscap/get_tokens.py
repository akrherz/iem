"""
Need something to get access tokens when my old ones go stale
$Id$:
"""
import gdata.sites.client
from gdata import gauth
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

"""
These are the scopes my app needs access to, if I change
this, I need to re-request tokens!
"""
SCOPES = [
          'https://sites.google.com/feeds/',
          'https://spreadsheets.google.com/feeds/',
          ]

token = gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                                client_secret=config.get('appauth', 'app_secret'),
                                scope=' '.join(SCOPES),
                                user_agent='daryl.testing',
                                access_token=config.get('googleauth', 'access_token'),
                                refresh_token=config.get('googleauth', 'refresh_token'))

print "Go to this URL:", token.generate_authorize_url()
code = raw_input('What is the verification code? (auth_token)').strip()
token.get_access_token(code)
print "refresh_token is", token.refresh_token