import os

# Use the OpenShift authenticator.

from oauthenticator.openshift import OpenShiftOAuthenticator
c.JupyterHub.authenticator_class = OpenShiftOAuthenticator

# Override scope as oauthenticator code doesn't set it correctly.

OpenShiftOAuthenticator.scope = ['user:info']

# Setup OAuth configuration by querying it from environment.

service_account_name = '%s-sa' % os.environ['JUPYTERHUB_SERVICE_NAME']
service_account_path = '/var/run/secrets/kubernetes.io/serviceaccount'

with open(os.path.join(service_account_path, 'namespace')) as fp:
    namespace = fp.read().strip()

client_id = 'system:serviceaccount:%s:%s' % (namespace, service_account_name)

c.OpenShiftOAuthenticator.client_id = client_id

with open(os.path.join(service_account_path, 'token')) as fp:
    client_secret = fp.read().strip()

c.OpenShiftOAuthenticator.client_secret = client_secret

# Work out hostname for the exposed route. This is tricky as we need
# to use the REST API to query it.

import openshift.client

openshift.client.configuration.api_key_prefix['authorization'] = 'Bearer'
openshift.client.configuration.api_key['authorization'] = client_secret

api_instance = openshift.client.AdmissionregistrationApi()

print(api_instance.list_namespaced_route())

#c.OpenShiftOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
