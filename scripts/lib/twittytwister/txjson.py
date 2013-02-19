import json

def parseUpdateResponse(responsetext):
    return json.loads(responsetext)["id"]