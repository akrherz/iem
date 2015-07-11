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

spr_client = util.get_sites_client(config)
service = util.get_driveclient()

site_users = []
for acl in spr_client.get_acl_feed().entry:
    userid = acl.scope.value
    if userid not in site_users:
        site_users.append(acl.scope.value)

# Get a listing of current permissions
perms = service.permissions().list(fileId=config.get('cscap', 'folderkey')).execute()
for item in perms.get('items', []):
    email = item['emailAddress']
    if email in site_users:
        site_users.remove(email)
        continue
    print("Email: %s can access Drive, not sites" % (email,))

for loser in site_users:
    print loser
    continue
    id_resp = service.permissions().getIdForEmail(email=loser).execute()
    id2 = id_resp['id']
    print(('Adding %s[%s] as writer to CSCAP Internal Documents Collection'
           ) % (loser, id2))
    newperm = dict(id=id2, type='user', role='writer',
                   sendNotificationEmails=False)
    res = service.permissions().insert(fileId=config.get('cscap', 'folderkey'),
                                       body=newperm).execute()
    print res
