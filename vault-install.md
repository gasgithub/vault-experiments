# Install Vault
1. Create `vaulte` project

```
$ oc new-project vault
```

2. Add the Hashicorp Helm repository.

```
$ helm repo add hashicorp https://helm.releases.hashicorp.com
```

3. Update all the repositories to ensure helm is aware of the latest versions.

```
$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "hashicorp" chart repository
Update Complete. ⎈Happy Helming!⎈
```

4. Install the latest version of the Vault server running in development mode configured to work with OpenShift.

For all params check: [heml values](https://github.com/hashicorp/vault-helm/blob/main/values.yaml)  
for openshift: [values for openshift](https://github.com/hashicorp/vault-helm/blob/main/values.openshift.yaml)

This installs vault in `dev` mode.
Dev requires no further setup, no state management, and no initialization. This is useful for experimenting with Vault without needing to unseal, store keys, et. al. All data is lost on restart - **do not use dev mode for anything other than experimenting**.

```
$ helm install vault hashicorp/vault \
    --set "global.openshift=true" \
    --set "server.dev.enabled=true" \
    --set "server.image.repository=docker.io/hashicorp/vault" \
    --set "injector.image.repository=docker.io/hashicorp/vault-k8s" \
    --set "route.enabled=true" \
    --set "route.tls.termination: edge"
```



The Vault pod and Vault Agent Injector pod are deployed in the default namespace.

# Configure web access
By default server in dev mode doesnt provide `route` to access via browser

Apply the following yaml to create `route`:

```
kind: Route
apiVersion: route.openshift.io/v1
metadata:
  name: vault
  labels:
    app.kubernetes.io/instance: vault
spec:
  to:
    kind: Service
    name: vault
    weight: 100
  port:
    targetPort: http
  tls:
    termination: edge
  wildcardPolicy: None
```
Then access your Vault via:
`https://vault-vault.apps.....`
