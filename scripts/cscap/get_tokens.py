"""
Need something to get access tokens when my old ones go stale
$Id: get_tokens.py 7798 2011-11-04 19:45:55Z akrherz $:
"""
from gdata import gauth
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

token = gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                                client_secret=config.get('appauth', 'app_secret'),
                                scope=config.get('googleauth', 'scopes'),
                                user_agent='daryl.testing',
                                access_token=config.get('googleauth', 'access_token'),
                                refresh_token=config.get('googleauth', 'refresh_token'))

print "Go to this URL:", token.generate_authorize_url()
code = raw_input('What is the verification code? (auth_token)').strip()
token.get_access_token(code)
print "refresh_token is", token.refresh_token