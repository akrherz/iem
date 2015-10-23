"""
 List out the folders on the Google Drive and see who their owners are!
"""
import util

drive = util.get_driveclient()

res = drive.files().list(
        q="mimeType = 'application/vnd.google-apps.folder'",
        maxResults=999).execute()

for item in res['items']:
    for owner in item['owners']:
        if owner['emailAddress'] != 'cscap.automation@gmail.com':
            print item['title'], owner['emailAddress']
