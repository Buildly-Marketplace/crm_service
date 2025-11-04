# ForgeCRM Operations Guide

Deploy ForgeCRM to production environments using Docker, Kubernetes, or other platforms.

## Docker Deployment

### Production Docker Setup

#### 1. Build Production Image

```bash
# Build optimized production image
docker build -f ops/Dockerfile -t forge-crm:1.0.0 .
docker tag forge-crm:1.0.0 forge-crm:latest
```

#### 2. Production Compose

Use the production compose file:

```bash
# Start with production configuration
docker-compose -f ops/docker-compose.yml up -d

# Or with custom environment
docker-compose -f ops/docker-compose.yml \
  --env-file production.env up -d
```

#### 3. Production Environment Variables

Create `production.env`:

```env
# Database Configuration
DATABASE_HOST=your-postgres-host
DATABASE_NAME=crm_production
DATABASE_USER=crm_user
DATABASE_PASSWORD=secure-password-here
DATABASE_PORT=5432

# Security
SECRET_KEY=your-very-long-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,api.yourdomain.com

# Optional: External Services
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=redis-password

# JWT Configuration (if using external auth)
JWT_AUTH_DISABLED=False
JWT_PUBLIC_KEY_RSA_BUILDLY=your-jwt-public-key
JWT_ALLOWED_ISSUER=your-auth-service
```

### Docker Registry Deployment

```bash
# Tag for registry
docker tag forge-crm:latest your-registry.com/forge-crm:1.0.0

# Push to registry
docker push your-registry.com/forge-crm:1.0.0

# Deploy on target server
docker run -d \
  --name forge-crm \
  --env-file production.env \
  -p 8080:8080 \
  your-registry.com/forge-crm:1.0.0
```

## Kubernetes Deployment

### Using Helm (Recommended)

#### 1. Install Helm Chart

```bash
# Add Buildly Helm repository
helm repo add buildly https://charts.buildly.io
helm repo update

# Install ForgeCRM
helm install forge-crm buildly/forge-crm \
  --namespace crm-system \
  --create-namespace \
  --values production-values.yaml
```

#### 2. Custom Values Configuration

Create `production-values.yaml`:

```yaml
# Image configuration
image:
  repository: forge-crm
  tag: "1.0.0"
  pullPolicy: IfNotPresent

# Scaling
replicaCount: 2

# Service configuration
service:
  type: ClusterIP
  port: 8080

# Ingress
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: crm.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: forge-crm-tls
      hosts:
        - crm.yourdomain.com

# Database (external)
postgresql:
  enabled: false
  external:
    host: postgres.yourdomain.com
    port: 5432
    database: crm_production
    username: crm_user
    existingSecret: crm-db-secret
    secretKey: password

# Environment variables
env:
  - name: DEBUG
    value: "False"
  - name: ALLOWED_HOSTS
    value: "crm.yourdomain.com"

# Resources
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

# Health checks
livenessProbe:
  httpGet:
    path: /health/
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

#### 3. Manual Kubernetes Deployment

If not using Helm:

```bash
# Apply Kubernetes manifests
kubectl apply -f ops/k8s/namespace.yaml
kubectl apply -f ops/k8s/configmap.yaml
kubectl apply -f ops/k8s/secret.yaml
kubectl apply -f ops/k8s/deployment.yaml
kubectl apply -f ops/k8s/service.yaml
kubectl apply -f ops/k8s/ingress.yaml
```

### Verify Kubernetes Deployment

```bash
# Check pods
kubectl get pods -n crm-system

# Check service
kubectl get svc -n crm-system

# Check logs
kubectl logs -n crm-system deployment/forge-crm

# Test health endpoint
kubectl port-forward -n crm-system svc/forge-crm 8080:8080
curl http://localhost:8080/health/
```

## Database Operations

### Production Database Setup

#### PostgreSQL Configuration

```sql
-- Create database and user
CREATE DATABASE crm_production;
CREATE USER crm_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE crm_production TO crm_user;

