#!/usr/bin/env python
"""
https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-manager-request-limits
https://management.azure.com/subscriptions/{guid}/resourcegroups?api-version=2016-09-01
we start with status code 429 at deployment time
NOT including any other error check for different Azure services
"""

import time
import azAuth
import requests
import adal
import json
import sys, os, getopt
import datetime
from azure.mgmt.resource import ResourceManagementClient

# subscription_id = '09d29343-ed9a-4ad8-baa3-25e147d2d48a'

subscription_id = raw_input('Enter subscription ID: ')

url = 'https://management.azure.com/subscriptions/' + subscription_id + '/resourcegroups?api-version=2016-09-01'
access_token = azAuth.getAccessToken(subscription_id)
auth = {"Authorization": 'Bearer ' + access_token}

results = requests.get(url, headers=auth)
status = results.status_code
remainReads = results.headers["x-ms-ratelimit-remaining-subscription-reads"]
#remainWrites = results.headers["x-ms-ratelimit-remaining-subscription-writes"]

print("Status:" + status, "RemainingReads:" + remainReads)

# json_output = results.json()
#
# print(json.dumps(json_output, indent=2))
#
# for sub in json_output["value"]:
#     print(sub["id"] + ': ' + sub["name"] + ': ' + sub["properties"]["provisioningState"])

def waitretry():
    if status == '429' :
        waittime = results.headers["Retry-After"]
        print(waittime)
        time.sleep(waitime)

# add re-run deploy since template deployment are incremental
def reDeploy():
    # re-deploy template

# define user-defined exceptions
class CustomError(Exception):
   """Base class for other exceptions"""

try:
    # Raise an exception with argument
    raise CustomError('This is a CustomError')
except CustomError as e:
    # Catch the custom exception
    print "Error: %s" % e

class TooManyRequestsError(CustomError):
   """Raised when HTTP status code is 429 Too many requests"""
    waitretry()
    reDeploy()

class OtherError(CustomError):
   """Raised when ..."""
      print("test only")

# main program to test

while True:
   try:
       stat = status
       if stat == 429:
           raise TooManyRequestsError
       else:
           raise OtherError(status)
       break
   except TooManyRequestsError:
       print("Wait for " + waittime() + " then try again!")
   except OtherError:
       print("This is test only, will add other errors to be handled !")
   time.sleep(5*60)  # wait 5 minutes


