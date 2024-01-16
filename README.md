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

## Add Observability stack

### Install OpenTelemetry

OpenTelemetry is an observability framework for cloud-native software.

OpenTelemetry provides a single set of APIs, libraries, agents, and collector services to capture distributed traces and metrics from your application. It's an OpenSource project that is part of the Cloud Native Computing Foundation (CNCF).

```bash
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update
```

The OpenTelemetry Operator is a Kubernetes operator that manages all resources and services required to run OpenTelemetry in a Kubernetes cluster.

```bash
helm upgrade --install opentelemetry-operator open-telemetry/opentelemetry-operator --namespace opentelemetry-operator-system --create-namespace
```

Now you can install the OpenTelemetry Collector using the OpenTelemetry Operator.

```bash
helm upgrade --install opentelemetry-collector open-telemetry/opentelemetry-collector -f helm/values-opentelemetry-collector.yml --namespace observability --create-namespace
```

At this step, your OpenTelemetry is installed in the cluster but not configured to instrument your application.

#### Using OpenTelemetry Auto-Instrumentation

OpenTelemetry provides an auto-instrumentation library for Python. This library will automatically instrument your application to collect traces and metrics.

This instrumentation can be installed using a CRD provided by the OpenTelemetry Operator.

```bash
kubectl apply -f k8s/CRDs/opentelemetry/python-instrumentation.yml -n observability
```

You will have to change your kubernetes deployment manifest to indicate that you want OpenTelemetry to auto-instrument your application.

```yaml
# Your deployment manifest...
template:
  metadata:
    annotations:
      instrumentation.opentelemetry.io/inject-python: 'observability/python-instrumentation'
```

Now apply the changes to your deployment

```bash
kubectl apply -f k8s/
```

_At this point, you may have to restart your pods manually and wait for the auto-instrumentation to be applied._

### Adding Jaeger

Jaeger is a distributed tracing system released as open source by Uber Technologies. It is used for monitoring and troubleshooting microservices-based distributed systems.

### Operator

For simplicity, we will install Jaeger using Helm.

```bash
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update
```

```bash
helm upgrade --install jaeger-operator jaegertracing/jaeger-operator -f helm/values-jaeger-operator.yml --namespace observability --create-namespace
```

At this step, you will need to create a CRD to deploy Jaeger.

```bash
kubectl apply -f k8s/CRDs/jaeger/jaeger.yml --namespace observability
```

Now you can access to your APM dashboard by running the following command:

```bash
kubectl port-forward svc/jaeger-query 16686:16686 --namespace observability
```
