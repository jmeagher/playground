Basic container with the helpful utilities for exploring kubernetes from inside the cluster already installed

Run it in Kubernetes using the latest docker hub image with `kubectl run --image jpmeagher/kube-shell:latest kube-shell`. Attach to this with `kubectl exec $(kubectl get pods | grep kube-shell | awk '{print $1}') -ti -- /bin/bash -l`

Run it from the docker hub image with `docker run -ti jpmeagher/kube-shell:latest`

Run it from this folder with `docker build -t kube-shell . && docker run -ti kube-shell:latest`

Build and publish the latest of this with `T=jpmeagher/kube-shell:latest ; docker build -t kube-shell . && docker tag kube-shell:latest $T && docker push $T`

Build and publish a snapshot of this with `T="jpmeagher/playground:shell-kubernetes-$(date -u +%Y-%m-%d)" ; docker build -t kube-shell . && docker tag kube-shell:latest $T && docker push $T`
