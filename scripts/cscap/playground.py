import datetime
import pytz
import pyiem.cscap_utils as util

config = util.get_config()

FOLDERS = {}

drive = util.get_driveclient(config)

print drive.files(
        ).delete(fileId='1W_gQBFxxOVpUkdzDoM3eKmYbGbPuofYl29WfHUDlsUo').execute()

sys.exit()
res = drive.revisions().list(
        fileId='1TbvxhjXNrE-pQoi7_lpkODinXsgRKHhdz_9m_wYR37U').execute()
for item2 in res['items']:
    md = datetime.datetime.strptime(item2['modifiedDate'][:19],
                                    '%Y-%m-%dT%H:%M:%S')
    md = md.replace(tzinfo=pytz.timezone("UTC"))
    luser = item2['lastModifyingUser']
    print '----------------------------------------------------------'
    print md, luser['emailAddress']
    print item2

"""
id_resp = drive.permissions(
            ).getIdForEmail(email='cscap.automation@gmail.com').execute()
uid = id_resp['id']

res = drive.files().list(q="'me' in owners").execute()
for item in res['items']:
    print item['title']
    permission = drive.permissions().get(
        fileId=item['id'], permissionId=uid).execute()
    permission['role'] = 'owner'
    print drive .permissions().update(
        fileId=item['id'], permissionId=uid, body=permission,
        transferOwnership=True).execute()

body = {'title': 'My Title 22',
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [{'id': '0B6ZGw0coobCxTnVsb0RLQUd1U0U'}]}
res = drive.files().insert(body=body).execute()
print res['parents']

folders = drive.files().list(q="mimeType = 'application/vnd.google-apps.folder'",
                             maxResults=999).execute()
for i, item in enumerate(folders['items']):
    FOLDERS[item['id']] = dict(title=item['title'], parents=[],
                               basefolder=None)
    for parent in item['parents']:
        FOLDERS[item['id']]['parents'].append(parent['id'])

for thisfolder in FOLDERS:
    title = FOLDERS[thisfolder]['title']
    if len(FOLDERS[thisfolder]['parents']) == 0:
        continue
    parentfolder = FOLDERS[thisfolder]['parents'][0]
    while len(FOLDERS[parentfolder]['parents']) > 0:
        parentfolder = FOLDERS[parentfolder]['parents'][0]
    print title, '->', FOLDERS[parentfolder]['title']
    FOLDERS[thisfolder]['basefolder'] = parentfolder

children = drive.children().list(folderId=util.CONFIG['cscap']['basefolder']).execute()
for item in children['items']:
    folderid = item['id']
    meta = drive.files().get(fileId=folderid).execute()
    print folderid, meta['title']
"""
