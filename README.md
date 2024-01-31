# POC Kube practice stuff

This repository is a POC to practice some kubernetes stuff. It contains a simple application with 3 services (alpha, beta and charlie).

## Get started

### Requirements

- Docker
- Kind
- Kubectl
- Helm

### Create your kubernetes cluster

For this POC we will use kind to create a kubernetes cluster. Kind is a tool that allows you to run local kubernetes clusters using docker container “nodes”. It is a great tool to test your kubernetes configuration.

```bash
export KIND_CLUSTER=poc-kube-practice-stuff
kind create cluster --name=$KIND_CLUSTER --config=./kind/cluster.yml
```

## Build the application

The alpha service is a simple web application that displays a sentences made of one noun and one adjective. The beta service is a simple web application that return a random adjectives. The charlie service is a simple web application that return a random noun.

### Build docker images

Build docker images and add them in the kind cluster registry to simplify deployment

```bash
for service in alpha beta charlie; do docker build -t leofvo/$service:1.0.0 ./apps/$service && kind load docker-image leofvo/$service:1.0.0 -n $KIND_CLUSTER; done
```

### Deploy application

Deploy the application in the kubernetes cluster

```bash
kubectl apply -f ./k8s
```

Now you can create a port-forward to the alpha service to access the application from your browser.

```bash
kubectl port-forward service/alpha-service 8080:80
```

The application is now available on [http://localhost:8080](http://localhost:8080)

## Installing Istio service mesh

### Setup with helm

```bash
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
```

```bash
kubectl create namespace istio-system
helm install istio-base istio/base -n istio-system --set defaultRevision=default
helm install istiod istio/istiod -n istio-system --wait
```

Now, Istio is installed in your clsuter.

### Installing sidecar on applications

```bash
kubectl label namespace default istio-injection=enabled
```
