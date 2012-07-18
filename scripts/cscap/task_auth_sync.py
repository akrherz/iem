"""
A script that syncs my google site authentication to a shared folder on google docs
$Id: task_auth_sync.py 8231 2012-05-07 20:29:34Z akrherz $:
"""
from gdata import gauth
import gdata.sites.client
import gdata.docs.client
import gdata.docs.data
import gdata.acl.data
import gdata.data
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

token = gauth.OAuth2Token(client_id=config.get('appauth','client_id'),
                                client_secret=config.get('appauth', 'app_secret'),
                                user_agent='daryl.testing',
                                scope=config.get('googleauth', 'scopes'),
                                refresh_token=config.get('googleauth', 'refresh_token'))

spr_client = gdata.sites.client.SitesClient( config.get('cscap', 'sitename') )
token.authorize(spr_client)

site_users = []
for acl in spr_client.get_acl_feed().entry:
    print "IN: ||%s||" % (acl.scope.value,)
    userid =  acl.scope.value 
    if userid not in site_users:
        site_users.append( acl.scope.value )
    #if userid == 'smzuber@illinois.edu':
    #    print acl
    
docs_client = gdata.docs.client.DocsClient()
token.authorize(docs_client)
query = gdata.docs.client.DocsQuery(show_collections='true', title='CSCAP Internal Documents')
feed = docs_client.GetAllResources(query=query)
#collection = feed[0]
#cscap = docs_client.GetResource( feed[0] )
cscap = feed[0]
acl_feed = docs_client.GetResourceAcl( cscap )
for acl in acl_feed.entry:
    #print acl.role.value, acl.scope.type, acl.scope.value
    userid = acl.scope.value
    #print "OUT: ||%s||" % (userid,)
    if userid in site_users:
        site_users.remove( userid )

acls = []
for loser in site_users:
    print 'Adding %s as writer to CSCAP Internal Documents Collection' % (loser,)
    acls.append( gdata.docs.data.AclEntry(
                    scope=gdata.acl.data.AclScope(value=loser, type='user'),
                    role=gdata.acl.data.AclRole(value='writer'),
                    batch_operation=gdata.data.BatchOperation(type='insert'),
                    )
                )
            
print cscap.GetAclLink().href
if len(acls) > 0:
    print docs_client.BatchProcessAclEntries(cscap, acls)
