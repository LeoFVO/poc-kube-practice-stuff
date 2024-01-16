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

## Add Monitoring stack

### Install dependencies

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.8.2/cert-manager.yaml
```

### Installing Monitoring stack

Kube-Prometheus-Stack is a collection of Kubernetes manifests, Grafana dashboards, and Prometheus rules combined with documentation and scripts to provide easy to operate end-to-end Kubernetes cluster monitoring with Prometheus using the Prometheus Operator.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

```bash
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack -f helm/values-prometheus.yml --namespace monitoring --create-namespace
```

This stack is installing principaly prometheus, grafana. You can access them by creating a portforward:

```bash
# Acccess Prometheus dashboard
kubectl port-forward svc/prometheus-operated 9090:9090 --namespace monitoring

# Acces Grafana dashboard
kubectl port-forward svc/kube-prometheus-stack-grafana 3000:80 --namespace monitoring
```

Prometheus dashboard should be available on [http://localhost:9090](http://localhost:9090)

Grafana dashboard should be available on [http://localhost:3000](http://localhost:3000)

Grafana login: `admin/prom-operator`
