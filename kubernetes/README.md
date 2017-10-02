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
 --num-nodes 1 --machine-type n1-standard-4 \
 --cluster-version 1.7.5 --preemptible

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

With this configuration the ElasticSearch cluster is only available from inside the Kubernetes cluster. It is a bit tough to directly access ElasticSearch with this setup so it can be a challenge to confirm everything is working. I use a Docker container with the utilities and dotfiles I am used to already installed. See docker/kube-shell/ for more details about this. Start a shell with `kubectl run --attach --rm=true -i --restart=Never --image jpmeagher/kube-shell:latest kube-shell` or access one already running in your cluster.

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

Start the basic Locust test that is included with `helm install -n locust-es-test locust`. Connect to this with `kubectl port-forward $(kubectl get pods | grep locust-es-test-master | awk '{print $1}') 8089 8089`
