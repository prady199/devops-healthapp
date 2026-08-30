# DevOps Healthcare Portal

CI/CD pipeline that builds a Dockerized Flask application and deploys it to
Kubernetes using Jenkins.

## Stack

| Component  | Tool                          |
|------------|-------------------------------|
| Application| Python 3.11 + Flask           |
| Container  | Docker                        |
| Registry   | Docker Hub (`prady/healthapp`)|
| Orchestrator | k3s (Kubernetes)            |
| CI/CD      | Jenkins (declarative pipeline)|
| Infra      | AWS EC2 (Ubuntu)              |

## Pipeline stages

1. **Checkout** - pull source from GitHub
2. **Build Docker Image** - tag with build number and `latest`
3. **Push to Docker Hub** - authenticate with stored credentials
4. **Deploy to Kubernetes** - apply manifests, roll out new image
5. **Verify** - list pods and services

## Kubernetes objects

- `Deployment healthapp` - 2 replicas, readiness probe on `/health`
- `Service healthapp-svc` - NodePort 30080

## Endpoints

| Path      | Purpose                      |
|-----------|------------------------------|
| `/`       | Portal home page             |
| `/health` | JSON health check for probes |

## Access

    http://<EC2-PUBLIC-IP>:30080
