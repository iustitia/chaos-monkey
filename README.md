# Chaos Monkey

This is simple app that tests pods recovery after random failure.
There are two sets of helm charts: **chaos-monkey** which is actual application and **hello-world** 
which creates simple input pods for chaos-monkey to consume.


## Configuration:
To set namespace change namespace in which pods will be terminated, change *namespace* setting in charts/chaos-monkey/values.yaml under *app.env.namespace*.

To set interval how often random termination will be performed, change *interval* setting in charts/chaos-monkey/values.yaml under *app.env.interval*.


## How to start

Start minikube with suggested resources.
Whole setup was tested on Mac OSX Catalina (version 10.15.7). Should work in any other operating system, without many changes.

    ./script/init.sh

Spawn test services (nginx containers named *hello-world* will be created) for chaos monkey to kill.

    ./script/spawn.sh


To deploy actual application on minikube, run:

    ./script/run.sh


To observe pods behaviour see:

    kubectl get all --namespace hello-namespace

or watch logs from chaos-monkey container:

    kubectl logs -f pod/chaos-monkey-<hash>

Get container id from:

    kubectl get all | grep pod/chaos-monkey

    
## Metrics

Run below code and open **http://127.0.0.1:8080** to see metrics

    export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=chaos-monkey,app.kubernetes.io/instance=chaos-monkey" -o jsonpath="{.items[0].metadata.name}")
    kubectl --namespace default port-forward $POD_NAME 8080:8000

## Clean up

To remove all deployments and turn off minikube:

    helm uninstall chaos-monkey
    helm uninstall hello-world

    minikube stop && minikube delete