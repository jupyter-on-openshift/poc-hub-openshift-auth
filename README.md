JupyterHub (OpenShift)
======================

This repository contains a sample application for deploying JupyterHub as a means to provide Jupyter notebooks to multiple users. Authentication of users is managed by using the authentication provider of the OpenShift cluster JupyterHub is deployed to.

Deploying the application
-------------------------

To deploy the sample application, you can run:

```
oc new-app https://raw.githubusercontent.com/jupyter-on-openshift/poc-hub-openshift-auth/master/templates/jupyterhub.json
```

This will create all the required builds and deployments from the one template.

If desired, you can instead load the template, with instantiation of the template done as a separate step from the command line or using the OpenShift web console.

Resource requirements
---------------------

If deploying to an OpenShift environment that enforces quotas, you must have a memory quota for terminating workloads (pods) of 3GiB so that builds can be run. For one user, you will need 6GiB of quota for terminating workloads (pods). Each additional user requires 1GiB.

For storage, two 1GiB persistent volumes are required for the PostgreSQL databases for KeyCloak and JupyterHub. Further, each user will need a 1GiB volume for notebook storage.
