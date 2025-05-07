# Vault Secrets Operator example

It is assumed that Vault is already installed (if not follow [Vault installation](../vault-install.md))  and Kubernetes authentication is configured ([Configure authentication](../auth-kubernetes.md))

## Install Operator
Access the OperatorHub and search for `Vault Secret Operator`.  Install operator using default settings.

## Configure Vault Connection
Create resource that configures connection to the vault.  
You can either create connection object via operator page or by applying the following yaml:

```
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultConnection
metadata:
  name: vaultconnection-sample
  namespace: openshift-operators
spec:
  address: 'http://vault.vault.svc.cluster.local:8200'
  skipTLSVerify: false
```
Run:

```
$ oc apply -f vault-connection.yaml
```

## Configure Authentication
Vault operator needs details how to authenticate to vault.  
This is defined by the `VaultAuth` object. Make sure you are using target app namespace.
You can combine that with `VaultAuthGlobal` if you need to share same authentication params for multiple apps. 
See [Vault authentication in detail](https://developer.hashicorp.com/vault/docs/platform/k8s/vso/sources/vault/auth)

Create the following object (via operator page or yaml). 

```
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultAuth
metadata:
  name: static-auth
  namespace: vault-app-vso
spec:
  method: kubernetes
  mount: demo-cluster
  vaultConnectionRef: openshift-operators/vaultconnection-sample  
  kubernetes:
    role: app1-role
    serviceAccount: default
    audiences:
      - vault
```
where:
 - `namespece` - defines your application project/namespace
 - `method` - should be fixed to kubernetes
 - `mount` - is vault authentication configuration for kubernetes method
 - `role` - defines access role in vault that can access the secrets
 - `serviceAccount` - defines account that apps uses to run in K8s. If you use non `default` account, make sure to configure it correctly in the namespace and `Deployment` object. 

## Configure Secret
Vault operator will automatically create k8s secret based on the secret defined in the Vault.

Lets create required secret in the vault for our application. This will put in the `dev-secrets` engine, secret named `config` for in the path `app` that contains `username` and `password` keys (as usual you can do it also via Vault GUI):

```
$ vault kv put dev-secrets/app1/config username="static-user" password="static-password"
```

### Create policy
Vault defaults to **denying** capabilities to paths to ensure that it is secure by default, so you need to create policy that would allow access to the secret. Create the following policy and name it `app1`:

```
path "dev-secrets/data/app1/config" {
   capabilities = ["read", "list"]
}
```

### Create a role in Vault to enable access to secrets within the `dev-secrets` engine using `app1` policy:

```
vault write auth/demo-cluster/role/app1-role \
   bound_service_account_names=* \
   bound_service_account_namespaces=vault-app-vso \
   policies=app1 \
   audience=vault \
   ttl=24h
```

where:
- `bound_service_account_names` - limits sa names that can use the role (* - any name)
- `bound_service_account_namespaces` - limits namespaces that can use the role
- `policies` - defines policy that will be attached to the role


### Create static secret
Create the following secret:
```
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultStaticSecret
metadata:
  name: vault-secret
  namespace: vault-app-vso  
spec:
  type: kv-v2

  # mount path (engine name)
  mount: dev-secrets

  # path of the secret
  path: app1/config

  # dest k8s secret name
  destination:
    name: app-secret
    create: true

  # static secret refresh interval
  refreshAfter: 30s
  ```

  After applying this, you will notice that matching k8s secret was created in the same namespace:
  ```
kind: Secret
apiVersion: v1
metadata:
  name: app-secret
  namespace: vault-app-vso
  labels:
    app.kubernetes.io/component: secret-sync
    app.kubernetes.io/managed-by: hashicorp-vso
    app.kubernetes.io/name: vault-secrets-operator
    secrets.hashicorp.com/vso-ownerRefUID: 0c573e85-2fb3-45ae-a071-07706fc80d9e
  ownerReferences:
    - apiVersion: secrets.hashicorp.com/v1beta1
      kind: VaultStaticSecret
      name: vault-secret
data:
  _raw: eyJkYXRhIjp7InBhc3N3b3JkIjoic3RhdGljLXBhc3N3b3JkIiwidXNlcm5hbWUiOiJzdGF0aWMtdXNlciJ9LCJtZXRhZGF0YSI6eyJjcmVhdGVkX3RpbWUiOiIyMDI1LTA0LTMwVDE1OjM4OjAzLjM0MTQ2MjY1NFoiLCJjdXN0b21fbWV0YWRhdGEiOm51bGwsImRlbGV0aW9uX3RpbWUiOiIiLCJkZXN0cm95ZWQiOmZhbHNlLCJ2ZXJzaW9uIjoxfX0=
  password: c3RhdGljLXBhc3N3b3Jk
  username: c3RhdGljLXVzZXI=
type: Opaque
```

*For configuring rotation see the next sections*


## Configure the application
It is assumed that sample app is already deployed in the same namespace (if not refer to the `webapp` section).
Configure deployment to use the secret:

```
          envFrom:
            - secretRef:
                name: app-secret
```
Test if you are seeing secrets correctly in the app.

# Rotation
If you will edit secret via vault UI, you will see new values in vault secret and in the generated k8s secret.
However, secrets are not update in the application.

`RolloutRestartTargets` should be configured whenever the application(s) consuming the Vault secret does
not support dynamically reloading a rotated secret. The Operator will trigger a "rollout-restart" for each target whenever the Vault secret changes between reconciliation events.

Add the following section to the vault secret definition:

```
  rolloutRestartTargets:
  - kind: Deployment
    name: app
```

Retest changing secret in the vault and observe Deployment pods being restarted.

## Dynamic secrets
Manually rotating secrets is can be cumbersome and prone to human error. You can use dynamic secrets that are automatically rotated. For more see [Dynamic secrets](https://developer.hashicorp.com/vault/tutorials/kubernetes/vault-secrets-operator#dynamic-secrets)