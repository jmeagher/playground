
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
	kubectl get pod --all-namespaces=true | grep tiller | grep '1/1' || \
	  (echo "Waiting a little longer" ; sleep 30s ; \
		  kubectl get pod --all-namespaces=true | grep tiller | grep '1/1' || \
			(echo "Waiting a bit longer"; sleep 60s) ; \
			kubectl get pod --all-namespaces=true | grep tiller | grep '1/1' \
		)

start_shell: start_gke
	kubectl get pod | grep kube-shell || \
	  kubectl run --image jpmeagher/kube-shell:latest kube-shell

check_shell: start_shell
	kubectl get pod | grep kube-shell | grep '1/1' || \
	  (echo "Waiting a little longer" ; sleep 30s ; \
		kubectl get pod | grep kube-shell | grep '1/1')


# ###############################################
# The testing infrastructure pieces
test_components: start_test_es forward_kibana forward_locust

start_test_es: check_tiller
	helm list | grep es-test | grep helm-elasticsearch || \
	  (echo "Launching the test ES cluster" ; helm install helm-elasticsearch --name es-test)

start_kibana: start_gke
	kubectl get pod | grep es-test-kibana || kubectl create -f kibana/kibana.yaml

check_kibana: start_kibana
	kubectl get pod | grep es-test-kibana | grep '1/1' || \
		(echo "Waiting a little longer" ; sleep 30s ; \
		kubectl get pod | grep es-test-kibana | grep '1/1')

forward_kibana: check_kibana
	pkill -f 'kubectl port-forward es-test-kibana' \
	  ; kubectl port-forward $(shell kubectl get pods | \
		   grep es-test-kibana | cut -f 1 -d' ') 5601 &

start_locust: check_tiller start_monitoring_es
	helm list | grep locust || helm install -n locust-es-test locust

check_locust: start_locust
	kubectl get pod | grep locust-es-test-master | grep '1/1' || \
	  (echo "Waiting a little longer" ; sleep 30s ; \
		kubectl get pod | grep locust-es-test-master | grep '1/1')

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

chaos_stop_data_node:
	curl -s http://localhost:8089/stats/reset \
	  && kubectl exec \
	    $(shell kubectl get pods | grep es-test-helm-elasticsearch-data \
	      | sort -n -k4 | head -n1 | cut -f 1 -d' ') \
	    -- pkill -9 java \
	  ; sleep 60s \
	  ; curl -s 'http://localhost:8089/stats/requests/csv' ; echo "" \
	  ; curl -s 'http://localhost:8089/stats/distribution/csv'

chaos_stop_master_node:
	curl -s http://localhost:8089/stats/reset \
	  && kubectl exec \
	    $(shell kubectl get pods | grep es-test-helm-elasticsearch-master \
	      | sort -n -k4 | head -n1 | cut -f 1 -d' ') \
	    -- pkill -9 java \
	  ; sleep 60s \
	  ; curl -s 'http://localhost:8089/stats/requests/csv' ; echo "" \
	  ; curl -s 'http://localhost:8089/stats/distribution/csv'
