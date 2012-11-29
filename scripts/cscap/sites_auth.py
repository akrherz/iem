import gdata.sites.client
import time
import gdata.gauth

token = gdata.gauth.OAuth2Token(client_id='992627006709.apps.googleusercontent.com',
                                client_secret='xq-a3cEOw8xWPMtxk4Q0SV3B',
                                scope='https://sites.google.com/feeds/',
                                user_agent='daryl.testing',
                                access_token='4/sBW4E5pZ8cV05OY3MGmcRylLx5cM',
                                refresh_token='1/1b8JVsXJUxFtrluZhchk_b1NR1AfQ3YgEb5h67_pR18')
#print token.generate_authorize_url()
#code = raw_input('What is the verification code? ').strip()
#token.get_access_token(code)
#print token.refresh_token

spr_client = gdata.sites.client.SitesClient('sustainablecorn')
token.authorize(spr_client)

for u in spr_client.get_acl_feed().entry:
    print u.get_id().split("%3A")[1].replace("%40","@")
