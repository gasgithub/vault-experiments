Based on https://developer.hashicorp.com/vault/docs/deploy/kubernetes/helm/openshift

Install the latest Vault Helm chart in HA Raft mode:
```
$ helm install vault hashicorp/vault \
  --create-namespace \
  --namespace vault \
  --set='global.openshift=true' \
  --set='server.ha.enabled=true' \
  --set='server.ha.raft.enabled=true'
```

Initialize and unseal vault-0 pod:
```
$ oc exec -ti vault-0 -- vault operator init
$ oc exec -ti vault-0 -- vault operator unseal
```

Finally, join the remaining pods to the Raft cluster and unseal them. The pods will need to communicate directly so we'll configure the pods to use the internal service provided by the Helm chart:
```
$ oc exec -ti vault-1 -- vault operator raft join http://vault-0.vault-internal:8200
$ oc exec -ti vault-1 -- vault operator unseal

$ oc exec -ti vault-2 -- vault operator raft join http://vault-0.vault-internal:8200
$ oc exec -ti vault-2 -- vault operator unseal
```

