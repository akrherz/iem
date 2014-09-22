"""
Sync authorized users on Google Sites to Google Drive

"""
import gdata.docs.client
import gdata.docs.data
import gdata.acl.data
import gdata.data
import ConfigParser
import util

config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')


docs_client = util.get_docs_client( config )
spr_client = util.get_sites_client( config )

site_users = []
for acl in spr_client.get_acl_feed().entry:
    #print "IN: ||%s||" % (acl.scope.value,)
    userid =  acl.scope.value 
    if userid not in site_users:
        site_users.append( acl.scope.value )

query = gdata.docs.client.DocsQuery(show_collections='true', 
                                    title='CSCAP Internal Documents')
feed = docs_client.GetAllResources(query=query)
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
            
if len(acls) > 0:
    feed = docs_client.BatchProcessAclEntries(cscap, acls)
    for entry in feed.entry:
        print entry.role.value, entry.title.text
