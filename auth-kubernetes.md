# Configure Vault
Configure `Kubernetes` authentication fro your Vault.  
These steps can be done either via web console or command line. Below command line option is shown.

1. Connect to Vault instance

```
$ oc exec -it vault-0 -- bin/sh
```
2. Enabel Kubernetes auth method
```
$ valult auth enable -path demo-cluster kubernetes
```
3. Configure auth method (use same URL as for `oc login`)
```
$ vault write auth/demo-cluster/config \
   kubernetes_host="https://api.cluster.endpoint:port"

```