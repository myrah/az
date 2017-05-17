#!/usr/bin/env python

"""AzAuth class to get API access on Azure"""
import os.path
import json
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
import adal
import sys,os,getopt
import datetime

def getCredentials():
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    return credentials

def getAccessToken(subscription_id):
    #subscription_id = '09d29343-ed9a-4ad8-baa3-25e147d2d48a'
    #subscription_id = raw_input('Enter subscription ID: ')
    authentication_endpoint = 'https://login.microsoftonline.com/'
    resource = 'https://management.core.windows.net/'
    client_id = os.environ['AZURE_CLIENT_ID']
    secret = os.environ['AZURE_CLIENT_SECRET']
    tenant = os.environ['AZURE_TENANT_ID']

    # get an Azure access token using the adal library
    context = adal.AuthenticationContext(authentication_endpoint + tenant)
    token_response = context.acquire_token_with_client_credentials(resource, client_id, secret)
    access_token = token_response.get('accessToken')
#    print(access_token)
    return access_token
