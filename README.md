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

## Add service Mesh (Consul)

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
```

```bash
helm upgrade --install consul hashicorp/consul --create-namespace --namespace consul --values helm/values-consul.yml
```

Access Consul UI:

```bash
kubectl port-forward service/consul-server --namespace consul 8500:8500
```

### Add consul sidecar

After installing consul, we need to change the configuration settings to annotates where should sidecar be deployed.

_Note:_
We could bypass this steps by settings the default values in the helm chart.

```yml
connectInject:
  enabled: true # Enable automatic injection of the Consul Connect sidecar
  default: true # Automatically inject sidecar on all pods
```

But, we want to be able to choose which service should be injected. So we will use annotations.

```yml
metadata:
  ...
  annotations:
    # https://www.consul.io/docs/platf orm/k8s/run.html#annotations
    'consul.hashicorp.com/connect-inject': 'true'
    'consul.hashicorp.com/connect-service-upstreams': 'beta-service:50100,charlie-service:50200'
```

As the sidecar is now routing request, we have to make our application send request to the sidecar instead of the service directly.

For this, we send traffic on the localhost port of our choice, that have to be the port where the service is listening, and of courses, must be unique.

```yml
env:
  - name: BETA_URL
    value: 'http://localhost:50100'
  - name: CHARLIE_URL
    value: 'http://localhost:50200'
```

After making change on your deployment and service, you will have to redeploy.

```bash
kubectl apply -f ./k8s
```

At this steps, all our services can communicate with each other using the sidecar.

### Restrict communication between services

Now, we want to restrict communication between services. For this, we will use intentions.
Restricting communication between services will empower our security policies by instauring a zero trust model.

By default, consul allow all services to communicate with each other.

We need to update our consul installation to change this behavior.

```yml
global:
  ...
  acls:
    manageSystemACLs: true
```

Also, we will change this behavior by adding the following intention:

```yml
apiVersion: consul.hashicorp.com/v1alpha1
kind: ServiceIntentions
metadata:
  name: deny-all
spec:
  destination:
    name: '*'
  sources:
    - name: '*'
      action: deny
```

```bash
kubectl apply -f ./k8s/consul/deny-all-communications.yml
```

Now, no services can communicate with each other. We will now allow communication from alpha to beta and charlie.

```bash
kubectl apply -f ./k8s/consul/allow-alpha-to-others.yml
```
