import os
import uuid

import jwt
import requests
from adal import AuthenticationContext


class Config():
    # Authentication config
    DATABRICKS_RID = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d"
    LOGIN_URL = "https://login.microsoftonline.com/"
    # Adobe Tenant ID
    TENANT_ID = "<tenant ID>"
    # databricks Native application
    CLIENT_ID = "<client ID>"
    authority_url = LOGIN_URL + TENANT_ID
    # Databricks config
    BASE_URL = 'https://eastus2.azuredatabricks.net'
    API_URL = f'{BASE_URL}/api/2.0/'
    # To initialize/launch workspace
    SUBSCRIPTION = "<sub ID>"
    RESOURCE_GROUP = "<RG_name>"
    WORKSPACE = "<workspace_name>"
    # if workspace already launched with know org id
    ORG_ID = "<org id>"

class Databricks():
    def __init__(self, org_id=None):
        self._access_token = None
        self._refresh_token = None
        self.code = None
        self._session = None
        self.org_id = org_id
        self.api_url = Config.API_URL
        self.context = AuthenticationContext(Config.authority_url)

    @property
    def refresh_token(self):
        if not self._refresh_token:
            try:
                with open('.token', 'r') as f:
                    self._refresh_token = f.read()
            except:
                return None
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value):
        if not value:
            try:
                os.remove('.token')
            except:
                pass
        try:
            with open('.token', 'w') as f:
                f.write(value)
        except:
            pass

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
        self._session.headers.update({'Authorization': "Bearer " + self.access_token})
        if self.org_id:
            # If we have an ORG_ID
            self._session.headers.update({'X-Databricks-Org-Id': self.org_id})
        else:
            # If not
            self._session.headers.update({
                                             'X-Databricks-Azure-Workspace-Resource-Id': f"/subscriptions/{Config.SUBSCRIPTION}/resourceGroups/{Config.RESOURCE_GROUP}/providers/Microsoft.Databricks/workspaces/{Config.WORKSPACE}"})
        return self._session

    @property
    def access_token(self):
        try:
            # Do we have an access token
            if self._access_token:
                # Is it still valid - 1 hour expiry FYI
                jwt.decode(self._access_token, verify=False)
        except jwt.ExpiredSignatureError:
            # It's expired, fetch a new one from refresh token
            return self.get_access_from_refresh()
        if self._access_token:
            # If we get there, we have a token and it's valid
            return self._access_token
        # We don't have a token, fetch a new one from refresh token
        return self.get_access_from_refresh()

    @access_token.setter
    def access_token(self, value):
        self._access_token = value

    def get_access_from_refresh(self):
        try:
            token_response = self.context.acquire_token_with_refresh_token(refresh_token=self.refresh_token,
                                                                           client_id=Config.CLIENT_ID,
                                                                           resource=Config.DATABRICKS_RID)
            self.access_token = token_response["accessToken"]
            self.refresh_token = token_response["refreshToken"]
            return self.access_token
        except:
            # The refresh token might be expired, restart auth flow from step 0
            # Invalidate known refresh token so that the cache file gets deleted
            self.refresh_token = None
            return self.get_access_from_code()

    def get_access_from_code(self):
        """
        This is step 0 of the auth flow. Ask user to provide access and retrieve authorization code from Azure.
        """
        if not self.code:
            print("We need to retrieve a new Authorization code, please open the following link:")
            print(
                f"https://login.microsoftonline.com/{Config.TENANT_ID}/oauth2/authorize?client_id={Config.CLIENT_ID}&response_type=code&redirect_uri=http%3A%2F%2Flocalhost&response_mode=query&resource={Config.DATABRICKS_RID}&state={str(uuid.uuid4())}")
            print(f"Azure will redirect you to a local URL that will not resolve, this is normal.")
            code_input = input("Please input the returned URL from your browser: ")
            code = code_input.split('=')[1].replace('&state', '')
            self.code = code
        token_response = self.context.acquire_token_with_authorization_code(authorization_code=self.code,
                                                                            redirect_uri='http://localhost',
                                                                            resource=Config.DATABRICKS_RID,
                                                                            client_id=Config.CLIENT_ID)
        self.access_token = token_response["accessToken"]
        self.refresh_token = token_response["refreshToken"]
        return self.access_token

    def list_workspace(self):
        r = self.session.get(self.api_url + 'workspace/list')
        return r.json()


    def list_clusters(self):
        r = self.session.get(self.api_url + 'clusters/list')
        return r.json()

    def list_jobs(self):
        r = self.session.get(self.api_url + 'jobs/list')
        return r.json()


#d = Databricks(org_id=Config.ORG_ID)
d = Databricks()
print(f"Workspace: {d.list_workspace()}")
print(f"Clusters: {d.list_clusters()}")
print(f"Jobs: {d.list_jobs()}")
