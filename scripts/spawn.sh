#!/usr/bin/env bash

# create some pods to kill

kubectl create namespace hello-namespace
helm install hello-world charts/hello-world --namespace hello-namespace
