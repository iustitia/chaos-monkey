import random
import sys
import os
from time import sleep

import urllib3
from kubernetes import client, config
import logging
from prometheus_client import Counter, start_http_server
import json_log_formatter


def get_logger(name):
    _logger = logging.getLogger(name)
    _logger.setLevel(logging.INFO)
    formatter = json_log_formatter.JSONFormatter()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger


def serve_metrics():
    logger.debug('serve metrics')
    start_http_server(8000)


logger = get_logger(__name__)


class ChaosMonkey:

    def __init__(self):
        self.c = Counter('killed_pods', 'Pods killed by Chaos Monkey', ['podlabel'])

        self.interval = os.getenv('interval')
        self.namespace = os.getenv('namespace')

        config.load_incluster_config()
        self.v1 = self.check_if_namespace_ok()

    def check_if_namespace_ok(self):
        v1 = client.CoreV1Api()
        namespaces = v1.list_namespace(watch=False)
        ns = [x.metadata.name for x in namespaces.items]
        if self.namespace not in ns:
            msg = f"Namespace '{self.namespace}' doesn't exist in current cluster."
            logging.warning(msg)
            raise Exception(msg)
        return v1

    def run(self):
        try:
            ret = self.v1.list_namespaced_pod(namespace=self.namespace, watch=False)
        except (urllib3.exceptions.NewConnectionError, ConnectionRefusedError):
            logger.warning(f"No pods running in namespace '{self.namespace}'. Terminating chaos monkey...")
            return

        if not ret.items:
            logger.warning(f"No pods running in namespace '{self.namespace}'. Terminating chaos monkey...")
            return

        pod = random.choice(ret.items)
        self.c.labels(podlabel=pod.metadata.labels['app.kubernetes.io/name']).inc()
        pod_name = pod.metadata.name

        logger.info(f"Turning off pod '{pod_name}'")

        self.v1.delete_namespaced_pod(pod.metadata.name, self.namespace)
        logger.info(f"Pod '{pod_name}' turned off")

    def get_wait_time(self):
        return int(self.interval) * 60


if __name__ == "__main__":

    cm = ChaosMonkey()
    serve_metrics()

    while True:
        cm.run()
        sleep(cm.get_wait_time())