-- Connect to the database
\c crm_production

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS hstore;

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO crm_user;
```

#### Migration in Production

```bash
# Run migrations in production
kubectl exec -it deployment/forge-crm -n crm-system -- \
  python manage.py migrate

# Or with Docker
docker exec forge-crm python manage.py migrate
```

### Backup and Restore

#### Backup

```bash
# Database backup
pg_dump -h postgres.yourdomain.com -U crm_user -d crm_production \
  -f crm_backup_$(date +%Y%m%d_%H%M%S).sql

# Media files backup (if applicable)
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz /app/media/
```

#### Restore

```bash
# Restore database
psql -h postgres.yourdomain.com -U crm_user -d crm_production \
  -f crm_backup_20251104_120000.sql

# Restore media files
tar -xzf media_backup_20251104_120000.tar.gz -C /app/
```

## Monitoring and Logging

### Health Monitoring

```bash
# Health check endpoint
curl https://crm.yourdomain.com/health/

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "timestamp": "2025-11-04T12:00:00Z"
}
```

### Application Logs

```bash
# Docker logs
docker logs forge-crm --tail=100 --follow

# Kubernetes logs
kubectl logs -f deployment/forge-crm -n crm-system

# Log aggregation with ELK/Fluentd (optional)
```

### Metrics Collection

Configure Prometheus metrics (optional):

```yaml
# Add to values.yaml for Helm
metrics:
  enabled: true
  serviceMonitor:
    enabled: true
    namespace: monitoring
```

## Security Considerations

### SSL/TLS Configuration

```yaml
# Ingress TLS configuration
ingress:
  tls:
    - secretName: forge-crm-tls
      hosts:
        - crm.yourdomain.com
```

### Network Security

```yaml
# Network policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: forge-crm-netpol
spec:
  podSelector:
    matchLabels:
      app: forge-crm
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
```

### Secrets Management

```bash
# Create database secret
kubectl create secret generic crm-db-secret \
  --from-literal=password=your-secure-password \
  -n crm-system

# Create JWT secret (if needed)
kubectl create secret generic crm-jwt-secret \
  --from-file=public-key=jwt-public-key.pem \
  -n crm-system
```

## Performance Tuning

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_account_owner ON crm_account(owner_id);
CREATE INDEX idx_lead_status ON crm_lead(status);
CREATE INDEX idx_opportunity_stage ON crm_opportunity(stage);
CREATE INDEX idx_task_due_date ON crm_task(due_date);
CREATE INDEX idx_campaign_status ON crm_campaign(status);
```

### Application Scaling

```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: forge-crm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: forge-crm
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Troubleshooting

### Common Production Issues

**High Memory Usage:**
```bash
# Check memory usage
kubectl top pods -n crm-system

# Increase memory limits
# Edit values.yaml and upgrade Helm chart
```

**Database Connection Issues:**
```bash
# Test database connectivity
kubectl exec -it deployment/forge-crm -n crm-system -- \
  python manage.py dbshell

# Check database credentials
kubectl get secret crm-db-secret -o yaml -n crm-system
```

**SSL Certificate Issues:**
```bash
# Check certificate status
kubectl describe certificate forge-crm-tls -n crm-system

# Force certificate renewal
kubectl delete certificate forge-crm-tls -n crm-system
```

### Log Analysis

```bash
# Search for errors in logs
kubectl logs deployment/forge-crm -n crm-system | grep ERROR

# Monitor real-time logs
kubectl logs -f deployment/forge-crm -n crm-system --tail=50
```

## Maintenance

### Regular Tasks

```bash
# Update deployment
helm upgrade forge-crm buildly/forge-crm \
  --values production-values.yaml

# Database maintenance
kubectl exec -it deployment/forge-crm -n crm-system -- \
  python manage.py clearsessions

# Collect static files (if needed)
kubectl exec -it deployment/forge-crm -n crm-system -- \
  python manage.py collectstatic --noinput
```

### Version Updates

```bash
# Update to new version
helm upgrade forge-crm buildly/forge-crm \
  --set image.tag=1.1.0 \
  --values production-values.yaml

# Rollback if needed
helm rollback forge-crm 1
```