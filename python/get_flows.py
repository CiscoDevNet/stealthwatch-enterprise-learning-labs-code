#!/usr/bin/env python

"""
This script will get the flows for a specific IP in Stealthwatch using the REST API.

For more information on this API, please visit:
https://www.cisco.com/web/fw/stealthwatch/Online-Help/Content/Online-Help/enterprise-rest-api.htm

 -

Script Dependencies:
    requests
Depencency Installation:
    $ pip install requests

System Requirements:
    Stealthwatch Version: 7.0.0 or higher

Copyright (c) 2019, Cisco Systems, Inc. All rights reserved.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import datetime
import json
import time

import requests

try:
    requests.packages.urllib3.disable_warnings()
except:
    pass


# Enter all authentication info
SMC_USER = ""
SMC_PASSWORD = ""
SMC_HOST = ""
SMC_TENANT_ID = ""
MALICIOUS_IP = ""

# Set the URL for SMC login
url = "https://" + SMC_HOST + "/token/v2/authenticate"

# Let's create the loginrequest data
login_request_data = {
    "username": SMC_USER,
    "password": SMC_PASSWORD
}

# Initialize the Requests session
api_session = requests.Session()

# Perform the POST request to login
response = api_session.request("POST", url, verify=False, data=login_request_data)

# If the login was successful
if(response.status_code == 200):

    # Set the URL for the query to POST the filter and initiate the search
    url = 'https://' + SMC_HOST + '/sw-reporting/v2/tenants/' + SMC_TENANT_ID + '/flows/queries'

    # Set the timestamps for the filters, in the correct format, for last 60 minutes
    end_datetime = datetime.datetime.utcnow()
    start_datetime = end_datetime - datetime.timedelta(minutes=60)
    end_timestamp = end_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
    start_timestamp = start_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Set the filter with the request data
    request_data = {
        "startDateTime": start_timestamp,
        "endDateTime": end_timestamp,
        "subject": {
            "ipAddresses": {
                "includes": [MALICIOUS_IP]
            }
        },
        "recordLimit": 50
    }

    # Perform the query to initiate the search
    request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = api_session.request("POST", url, verify=False, data=json.dumps(request_data), headers=request_headers)

    # If successfully able to initiate flows search, grab the search details
    # TODO: What HTTP response code do we need to look for?
    if (response.status_code == XXX):
        print("Generating results. Please wait...\n")
        search = json.loads(response.content)["data"]["query"]

        # Set the URL to check the search status
        # TODO: What do we need to add to the URL to look at the status of our previous query?
        # Hint: Print the 'search' variable.
        url = 'https://' + SMC_HOST + '/sw-reporting/v2/tenants/' + SMC_TENANT_ID + '/flows/queries/' + ...

        # While search status is not complete, check the status every second
        while search["percentComplete"] != 100.0:
            response = api_session.request("GET", url, verify=False)
            search = json.loads(response.content)["data"]["query"]
            time.sleep(1)

        # Set the URL to check the search results and get them
        # TODO: Use the same variable from the url assembly above.
        # Extra Credit: How could you shorten the URL construction?
        url = 'https://' + SMC_HOST + '/sw-reporting/v2/tenants/' + SMC_TENANT_ID + '/flows/queries/' + ... + "/results"
        response = api_session.request("GET", url, verify=False)
        results = json.loads(response.content)["data"]["flows"]

        # Loop through the results and print each flow in a new line
        for flow in results:
            print(flow)

    # If unable to update the IPs for a given tag (host group)
    else:
        print("An error has ocurred, while getting flows, with the following code {}".format(response.status_code))

# If the login was unsuccessful
else:
        print("An error has ocurred, while logging in, with the following code {}".format(response.status_code))
