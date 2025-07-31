# Notes App Helm Chart

This Helm chart deploys a scalable microservices-based note-taking application on Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PV provisioner support in the underlying infrastructure (for PostgreSQL persistence)

## Installing the Chart

To install the chart with the release name `my-notes-app`:

```bash
helm install my-notes-app ./helm/notes-app
```

The command deploys the Notes App on the Kubernetes cluster with default configuration. The [Parameters](#parameters) section lists the parameters that can be configured during installation.

## Uninstalling the Chart

To uninstall/delete the `my-notes-app` deployment:

```bash
helm delete my-notes-app
```

## Parameters

### Global parameters

| Name                      | Description                                     | Value |
| ------------------------- | ----------------------------------------------- | ----- |
| `global.imageRegistry`    | Global Docker image registry                    | `""`  |
| `global.imagePullSecrets` | Global Docker registry secret names as an array| `[]`  |
| `global.storageClass`     | Global StorageClass for Persistent Volume(s)   | `""`  |

### Application parameters

| Name                | Description                    | Value        |
| ------------------- | ------------------------------ | ------------ |
| `app.name`          | Application name               | `notes-app`  |
| `app.version`       | Application version            | `1.0.0`      |

### Frontend parameters

| Name                                    | Description                                          | Value           |
| --------------------------------------- | ---------------------------------------------------- | --------------- |
| `frontend.enabled`                      | Enable frontend deployment                           | `true`          |
| `frontend.replicaCount`                 | Number of frontend replicas                          | `2`             |
| `frontend.image.repository`             | Frontend image repository                            | `notes-frontend`|
| `frontend.image.tag`                    | Frontend image tag                                   | `latest`        |
| `frontend.image.pullPolicy`             | Frontend image pull policy                           | `IfNotPresent`  |
| `frontend.service.type`                 | Frontend service type                                | `ClusterIP`     |
| `frontend.service.port`                 | Frontend service port                                | `80`            |
| `frontend.resources.limits.cpu`         | Frontend CPU limit                                   | `200m`          |
| `frontend.resources.limits.memory`      | Frontend memory limit                                | `256Mi`         |
| `frontend.resources.requests.cpu`       | Frontend CPU request                                 | `100m`          |
| `frontend.resources.requests.memory`    | Frontend memory request                              | `128Mi`         |

### Backend parameters

| Name                                           | Description                                          | Value           |
| ---------------------------------------------- | ---------------------------------------------------- | --------------- |
| `backend.enabled`                              | Enable backend deployment                            | `true`          |
| `backend.replicaCount`                         | Number of backend replicas                           | `3`             |
| `backend.image.repository`                     | Backend image repository                             | `notes-backend` |
| `backend.image.tag`                            | Backend image tag                                    | `latest`        |
| `backend.image.pullPolicy`                     | Backend image pull policy                            | `IfNotPresent`  |
| `backend.service.type`                         | Backend service type                                 | `ClusterIP`     |
| `backend.service.port`                         | Backend service port                                 | `8000`          |
| `backend.resources.limits.cpu`                 | Backend CPU limit                                    | `500m`          |
| `backend.resources.limits.memory`              | Backend memory limit                                 | `512Mi`         |
| `backend.resources.requests.cpu`               | Backend CPU request                                  | `250m`          |
| `backend.resources.requests.memory`            | Backend memory request                               | `256Mi`         |
| `backend.autoscaling.enabled`                  | Enable Horizontal Pod Autoscaler                     | `true`          |
| `backend.autoscaling.minReplicas`              | Minimum number of replicas                           | `3`             |
| `backend.autoscaling.maxReplicas`              | Maximum number of replicas                           | `10`            |
| `backend.autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization percentage            | `70`            |
| `backend.autoscaling.targetMemoryUtilizationPercentage` | Target memory utilization percentage      | `80`            |

### Database parameters

| Name                                    | Description                                          | Value                    |
| --------------------------------------- | ---------------------------------------------------- | ------------------------ |
| `database.external`                     | Use external database                                | `false`                  |
| `database.host`                         | Database host                                        | `postgres-service`       |
| `database.port`                         | Database port                                        | `5432`                   |
| `database.name`                         | Database name                                        | `notesdb`                |
| `database.username`                     | Database username                                    | `notesuser`              |

### PostgreSQL parameters

| Name                                    | Description                                          | Value                    |
| --------------------------------------- | ---------------------------------------------------- | ------------------------ |
| `postgresql.enabled`                    | Enable PostgreSQL subchart                           | `true`                   |
| `postgresql.auth.postgresPassword`      | PostgreSQL admin password                            | `postgres`               |
| `postgresql.auth.username`              | PostgreSQL username                                  | `notesuser`              |
| `postgresql.auth.password`              | PostgreSQL password                                  | `notespassword`          |
| `postgresql.auth.database`              | PostgreSQL database name                             | `notesdb`                |

### Ingress parameters

| Name                       | Description                                          | Value        |
| -------------------------- | ---------------------------------------------------- | ------------ |
| `ingress.enabled`          | Enable ingress record generation                     | `true`       |
| `ingress.className`        | IngressClass that will be used                       | `nginx`      |
| `ingress.hosts[0].host`    | Default host for the ingress record                  | `notes.local`|

## Configuration and installation details

### Setting up Ingress

This chart provides support for Ingress resources. If you have an ingress controller installed on your cluster, you can utilize the ingress controller to serve your application.

To enable Ingress integration, set `ingress.enabled` to `true`. The `ingress.hostname` property can be used to set the host name. The `ingress.tls` parameter can be used to add the TLS configuration for this host.

### Setting up TLS

This chart provides support for TLS between the ingress and the backend. To enable TLS, set the `ingress.tls` parameter.

## Troubleshooting

### Check pod status

```bash
kubectl get pods -l app.kubernetes.io/instance=my-notes-app
```

### View logs

```bash
# Backend logs
kubectl logs -l app.kubernetes.io/instance=my-notes-app,app.kubernetes.io/component=backend

# Frontend logs
kubectl logs -l app.kubernetes.io/instance=my-notes-app,app.kubernetes.io/component=frontend

# Database logs
kubectl logs -l app.kubernetes.io/instance=my-notes-app,app.kubernetes.io/name=postgresql
```

### Run tests

```bash
helm test my-notes-app
```
