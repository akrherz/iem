"""Download from USDM website"""
from __future__ import print_function

import requests
import pandas as pd

SERVICE = "http://droughtmonitor.unl.edu/Ajax.aspx/ReturnTabularDM"


def main():
    """Go Main!"""
    payload = "{'area':'IA', 'type':'state', 'statstype':'2'}"
    headers = {}
    headers['Accept'] = "application/json, text/javascript, */*; q=0.01"
    headers['Content-Type'] = "application/json; charset=UTF-8"
    req = requests.post(SERVICE, payload, headers=headers)
    jdata = req.json()
    df = pd.DataFrame(jdata['d'])
    df.sort_values('Date', ascending=True, inplace=True)
    df[['Date', 'None', 'D0', 'D1', 'D2', 'D3', 'D4']].to_csv('iowa.txt',
                                                              index=False)


if __name__ == '__main__':
    main()
