import os

import json
import requests

# Work out the public server address for the OpenShift REST API. Don't
# know how to get this via the REST API client so do a raw request to
# get it. Make sure request is done in a session so connection is closed
# and later calls against REST API don't attempt to reuse it. This is
# just to avoid potential for any problems with connection reuse.

server_url = 'https://openshift.default.svc.cluster.local'
api_url = '%s/oapi' % server_url

with requests.Session() as session:
    response = session.get(api_url, verify=False)
    data = json.loads(response.content.decode('UTF-8'))
    address = data['serverAddressByClientCIDRs'][0]['serverAddress']

# Enable the OpenShift authenticator. The OPENSHIFT_URL environment
# variable must be set before importing the authenticator as it only
# reads it when module is first imported.

os.environ['OPENSHIFT_URL'] = 'https://%s' % address

from oauthenticator.openshift import OpenShiftOAuthenticator
c.JupyterHub.authenticator_class = OpenShiftOAuthenticator

# Override scope as oauthenticator code doesn't set it correctly.
# Need to lodge a PR against oauthenticator to have this fixed.

OpenShiftOAuthenticator.scope = ['user:info']

# Setup authenticator configuration using details from environment.

service_name = os.environ['JUPYTERHUB_SERVICE_NAME']

service_account_name = '%s-sa' %  service_name
service_account_path = '/var/run/secrets/kubernetes.io/serviceaccount'

with open(os.path.join(service_account_path, 'namespace')) as fp:
    namespace = fp.read().strip()

client_id = 'system:serviceaccount:%s:%s' % (namespace, service_account_name)

c.OpenShiftOAuthenticator.client_id = client_id

with open(os.path.join(service_account_path, 'token')) as fp:
    client_secret = fp.read().strip()

c.OpenShiftOAuthenticator.client_secret = client_secret

# Work out hostname for the exposed route of the JupyterHub server. This
# is tricky as we need to use the REST API to query it.

import openshift.client
import openshift.config

openshift.config.load_incluster_config()

api_client = openshift.client.ApiClient()
oapi_client = openshift.client.OapiApi(api_client)

route_list = oapi_client.list_namespaced_route(namespace)

host = None

for route in route_list.items:
    if route.metadata.name == service_name:
        host = route.spec.host

if not host:
    raise RuntimeError('Cannot calculate external host name for JupyterHub.')

c.OpenShiftOAuthenticator.oauth_callback_url = 'https://%s/hub/oauth_callback' % host
