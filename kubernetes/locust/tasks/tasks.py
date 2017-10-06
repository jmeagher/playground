import datetime
import glob
import os
import random
import time

from locust import HttpLocust, TaskSet, task

timeout = (2, 20)
corpus_glob = os.environ["CORPUS_GLOB"]
all_files = glob.glob(corpus_glob)

test_index = os.environ.get("TEST_INDEX", "load_test")

simple_queries = [
    'romeo', 'thou', 'laertes', 'to be',
    'random:10', 'my_id:100',
    'random:50 AND data_type:medium_cardinality_insert'
]

class MixedElasticSearchLoad(TaskSet):

    def on_start(self):
        corpus_file = random.choice(all_files)
        raw = open(corpus_file).readlines()
        # Cleanup the ouptut
        self.corpus = [ l.strip() for l in raw if len(l) > 2]

    @task(100)
    def low_cardinality_insert(self):
        self._do_insert(random.randint(0,100), "low_cardinality_insert")

    @task(100)
    def medium_cardinality_insert(self):
        self._do_insert(random.randint(0,10000), "medium_cardinality_insert")

    @task(1000)
    def high_cardinality_insert(self):
        self._do_insert(random.randint(0,10000000), "high_cardinality_insert")

    @task(100)
    def simple_search(self):
        self._do_search("simple_search", simple_search=random.choice(simple_queries))

    def _do_search(self, name, simple_search=None, post_search=None):
        if simple_search:
            url = "/%s/_search?q=%s" % (test_index, simple_search)
        else:
            url = "/%s/_search" % test_index
        response = self.client.get(url, name=name,
            json=post_search, timeout=timeout)
        self._do_validation(response)

    def _do_insert(self, id, name):
        line = random.choice(self.corpus)
        data = {
            "time1": int(time.time()),
            "time2": 1000*int(time.time()),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "line": line,
            "my_id": id,
            "random": random.randint(0,1000),
            "data_type": name,
        }
        response = self.client.put(
            "/%s/test/%s-%s" % (test_index, name, id),
            json=data, name=name, timeout=timeout)
        self._do_validation(response)

    def _do_validation(self, response):
        assert response.status_code == 200
        out = response.json()
        shards = out["_shards"]
        assert shards["successful"] > 0
        assert shards["failed"] == 0


class ElasticSearchUser(HttpLocust):
    task_set = MixedElasticSearchLoad
    min_wait = 900
    max_wait = 1000
