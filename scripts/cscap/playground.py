import util
import sys
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('mytokens.cfg')

FOLDERS = {}

drive = util.get_driveclient()

body = {'title': 'My Title 22',
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [{'id': '0B6ZGw0coobCxTnVsb0RLQUd1U0U'}]}
res = drive.files().insert(body=body).execute()
print res['parents']

"""
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
