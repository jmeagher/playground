import datetime
import glob
import os
import random
import requests
import sys
import time
import traceback

from locust import HttpLocust, TaskSet, task

timeout = (0.5, 1.0)
corpus_glob = os.environ["CORPUS_GLOB"]
all_files = glob.glob(corpus_glob)

test_index = os.environ.get("TEST_INDEX", "load_test")

simple_queries = [
    'romeo', 'thou', 'laertes', 'to be',
    'random:10', 'my_id:100',
    'random:50 AND data_type:medium_cardinality_insert'
]

monitoring_es = os.environ.get("MONITORING_ES_URL", None)
print "Monitoring_es = '%s'" % monitoring_es

def monitored(func):
    def wrapper(*arg, **kw):
        timestamp = datetime.datetime.utcnow().isoformat()
        start = time.time()
        success = False
        reason = ""
        try:
            success, reason = func(*arg, **kw)
        except:
            success = False
            reason = "Something unknown in the wrapper: " + str(traceback.format_exc())
        end = time.time()
        if monitoring_es:
            requests.request('POST', monitoring_es, timeout=(10,30), json={
              "timestamp": timestamp,
              "results_timestamp": datetime.datetime.utcnow().isoformat(),
              "response_time": (end-start),
              "test": func.__name__,
              "success": success,
              "reason": reason,
            })
        return success
    return wrapper

class MixedElasticSearchLoad(TaskSet):

    def on_start(self):
        corpus_file = random.choice(all_files)
        raw = open(corpus_file).readlines()
        # Cleanup the ouptut
        self.corpus = [ l.strip() for l in raw if len(l) > 2]

    @task(100)
    @monitored
    def low_cardinality_insert(self):
        return self._do_insert(random.randint(0,100), "low_cardinality_insert")

    @task(100)
    @monitored
    def medium_cardinality_insert(self):
        return self._do_insert(random.randint(0,10000), "medium_cardinality_insert")

    @task(1000)
    @monitored
    def high_cardinality_insert(self):
        return self._do_insert(random.randint(0,10000000), "high_cardinality_insert")

    @task(100)
    @monitored
    def simple_search(self):
        return self._do_search("simple_search", simple_search=random.choice(simple_queries))

    def _do_search(self, name, simple_search=None, post_search=None):
        if simple_search:
            url = "/%s/_search?q=%s" % (test_index, simple_search)
        else:
            url = "/%s/_search" % test_index
        with self.client.get(url, name=name,
            json=post_search, timeout=timeout, catch_response=True) as response:
          return self._do_validation(response)

    def _do_insert(self, id, name):
        line = random.choice(self.corpus)
        data = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "line": line,
            "my_id": id,
            "random": random.randint(0,1000),
            "data_type": name,
        }
        with self.client.put(
            "/%s/test/%s-%s" % (test_index, name, id),
            json=data, name=name, timeout=timeout, catch_response=True) as response:
          return self._do_validation(response, expected_response_codes=[200,201])

    def _do_validation(self, response, expected_response_codes=[200]):
        successful_request = False
        failure_reason = ""
        try:
            response.raise_for_status()
            try:
                out = response.json()
            except (ValueError) as e:
                failure_reason = "Didn't get json as a response, status: %s  text: %s" % (response.status_code, response.text)
                response.failure(failure_reason)
            if not response.status_code in expected_response_codes:
                failure_reason = ("Expected response code %s but got %s instead" %
                  (expected_response_codes, response.status_code) )
                response.failure(failure_reason)
            elif not "_shards" in out:
                failure_reason = ("No _shards information is available")
                response.failure(failure_reason)
            else:
              shards = out["_shards"]
              successful = shards.get("successful", -1)
              failed = shards.get("failed", 999)
              if successful <= 0:
                  failure_reason = ("Expected successful shards, but got %s instead" % str(successful) )
                  response.failure(failure_reason)
              elif failed > 0:
                  failure_reason = ("Expected no failed shards, but got %s instead" % str(failed) )
                  response.failure(failure_reason)
              else:
                  successful_request = True
                  response.success()
        except:
            failure_reason = ("Unknown exception: " + str(traceback.format_exc()))
            response.failure(failure_reason)
        return (successful_request, failure_reason)


class ElasticSearchUser(HttpLocust):
    task_set = MixedElasticSearchLoad
    min_wait = 900
    max_wait = 1000
