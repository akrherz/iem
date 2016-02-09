"""Script fetches openauth2 refresh token that my offline scripts can use
"""
from gdata import gauth
import pyiem.cscap_utils as util

config = util.get_config()

token = gauth.OAuth2Token(client_id=config['appauth']['client_id'],
                          client_secret=config['appauth']['app_secret'],
                          scope=config['googleauth']['scopes'],
                          user_agent='daryl.testing',
                          access_token=config['googleauth']['access_token'],
                          refresh_token=config['googleauth']['refresh_token'])

print "Go to this URL:", token.generate_authorize_url()
code = raw_input('What is the verification code? (auth_token)').strip()
token.get_access_token(code)
print "refresh_token is", token.refresh_token
config['googleauth']['refresh_token'] = token.refresh_token
util.save_config(config)
print "Saved configuration to file..."
