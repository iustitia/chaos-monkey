#!/usr/bin/env bash

CPUS=4
RAM=8192
DISK_SIZE=25000mb

if minikube status ; then
    echo "Minikube is already running... Unable to initialize minikube.";
else
    echo "Starting minikube...";

    if [[ $OSTYPE == darwin* ]]; then
        minikube start \
            --cpus $CPUS \
            --memory $RAM \
            --disk-size $DISK_SIZE  \
            --driver=hyperkit #\
            # --extra-config=apiserver.authorization-mode=AlwaysAllow   # start minikube without RBAC, but it doesn't work on my setup, hence workaround below
    else
        minikube start \
        --cpus $CPUS \
        --memory $RAM \
        --disk-size $DISK_SIZE #\
        # --extra-config=apiserver.authorization-mode=AlwaysAllow   # start minikube without RBAC, but it doesn't work on my setup, hence workaround below
    fi
fi

sleep 5


# turn off RBAC - workaround
minikube ssh 'sudo cat /etc/kubernetes/manifests/kube-apiserver.yaml | sed -r "s/--authorization-mode=.+/--authorization-mode=AlwaysAllow/g" | sudo tee /etc/kubernetes/manifests/kube-apiserver.yaml'

