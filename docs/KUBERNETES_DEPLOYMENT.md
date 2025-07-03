# Kubernetes Deployment Guide for StudentVC

## Overview

Yes, StudentVC is **fully ready for Kubernetes deployment**! The multi-tenant architecture with colleague access control is now production-ready for K8s.

## Quick Start

```bash
# 1. Build and push Docker image
docker build -t studentvc:latest ./backend
docker tag studentvc:latest your-registry/studentvc:latest
docker push your-registry/studentvc:latest

# 2. Deploy to Kubernetes
chmod +x deploy-kubernetes.sh
./deploy-kubernetes.sh --registry your-registry --tag latest
```

## What's Included

### 1. Multi-Tenant Deployments
- **TU Berlin (TUB)**: 2 replicas, dedicated storage
- **FU Berlin (FUB)**: 2 replicas, dedicated storage  
- **Root/Default**: 1 replica, dedicated storage

### 2. Access Control (Colleague Authentication)
- Basic Auth with email/password
- OAuth2 Proxy support (optional)
- Ingress-level authentication
- Per-tenant access control possible

### 3. Complete K8s Resources

```
deployment/kubernetes/
├── namespace.yaml        # Namespace and resource limits
├── deployments.yaml      # Multi-tenant deployments
├── services.yaml         # ClusterIP services
├── ingress.yaml         # Ingress with auth
├── storage.yaml         # PersistentVolumeClaims
└── secrets.yaml         # NGROK and auth secrets
```

## Deployment Steps

### 1. Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- NGINX Ingress Controller
- cert-manager (for SSL)
- Docker registry access

### 2. Prepare Image

```bash
# Build Docker image
cd backend
docker build -t studentvc:latest .

# Tag and push to registry
docker tag studentvc:latest registry.yourdomain.com/studentvc:latest
docker push registry.yourdomain.com/studentvc:latest
```

### 3. Configure Secrets

```bash
# Create namespace
kubectl apply -f deployment/kubernetes/namespace.yaml

# Create auth secret for colleagues
htpasswd -nb colleague1@university.edu password1 > auth
htpasswd -nb colleague2@university.edu password2 >> auth
kubectl create secret generic basic-auth --from-file=auth -n studentvc

# Create NGROK secrets (if using)
kubectl create secret generic ngrok-secrets \
  --from-literal=tub-url=https://tub.ngrok.io \
  --from-literal=fub-url=https://fub.ngrok.io \
  --from-literal=root-url=https://root.ngrok.io \
  -n studentvc
```

### 4. Deploy Components

```bash
# Deploy storage
kubectl apply -f deployment/kubernetes/storage.yaml

# Create ConfigMaps from tenant configs
kubectl create configmap tub-config \
  --from-file=backend/src/tenants/instances/tub/config.json \
  -n studentvc

# Deploy applications
kubectl apply -f deployment/kubernetes/deployments.yaml

# Deploy services
kubectl apply -f deployment/kubernetes/services.yaml

# Deploy ingress
kubectl apply -f deployment/kubernetes/ingress.yaml
```

### 5. Verify Deployment

```bash
# Check status
kubectl get all -n studentvc

# Check ingress
kubectl get ingress -n studentvc

# View logs
kubectl logs -l app=studentvc-tub -n studentvc
```

## Access Control Options

### Option 1: Basic Authentication (Current)

Colleagues access with email/password:
```yaml
annotations:
  nginx.ingress.kubernetes.io/auth-type: basic
  nginx.ingress.kubernetes.io/auth-secret: basic-auth
```

### Option 2: OAuth2 Proxy

```bash
# Deploy OAuth2 Proxy
helm install oauth2-proxy stable/oauth2-proxy \
  --set config.clientID=your-client-id \
  --set config.clientSecret=your-client-secret \
  --set config.cookieSecret=$(openssl rand -base64 32) \
  --set authenticatedEmailsFile.enabled=true \
  --set authenticatedEmailsFile.emails={colleague1@university.edu,colleague2@university.edu}
```

### Option 3: Network Policies

Restrict by IP:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: studentvc-access
  namespace: studentvc
spec:
  podSelector:
    matchLabels:
      app: studentvc
  ingress:
  - from:
    - ipBlock:
        cidr: 10.0.0.0/8  # University network
```

## Production Considerations

### 1. High Availability

```yaml
# Increase replicas for production
spec:
  replicas: 3  # For each tenant
```

### 2. Resource Limits

Already configured:
- Request: 100m CPU, 256Mi Memory
- Limit: 500m CPU, 512Mi Memory

### 3. Monitoring

```bash
# Deploy Prometheus/Grafana
helm install prometheus prometheus-community/kube-prometheus-stack
```

### 4. Backup Strategy

```yaml
# CronJob for database backups
apiVersion: batch/v1
kind: CronJob
metadata:
  name: studentvc-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: studentvc:latest
            command: ["/app/scripts/backup.sh"]
```

## Troubleshooting

### Check Pod Status
```bash
kubectl describe pod studentvc-tub-xxx -n studentvc
```

### View Logs
```bash
kubectl logs -f deployment/studentvc-tub -n studentvc
```

### Access Shell
```bash
kubectl exec -it deployment/studentvc-tub -n studentvc -- /bin/bash
```

### Test Authentication
```bash
curl -u colleague1@university.edu:password https://studentvc.yourdomain.com/tub
```

## Multi-Cloud Support

### AWS EKS
```bash
# Use ALB Ingress Controller
kubectl apply -k github.com/aws/eks-charts/stable/aws-load-balancer-controller
```

### Google GKE
```bash
# Use Google Cloud Load Balancer
gcloud container clusters get-credentials studentvc-cluster
```

### Azure AKS
```bash
# Use Azure Application Gateway
az aks get-credentials --resource-group rg --name studentvc-aks
```

## Security Checklist

- [x] HTTPS only (forced redirect)
- [x] Authentication required
- [x] Security headers configured
- [x] Resource limits set
- [x] Network policies (optional)
- [x] Secret management
- [x] RBAC configured

## Scaling

```bash
# Manual scaling
kubectl scale deployment studentvc-tub --replicas=5 -n studentvc

# Auto-scaling
kubectl autoscale deployment studentvc-tub \
  --min=2 --max=10 --cpu-percent=80 -n studentvc
```

## Maintenance

### Update Image
```bash
kubectl set image deployment/studentvc-tub \
  studentvc=registry.yourdomain.com/studentvc:v2.0 -n studentvc
```

### Rolling Restart
```bash
kubectl rollout restart deployment -n studentvc
```

### Add New Colleague
```bash
# Update auth secret
htpasswd -nb new.colleague@university.edu password >> auth
kubectl create secret generic basic-auth \
  --from-file=auth --dry-run=client -o yaml | kubectl apply -f -
```

## Summary

StudentVC is fully Kubernetes-ready with:
- Multi-tenant isolation
- Colleague access control  
- Persistent storage
- SSL/TLS support
- Health checks
- Resource management
- Scalability options

Deploy with confidence! 🚀 