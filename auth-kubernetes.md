# Configure Vault
Configure `Kubernetes` authentication fro your Vault.  
These steps can be done either via web console or command line. Below command line option is shown.

1. Connect to Vault instance

```
$ oc exec -it vault-0 -- bin/sh
```
2. Enable Kubernetes auth method
```
$ valult auth enable -path demo-cluster kubernetes
```
3. Configure auth method (use same URL as for `oc login` , eg https://api.crc.testing:6443)
```
$ vault write auth/demo-cluster/config \
   kubernetes_host="https://api.cluster.endpoint:port"

```

# Create Secret engine
```
vault secrets enable -path=dev-secrets kv-v2
```