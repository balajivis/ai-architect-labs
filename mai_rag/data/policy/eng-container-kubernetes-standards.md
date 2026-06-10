---
title: Container & Kubernetes Standards
doc_id: eng-container-kubernetes-standards
owner: Platform Engineering
last_updated: 2026-06-01
status: active
classification: internal
supersedes: ""
superseded_by: ""
---

# Container & Kubernetes Standards

## 1. Overview

All Northwind services run as containerized workloads on Kubernetes (EKS on AWS, AKS on Azure). This standard defines container image requirements, Kubernetes manifest patterns, networking, and resource limits.

## 2. Container Image Requirements

### 2.1 Dockerfile Standards

All Dockerfiles must follow best practices:

```dockerfile
# ✓ GOOD: Multi-stage build, minimal base image, security scanning
FROM node:20-alpine AS builder
WORKDIR /build
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /build/node_modules ./node_modules
COPY . .

# Run as non-root user
RUN addgroup -g 1001 -S app && adduser -S app -u 1001
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node healthcheck.js

EXPOSE 3000
CMD ["node", "server.js"]
```

**Key requirements**:
1. **Multi-stage builds**: Reduce final image size (builder stage not included in final image)
2. **Minimal base image**: Use `alpine` or `distroless` (not `ubuntu` or `debian`)
3. **Non-root user**: Never run as root; declare USER in Dockerfile
4. **Health checks**: HEALTHCHECK instruction for container orchestration
5. **No secrets**: Never bake secrets/credentials into image (use environment variables)

### 2.2 Image Scanning and Security

All images scanned for vulnerabilities before deployment:

```bash
# Local: Scan before push
trivy image northwind-prod-east.dkr.ecr.us-east-1.amazonaws.com/data-connector:v1.5.2

# Result:
# ERROR: High-severity vulnerability found: openssl v1.0.2 (CVE-2016-2183)
# Action: Rebuild with openssl >= 1.1.0

# CI/CD: GitHub Actions scans on every build
# If HIGH or CRITICAL found: Build fails; must fix before merge
```

### 2.3 Image Registry (ECR)

All images pushed to AWS ECR after successful build:

```bash
# ECR repository naming: northwind-prod-<service-name>
# Example: northwind-prod-east.dkr.ecr.us-east-1.amazonaws.com/data-connector

# Image tagging:
# - :latest → Most recent build (use with caution; prefer semantic versions)
# - :v1.5.2 → Semantic version (stable release)
# - :v1.5.2-hotfix → Hotfix release (see GIT_BRANCHING_RELEASE_STRATEGY)
# - :git-abc123 → Specific commit SHA (for debugging)

# Retention policy: Keep images for 180 days
# Automated cleanup: AWS ECR lifecycle policy deletes untagged images > 30 days old
```

## 3. Kubernetes Manifests

### 3.1 Deployment Template

```yaml
# kubernetes/deployments/data-connector.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-connector
  namespace: northwind-prod
  labels:
    app: data-connector
    version: v1
    team: data-platform
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: data-connector
  template:
    metadata:
      labels:
        app: data-connector
        version: v1
    spec:
      # Pod disruption budget: Allow rolling updates with 1 replica down
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: app
                operator: In
                values: [data-connector]
      
      containers:
      - name: data-connector
        image: northwind-prod-east.dkr.ecr.us-east-1.amazonaws.com/data-connector:v1.5.2
        imagePullPolicy: IfNotPresent
        
        # Resource requests: Kubernetes reserves these resources
        resources:
          requests:
            cpu: 200m          # 0.2 CPU core
            memory: 512Mi      # 512 MB
          limits:
            cpu: 1000m         # 1 CPU core (hard limit)
            memory: 2Gi        # 2 GB (hard limit)
        
        # Ports
        ports:
        - name: http
          containerPort: 3000
        - name: metrics
          containerPort: 9090
        
        # Environment variables from secrets
        env:
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: northwind-db-secrets
              key: postgres-password
        - name: SALESFORCE_API_KEY
          valueFrom:
            secretKeyRef:
              name: external-api-secrets
              key: salesforce-api-key
        - name: LOG_LEVEL
          value: "info"
        
        # Liveness probe: Restart if unhealthy
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Readiness probe: Remove from load balancer if not ready
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        
        # Security context
        securityContext:
          runAsNonRoot: true
          runAsUser: 1001
          readOnlyRootFilesystem: false
          allowPrivilegeEscalation: false
          capabilities:
            drop: [ALL]
        
        # Volume mounts
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      
      # Pod security context
      securityContext:
        fsGroup: 1001
      
      # Service account (RBAC)
      serviceAccountName: data-connector
      
      # Volumes
      volumes:
      - name: tmp
        emptyDir: {}
      
      # Node selector: Run on specific node pools
      nodeSelector:
        workload-type: general
      
      # Tolerations: Allow scheduling on tainted nodes
      tolerations:
      - key: batch
        operator: Equal
        value: "true"
        effect: NoExecute
        tolerationSeconds: 60
```

