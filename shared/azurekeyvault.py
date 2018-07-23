#! /usr/bin/env python3.6
# source code:
# https://github.com/Azure-Samples/key-vault-python-authentication/blob/d4c4cd53ccf4ba6252d35f881892265b09c5e476/authentication_sample.py#L90-L131
import adal
from azure.keyvault import KeyVaultClient, KeyVaultAuthentication
from azure.keyvault import KeyVaultId
import json

# read configuration file
with open('config.json') as f:
    config = json.load(f)

tenant_id = config['keyvault']['tenant_id']
vault_uri = config['keyvault']['vault_uri']
client_id = config['keyvault']['client_id']

# create an adal authentication context
auth_context = adal.AuthenticationContext('https://login.microsoftonline.com/%s' % tenant_id)

# create a callback to supply the token type and access token on request
# resource is provided by keyvault
def adal_callback(server, resource, scope):
    user_code_info = auth_context.acquire_user_code(resource,client_id)

    print(user_code_info['message'])
    token = auth_context.acquire_token_with_device_code(resource=resource,
                                                        client_id=client_id,
                                                        user_code_info=user_code_info)
    return token['tokenType'], token['accessToken']

# create a KeyVaultAuthentication instance which will callback to the supplied adal_callback
auth = KeyVaultAuthentication(adal_callback)

# create the KeyVaultClient using the created KeyVaultAuthentication instance
client = KeyVaultClient(auth)

def get_secret(secret_name):
    """
    authenticates to the Azure Key Vault by providing a callback to authenticate using adal
    """
    print('getting secret')
    secret_bundle = client.get_secret(vault_uri, secret_name, secret_version=KeyVaultId.version_none)
    print(secret_bundle)

if __name__ == "__main__":
    get_secret("shunpythonsecrettest")