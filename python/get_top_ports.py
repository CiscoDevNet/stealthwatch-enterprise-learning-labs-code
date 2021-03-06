#!/usr/bin/env python

"""
This script will get the top ports for a specific IP in Stealthwatch using the REST API.

For more information on this API, please visit:
https://developer.cisco.com/docs/stealthwatch/

 -

Script Dependencies:
    requests
Depencency Installation:
    $ pip install requests

System Requirements:
    Stealthwatch Version: 6.10.0 or higher

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
    # TODO: Complete the "Flow Reports" query to get the Top Ports
    url = 'https://' + SMC_HOST + '/sw-reporting/v1/tenants/' + SMC_TENANT_ID + '...'

    # Set the timestamps for the filters, in the correct format, for last 60 minutes
    end_datetime = datetime.datetime.utcnow()
    start_datetime = end_datetime - datetime.timedelta(minutes=60)

    # Timestamps for this API call requires 3-digit microseconds, so removing the 4th digit at the end of the timestamp
    end_timestamp = end_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-1]
    start_timestamp = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-1]

    # Set the filter with the request data
    request_data = {
        "startTime": start_timestamp,
        "endTime": end_timestamp,
        "subject": {
            "ipAddresses": {
                "includes": [MALICIOUS_IP]
            }
        },
        "maxRows": 50
    }

    # Perform the query to initiate the search
    request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = api_session.request("POST", url, verify=False, data=json.dumps(request_data), headers=request_headers)

    # If successfully able to initiate search, grab the search details
    if (response.status_code == 200):
        print("Generating results. Please wait...\n")
        search = json.loads(response.content)["data"]

        # Set the URL to check the search status
        url = 'https://' + SMC_HOST + '/sw-reporting/v1/tenants/' + SMC_TENANT_ID + '/flow-reports/top-ports/queries/' + search["queryId"]

        # While search status is not complete, check the status every second
        # TODO: What "status" should we look for to know when the query is complete?
        while search["status"] != "XXXX":
            response = api_session.request("GET", url, verify=False)
            search = json.loads(response.content)["data"]
            time.sleep(1)

        # Set the URL to check the search results and get them
        url = 'https://' + SMC_HOST + '/sw-reporting/v1/tenants/' + SMC_TENANT_ID + '/flow-reports/top-ports/results/' + search["queryId"]
        response = api_session.request("GET", url, verify=False)
        results = json.loads(response.content)["data"]["results"]

        # Loop through the results and print each row in a new line
        for row in results:
            print(row)

    # If unable to update the IPs for a given tag (host group)
    else:
        print("An error has ocurred, while getting top-ports, with the following code {}".format(response.status_code))

# If the login was unsuccessful
else:
        print("An error has ocurred, while logging in, with the following code {}".format(response.status_code))