### 3.2 Service Manifest

```yaml
# kubernetes/services/data-connector.yaml
apiVersion: v1
kind: Service
metadata:
  name: data-connector
  namespace: northwind-prod
spec:
  type: ClusterIP  # Internal only; ingress for external
  selector:
    app: data-connector
  ports:
  - name: http
    port: 80
    targetPort: 3000
  - name: metrics
    port: 9090
    targetPort: 9090
```

### 3.3 ConfigMap and Secrets

```yaml
# kubernetes/configmaps/data-connector-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: data-connector-config
  namespace: northwind-prod
data:
  # Non-sensitive configuration
  ENVIRONMENT: "prod"
  LOG_LEVEL: "info"
  METRICS_ENABLED: "true"
```

```yaml
# kubernetes/secrets/northwind-db-secrets.yaml (use Sealed Secrets in git)
apiVersion: v1
kind: Secret
metadata:
  name: northwind-db-secrets
  namespace: northwind-prod
type: Opaque
data:
  # Base64 encoded; do NOT commit plaintext to git
  # Use 'kubectl create secret' or kubeseal for encryption
  postgres-password: <base64-encoded>
  postgres-username: <base64-encoded>
```

## 4. Networking Policies

### 4.1 Ingress (External Traffic)

```yaml
# kubernetes/ingress/api-gateway.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-gateway-ingress
  namespace: northwind-prod
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.northwind.com
    secretName: api-gateway-tls
  rules:
  - host: api.northwind.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 80
```

### 4.2 Network Policies (Pod-to-Pod)

Restrict traffic between services using NetworkPolicy:

```yaml
# kubernetes/network-policies/data-connector-egress.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: data-connector-egress
  namespace: northwind-prod
spec:
  podSelector:
    matchLabels:
      app: data-connector
  policyTypes:
  - Egress
  egress:
  # Allow DNS
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
  # Allow external API calls
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
    ports:
    - protocol: TCP
      port: 443
  # Allow traffic to other services
  - to:
    - namespaceSelector:
        matchLabels:
          name: northwind-prod
      podSelector:
        matchLabels:
          app: transformation-engine
    ports:
    - protocol: TCP
      port: 3000
```

## 5. Resource Limits and HPA (Horizontal Pod Autoscaling)

### 5.1 Pod Resource Requests/Limits

All pods must declare resource requests (soft limit) and limits (hard limit):

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|-----------------|--------------|
| api-gateway | 200m | 1000m | 512Mi | 2Gi |
| data-connector | 500m | 2000m | 1Gi | 4Gi |
| transformation-engine | 1000m | 4000m | 2Gi | 8Gi |

**Requests**: K8s reserves this amount (guarantees availability)  
**Limits**: Pod killed if it exceeds this amount (prevents runaway)

### 5.2 Horizontal Pod Autoscaling

```yaml
# kubernetes/hpa/data-connector.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: data-connector-hpa
  namespace: northwind-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: data-connector
  minReplicas: 3
  maxReplicas: 10
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale up at 70% CPU
  # Custom metric (Prometheus)
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1k"  # Scale up if > 1k req/sec per pod
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50  # Scale down by 50% max
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100  # Double replicas
        periodSeconds: 30
```

## 6. StatefulSets vs. Deployments

| Use Case | Resource | Persistence | Ordering |
|----------|----------|-------------|----------|
| **Stateless services** (api-gateway, transformation-engine) | Deployment | No | Parallel |
| **Databases, caches** (PostgreSQL, Redis) | StatefulSet | Yes (PersistentVolume) | Ordered |

All Northwind stateless services use Deployments. Databases managed by cloud providers (RDS, Azure DB) not in K8s.

## 7. Observability in Kubernetes

### 7.1 Logging

All pod logs go to stdout/stderr; Datadog agent collects:

```bash
# View logs
kubectl logs -f deployment/data-connector -n northwind-prod

# Result:
2026-06-01T14:30:45.123Z INFO data-connector: Customer sync started
```

### 7.2 Metrics

Prometheus endpoint exposed on `:9090/metrics` (see **Observability & Monitoring Standards**).

### 7.3 Health Checks

All deployments include liveness and readiness probes (see manifest template above).

## 8. Cluster Maintenance

### 8.1 Node Updates

EKS/AKS clusters automatically patch nodes (security updates, OS patches).

**Managed by**: Cloud provider (AWS/Azure) — no manual intervention required.

### 8.2 Kubernetes Version Upgrades

Quarterly, platform team upgrades Kubernetes version:

```bash
# Check current version
kubectl version --short

# Upgrade command (managed via Terraform)
# See INFRASTRUCTURE_AS_CODE_STANDARDS
```

---

**Related policies:**
- See **Microservices Architecture Overview** for service topology
- See **Service Catalog** for which services run where
- See **Observability & Monitoring Standards** for health checks and metrics
- See **Infrastructure as Code Standards** for Terraform Kubernetes resource definitions
- See **Secrets Management Standard** for secret handling in Kubernetes
