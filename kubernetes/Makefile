
setup: infrastructure test_components

complete_shutdown:
	gcloud container clusters delete es-test

# ###############################################
# The basics to get the infrastructure up and running
infrastructure: forward_monitoring_kibana helm_init start_shell

start_gke:
	kubectl get nodes || ( \
	  echo "Can't connect to cluster, starting new one, this will take a few minutes" \
	  && gcloud beta container clusters create es-test \
	    --zone us-central1-c \
	    --additional-zones us-central1-b \
	    --num-nodes 2 --machine-type n1-standard-2 \
			--cluster-version 1.7.8 \
	  && gcloud container clusters get-credentials es-test )
		# --preemptible \

start_monitoring_svc: start_gke
	kubectl get svc | grep monitoring-es-svc || \
	  kubectl create -f monitoring/monitoring-es-svc.yaml

start_monitoring_es: start_monitoring_svc
	kubectl get pods | grep monitoring-es \
	  || (echo "Monitoring cluster is not running, starting it now" ; \
		  kubectl create -f monitoring/monitoring-es-cluster.yaml)

start_monitoring_kibana: start_monitoring_svc
	kubectl get pod | grep monitoring-kibana || kubectl create -f monitoring/monitoring-kibana.yaml

forward_monitoring_kibana: start_monitoring_kibana start_monitoring_es
		pkill -f 'kubectl port-forward monitoring-kibana' \
		  ; kubectl port-forward $(shell kubectl get pods | \
			   grep monitoring-kibana | cut -f 1 -d' ') 15601:5601 &

helm_init: start_gke
	kubectl get pod --all-namespaces=true | grep tiller \
	  || ( echo "Tiller is not running, running helm_init" ; helm init)

check_tiller: helm_init
	./bin/pod-running tiller 10 10

start_shell: start_gke
	kubectl get pod | grep kube-shell || \
	  kubectl run --image jpmeagher/kube-shell:latest kube-shell

check_shell: start_shell
	./bin/pod-running kube-shell 10 10


# ###############################################
# The testing infrastructure pieces
test_components: start_test_es forward_kibana forward_locust forward_test_es

start_test_es: check_tiller
	helm list | grep es-test | grep helm-elasticsearch || \
	  (echo "Launching the test ES cluster" ; helm install helm-elasticsearch --name es-test)

check_test_es: start_test_es
	./bin/pod-running es-test-helm-elasticsearch-master 10 10

forward_test_es: check_test_es
	pkill -f 'kubectl port-forward es-test-helm-elasticsearch-client' \
	  ; kubectl port-forward $(shell ./bin/get-pod es-test-helm-elasticsearch-client) 9200 &

start_kibana: start_gke
	kubectl get pod | grep es-test-kibana || kubectl create -f kibana/kibana.yaml

check_kibana: start_kibana
	./bin/pod-running es-test-kibana 10 10

forward_kibana: check_kibana
	pkill -f 'kubectl port-forward es-test-kibana' \
	  ; kubectl port-forward $(shell kubectl get pods | \
		   grep es-test-kibana | cut -f 1 -d' ') 5601 &

start_locust: check_tiller start_monitoring_es
	helm list | grep locust || helm install -n locust-es-test locust

check_locust: start_locust
	./bin/pod-running locust-es-test-master 10 10

forward_locust: check_locust
	pkill -f 'kubectl port-forward locust-es-test-master' \
	  ; kubectl port-forward $(shell kubectl get pods | \
		   grep locust-es-test-master | cut -f 1 -d' ') 8089 &

delete_locust:
	helm delete --purge locust-es-test && sleep 3s

reload_locust: delete_locust forward_locust


# ######################################
# Actual test stuff

locust_light_load: forward_locust
	sleep 1s; curl localhost:8089/swarm -X POST -F locust_count=20 -F hatch_rate=1

chaos_pkill_data_node:
	curl -s http://localhost:8089/stats/reset \
		; sleep 60s \
		; ./bin/locust-stats \
	  && kubectl exec \
	    $(shell ./bin/get-pod es-test-helm-elasticsearch-data -nk4) \
	    -- pkill -9 java \
	  ; sleep 60s \
		; ./bin/locust-stats

chaos_pkill_active_master_node:
	curl -s http://localhost:8089/stats/reset \
		; sleep 60s \
		; ./bin/locust-stats \
	  && kubectl exec \
	    $(shell ./bin/active-master) \
	    -- pkill -9 java \
	  ; sleep 60s \
	  ; ./bin/locust-stats


chaos_network_degredation_active_master_node:
	curl -s http://localhost:8089/stats/reset \
		; sleep 60s \
		; ./bin/locust-stats \
		; curl -s http://localhost:8089/stats/reset \
	  && kubectl exec \
	    $(shell ./bin/active-master) -c toxiproxy \
	    -- /bin/sh -c \
				'/go/bin/toxiproxy-cli toxic add -n limited -t bandwidth -a rate=1 es_transport \
				; /go/bin/toxiproxy-cli toxic add -n latency -t latency -a latency=30000 es_transport \
				; echo "Starting Chaos" ; sleep 240s ; echo "Ending Chaos" \
				; /go/bin/toxiproxy-cli toxic delete -n limited es_transport \
				; /go/bin/toxiproxy-cli toxic delete -n latency es_transport' \
	  ; sleep 3s \
	  ; ./bin/locust-stats

chaos_network_degredation_data_node:
	curl -s http://localhost:8089/stats/reset \
		; sleep 60s \
		; ./bin/locust-stats \
		; curl -s http://localhost:8089/stats/reset \
	  && kubectl exec \
	    $(shell ./bin/get-pod es-test-helm-elasticsearch-data) -c toxiproxy \
	    -- /bin/sh -c \
				'/go/bin/toxiproxy-cli toxic add -n limited -t bandwidth -a rate=1 es_transport \
			 	; /go/bin/toxiproxy-cli toxic add -n latency -t latency -a latency=30000 es_transport \
				; echo "Starting Chaos" ; sleep 240s ; echo "Ending Chaos" \
				; /go/bin/toxiproxy-cli toxic delete -n limited es_transport \
				; /go/bin/toxiproxy-cli toxic delete -n latency es_transport' \
	  ; sleep 3s \
	  ; ./bin/locust-stats
