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


if __name__ == "__main__":

    c = Counter('killed_pods', 'Pods killed by Chaos Monkey', ['podlabel'])

    interval = os.getenv('interval')
    namespace = os.getenv('namespace')

    config.load_incluster_config()

    v1 = client.CoreV1Api()
    namespaces = v1.list_namespace(watch=False)
    ns = [x.metadata.name for x in namespaces.items]
    if namespace not in ns:
        logging.warning(f"Namespace '{namespace}' doesn't exist in current cluster.")
        exit()

    serve_metrics()

    while True:
        try:
            ret = v1.list_namespaced_pod(namespace=namespace, watch=False)
        except (urllib3.exceptions.NewConnectionError, ConnectionRefusedError):
            logger.warning(f"No pods running in namespace '{namespace}'. Terminating chaos monkey...")
            break

        if not ret.items:
            logger.warning(f"No pods running in namespace '{namespace}'. Terminating chaos monkey...")
            break

        pod = random.choice(ret.items)
        c.labels(podlabel=pod.metadata.labels['app.kubernetes.io/name']).inc()
        pod_name = pod.metadata.name

        logger.info(f"Turning off pod '{pod_name}'")

        out = v1.delete_namespaced_pod(pod.metadata.name, namespace)
        logger.info(f"Pod '{pod_name}' turned off")

        sleep(int(interval) * 60)
