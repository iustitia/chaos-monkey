#!/usr/bin/env bash

eval $(minikube docker-env)

docker build . -t monkey-base
docker tag monkey-base localhost:5000/monkey-base:0.1.0


helm delete chaos-monkey

helm install chaos-monkey charts/chaos-monkey

kubectl port-forward service/chaos-monkey 8000:8000

kubectl get all

