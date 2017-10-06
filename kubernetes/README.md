# ElasticSearch Chaos Testing on Kubernetes

This _should_ work on any Kubernetes cluster, but I've used [Kubernetes on Google Cloud](https://cloud.google.com/container-engine/docs/).

## Basic Setup

These steps assume you are either familiar with Kubernetes and can run it yourself or you are using Google Clound Platform. If you are using GCP I'll try to include the commands needed to get it up and running.

If you do not have access to a Kubernetes cluster. [There are good docs on the Google site about how to get started with Kubernetes on GCP](https://cloud.google.com/container-engine/docs/quickstart). Here's what I used to create the GCE cluster

```
# This takes several minutes to run
$ gcloud beta container clusters create es-test \
 --zone us-central1-c \
 --additional-zones us-central1-b \
 --num-nodes 2 --machine-type n1-standard-2 \
 --preemptible

# If the get nodes command does nothing, try this to make sure the authentication is setup
$ gcloud container clusters get-credentials es-test
```

When done testing this cluster can be shut down to avoid paying for an idle cluster with `$ gcloud container clusters delete es-test`

The imporant thing is having kubectl work and connect to your cluster. An easy example command to make sure it is working is

```
$ kubectl get nodes
NAME                                       STATUS    AGE       VERSION
gke-es-testing-larger-pool-7793768a-mbrj   Ready     29m       v1.7.5
gke-es-testing-larger-pool-7793768a-p4g9   Ready     29m       v1.7.5
```

Make sure there is enough memory available. A single node cluster with something like minikube will likely not work. This test is running on 2 n1-standard-4 nodes with 4 CPU and 15 GB of ram each. The 2 nodes are in different zones.

```
$ kubectl describe nodes | grep instance-type
			beta.kubernetes.io/instance-type=n1-standard-4
			beta.kubernetes.io/instance-type=n1-standard-4

      $ kubectl describe nodes | grep -A3 Capacity
      Capacity:
       cpu:		4
       memory:	15406128Ki
       pods:		110
      --
      Capacity:
       cpu:		4
       memory:	15406128Ki
       pods:		110

```

### Run ElasticSearch

[Helm](https://github.com/kubernetes/helm) is used here to deploy all the nodes of the ElasticSearch cluster. See their instructions for installing Helm. Once installed run `helm init` to get everything setup.

The Helm Chart configuration to run the ElasticSearch cluster is in the helm-elasticsearch folder. The values.yaml file controls the details about what gets installed and run. Take a look at the values.yaml file. This configuration will start 1 master node, 1 client node, and 2 data nodes. This is a branch from the original [ElasticSearch for Helm configuration](https://github.com/clockworksoul/helm-elasticsearch). This makes a few configuration changes and removes Curator since the alpha features it is using are not available by default in the GCE Kubernetes. Additional changes were needed to get it working with the x-pack plugin from Elastic.

To start the ElasticSearch cluster run `$ helm install helm-elasticsearch --name es-test`. These should run within a short time. Confirm everything is started with

```
$ kubectl get pods
NAME                                                 READY     STATUS    RESTARTS   AGE
es-test-helm-elasticsearch-client-1872151621-2rsq7   1/1       Running   0          42s
es-test-helm-elasticsearch-data-2314445612-0tg5q     1/1       Running   0          42s
es-test-helm-elasticsearch-data-2314445612-mg1b1     1/1       Running   0          42s
es-test-helm-elasticsearch-master-3466965459-pnpp8   1/1       Running   0          42s
```

With this configuration the ElasticSearch cluster is only available from inside the Kubernetes cluster. It is a bit tough to directly access ElasticSearch with this setup so it can be a challenge to confirm everything is working. I use a Docker container with the utilities and dotfiles I am used to already installed. See docker/kube-shell/ for more details about this. Start the shell pod with `kubectl run --image jpmeagher/kube-shell:latest kube-shell`. Attach to this with `kubectl exec $(kubectl get pods | grep kube-shell | awk '{print $1}') -ti -- /bin/bash -l`.

Confirm ElasticSearch is running in your cluster with

```
$ curl es-test-helm-elasticsearch:9200/_cat/health
1505694033 00:20:33 jpm-es-testing green 4 2 0 0 0 0 0 0 - 100.0%
```

From inside the cluster the REST API for ElasticSearch will be accessible with the service name and port 9200.

### Run Kibana

Start the Elastic provided version of Kibana with `kubectl create -f kibana/kibana.yaml`. The kibana/kibana.yaml Kubernetes configuration will connect to the ElasticSearch cluster launched above. The login is the default from ElasticSearch (elastic/changeme).

To access this instance from outside the cluster a port-forward can be used. `kubectl port-forward $(kubectl get pods | grep es-test-kibana | awk '{print $1}') 5601 5601` will create a local redirect to Kibana. Open that via http://localhost:5601/.

### Run Locust

Start the basic Locust test that is included with `helm install -n locust-es-test locust`. Connect to this with `kubectl port-forward $(kubectl get pods | grep locust-es-test-master | awk '{print $1}') 8089 8089` and http://localhost:8089/.

### A Few Helpful Commands

Updates to the applications can be run with a few different commands. Here's what I use

* `helm upgrade locust-es-test locust`

## Unleash the Chaos

> This assumes everything is setup as it was done above. Some code will run locally and some will run on the kube-shell host. Make sure http://localhost:8089/ correctly connects to [Locust](#run-locust) and http://localhost:5601/app/monitoring connects to [Kibana](#run-kibana).

### Chaos by Hand

Generate a mixed load on the cluster with `curl localhost:8089/swarm -X POST -F locust_count=100 -F hatch_rate=10` (or use the Locust UI). In [Kibana](http://localhost:5601/app/monitoring) open the monitoring view and watch the overall cluster overview and the node view. Everything should be in a green state. Indexing rate should be around 100 RPS (Requests Per Second) for the primaries and 200 RPS total. Search rate should be around 50 RPS.

Let this run for a few minutes and then capture a snapshot of the stats from Locust (or see the UI). To get the basic stats that are shown in the UI use `curl -s http://localhost:8089/stats/requests/csv`. This should show 0 failures for any of the endpoints and median response times in the low 10s of milliseconds. A distribution of the response times is available via `curl -s http://localhost:8089/stats/distribution/csv`. 99th percentile should be around 100 ms with max at a few hundred ms.

Now lets break something and see how everything responds. For the first test a single data node process will be stopped in an ungraceful manner. Before stopping the process this will reset the stats captured on the load test. After a minute this will display the post-chaos stats as seen from the load test client.
TODO: This had a minor impact with ES 5.6.1. Rerun with 2.4.x which showed a ~90 second impact and compare results. Also test with ES 6.x for an additional comparison. Also need a better way to show the impact. Marvel doesn't seem to have enough detail.

```
curl -s http://localhost:8089/stats/reset \
  && kubectl exec \
    $(kubectl get pods | grep es-test-helm-elasticsearch-data \
      | sort -n -k4 | head -n1 | awk '{print $1}') \
    -- pkill -9 java \
  ; sleep 60s \
  ; curl -s http://localhost:8089/stats/requests/csv ; echo "" \
  ; curl -s http://localhost:8089/stats/distribution/csv
```

Next lets stop a master node.
TODO: Also capture better impact data. With 5.6.1 it initially looks like a very low impact event.

```
curl -s http://localhost:8089/stats/reset \
  && kubectl exec \
    $(kubectl get pods | grep es-test-helm-elasticsearch-master \
      | sort -n -k4 | head -n1 | awk '{print $1}') \
    -- pkill -9 java \
  ; sleep 60s \
  ; curl -s http://localhost:8089/stats/requests/csv ; echo "" \
  ; curl -s http://localhost:8089/stats/distribution/csv
```
