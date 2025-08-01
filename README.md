# Scalable Microservices Note-taking App

## Overview
A modern, scalable note-taking application built with microservices architecture:

- **Frontend:** React (Vite + TypeScript) with rich text editor
- **Backend:** Python (FastAPI) microservices with async database operations
- **Database:** PostgreSQL with connection pooling
- **API Gateway:** FastAPI-based routing and load balancing
- **Orchestration:** Docker Compose for local development
- **Monitoring:** Prometheus, Grafana, Jaeger, Loki (optional)
- **Security:** JWT Authentication, Rate Limiting, CORS Protection

## Features
- 📝 Rich text editing with markdown support
- 🔄 Real-time note synchronization
- 📱 Responsive design for all devices
- 🚀 Fast API responses with async operations
- 🔒 Secure database connections
- 🔐 **JWT Authentication & Authorization**
- 🛡️ **Rate Limiting & Security Headers**
- 📊 **Comprehensive Monitoring Stack**
- 🐳 **Microservices Architecture**
- ☸️ **Kubernetes-ready with Helm charts**
- 🔧 **Multi-environment deployment** (Dev/Prod)
- 📈 **Auto-scaling with HPA**
- 🌐 **Ingress-based routing**
- 🔄 **CI/CD ready**

## Architecture

### Microservices
- **Frontend Service**: React app with NGINX
- **API Gateway**: Routes requests to microservices
- **Notes Service**: Handles note CRUD operations
- **Folders Service**: Manages folder organization
- **Database Service**: PostgreSQL with persistent storage

### Monitoring Stack (Optional)
- **Grafana**: Dashboard and visualization
- **Prometheus**: Metrics collection and alerting
- **Jaeger**: Distributed tracing
- **Loki**: Log aggregation
- **Node Exporter**: System metrics

## Security Features
- **JWT Token Authentication** with access and refresh tokens
- **Password Security** with bcrypt hashing and strength validation
- **Rate Limiting** to prevent abuse (100 requests/minute)
- **Security Headers** (CSP, XSS Protection, etc.)
- **CORS Protection** with configurable origins
- **Input Validation** for all user inputs
- **User Data Isolation** - users can only access their own data
- **SQL Injection Protection** with parameterized queries

## Project Structure
```
├── frontend/          # React + Vite app with TypeScript
├── microservices/     # Microservices architecture
│   ├── api-gateway/   # API Gateway service
│   ├── notes-service/ # Notes management service
│   ├── folders-service/ # Folder organization service
│   ├── shared/        # Shared utilities and models
│   └── init.sql       # Database initialization
├── monitoring/        # Prometheus & Grafana setup
├── k8s/              # Kubernetes manifests (Kustomize)
│   ├── base/         # Base Kubernetes resources
│   └── overlays/     # Environment-specific configs
├── helm/             # Helm charts for Kubernetes deployment
│   └── notes-app/    # Main Helm chart
├── scripts/          # Deployment and utility scripts
├── docker-compose.yml # Local development setup
└── SECURITY.md       # Comprehensive security documentation
```

## Prerequisites

### For Local Development
- **Docker & Docker Compose** (required)
- **Node.js** 18+ (for frontend development)
- **Python** 3.9+ (for backend development)

### For Production Deployment
- **Kubernetes** cluster (1.20+)
- **Helm** 3.0+
- **NGINX Ingress Controller**
- **kubectl** configured

## Quick Start

### Option 1: Microservices with Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Scalable-Notetaking-App
   ```

2. **Start the microservices**
   ```bash
   cd microservices
   sh start-microservices.sh
   ```

3. **Access the application**
   - Frontend: http://localhost
   - API Gateway: http://localhost:8000
   - Notes Service: http://localhost:8001
   - Folders Service: http://localhost:8002
   - API Documentation: http://localhost:8000/docs

### Option 2: With Monitoring Stack

1. **Start microservices first**
   ```bash
   cd microservices
   sh start-microservices.sh
   ```

2. **Start monitoring stack**
   ```bash
   cd monitoring
   sh start-monitoring.sh
   ```

3. **Access monitoring dashboards**
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090
   - Jaeger: http://localhost:16686

### Option 3: Local Development

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Frontend will be available at http://localhost:5173
```

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
# Backend will be available at http://localhost:8000
```

### Option 4: Kubernetes Deployment

#### Prerequisites
- **Kubernetes cluster** (Minikube, GKE, EKS, AKS, etc.)
- **kubectl** configured to connect to your cluster
- **Docker** for building images
- **kustomize** (usually included with kubectl)
- **Helm** 3.0+ (for Helm deployment)

#### Option 4A: Kustomize Deployment (Recommended for simplicity)

1. **Build and push images**
   ```bash
   # Build images with your registry
   ./scripts/build-images.sh v1.0.0 your-registry.com/your-project
   
   # For local testing (no registry push)
   ./scripts/build-images.sh v1.0.0 localhost:5000/notes
   ```

2. **Update image references** (if using custom registry)
   ```bash
   # Update k8s/base/backend-deployment.yaml
   # Change: image: notes-backend:latest
   # To: image: your-registry.com/your-project/notes-backend:v1.0.0
   
   # Update k8s/base/frontend-deployment.yaml  
   # Change: image: notes-frontend:latest
   # To: image: your-registry.com/your-project/notes-frontend:v1.0.0
   ```

3. **Deploy to development**
   ```bash
   # Deploy to development environment
   kubectl apply -k k8s/overlays/development
   
   # Or use the deployment script
   ./scripts/deploy-k8s.sh development
   ```

4. **Deploy to production**
   ```bash
   # Deploy to production environment
   kubectl apply -k k8s/overlays/production
   
   # Or use the deployment script
   ./scripts/deploy-k8s.sh production
   ```

5. **Access the application**
   ```bash
   # Port forward to access locally
   kubectl port-forward service/dev-frontend-service 8080:80 -n notes-app-dev
   
   # Access via ingress (if configured)
   echo "127.0.0.1 notes.local" >> /etc/hosts
   curl http://notes.local
   ```

#### Option 4B: Helm Deployment (Recommended for production)

1. **Build and push images**
   ```bash
   # Build images with your registry
   ./scripts/build-images.sh v1.0.0 your-registry.com/your-project
   ```

2. **Install with Helm**
   ```bash
   # Install with default values
   helm install notes-app ./helm/notes-app --namespace notes-app
   
   # Or use the install script
   ./helm/install.sh my-release my-namespace
   ```

3. **Upgrade with new version**
   ```bash
   # Upgrade to new version
   helm upgrade notes-app ./helm/notes-app --set app.version=v1.1.0
   ```

4. **Access the application**
   ```bash
   # Port forward to access locally
   kubectl port-forward -n notes-app svc/notes-app-notes-app-frontend 8080:80
   
   # Access via configured domain
   curl https://notes.yourdomain.com
   ```

#### Kubernetes Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ingress       │    │   Frontend      │    │   Backend       │
│   (NGINX)       │───▶│   (React)       │───▶│   (FastAPI)     │
│   Port: 80/443  │    │   Port: 80      │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Database      │
                                               │   (PostgreSQL)  │
                                               │   Port: 5432    │
                                               └─────────────────┘
```

#### Kubernetes Resources
- **Namespace**: Isolates the application
- **Deployments**: Application workloads (Frontend, Backend, Database)
- **Services**: Internal networking
- **ConfigMaps**: Non-sensitive configuration
- **Secrets**: Database credentials
- **PersistentVolumeClaim**: Database storage
- **Ingress**: External access
- **HorizontalPodAutoscaler**: Auto-scaling

#### Monitoring and Scaling
```bash
# Check deployment status
kubectl get pods -n notes-app

# View logs
kubectl logs -f deployment/backend-deployment -n notes-app

# Manual scaling
kubectl scale deployment/backend-deployment --replicas=5 -n notes-app

# Check HPA status
kubectl get hpa -n notes-app
```

For detailed Kubernetes deployment instructions, see:
- **Kustomize Guide**: [k8s/README.md](k8s/README.md)
- **Helm Guide**: [helm/notes-app/README.md](helm/notes-app/README.md)

### Local Testing Without Registry

For local development and testing, you can use the built images directly:

```bash
# 1. Build images locally (no push)
./scripts/build-images.sh v1.0.0 localhost:5000/notes

# 2. Update Kubernetes manifests to use local images
# Edit k8s/base/backend-deployment.yaml:
#   image: localhost:5000/notes/notes-backend:v1.0.0
#   imagePullPolicy: Never

# Edit k8s/base/frontend-deployment.yaml:
#   image: localhost:5000/notes/notes-frontend:v1.0.0  
#   imagePullPolicy: Never

# 3. Deploy to local cluster
kubectl apply -k k8s/overlays/development

# 4. Access the application
kubectl port-forward service/dev-frontend-service 8080:80 -n notes-app-dev
# Then visit: http://localhost:8080
```

## API Endpoints

### Application Services
- **Frontend**: http://localhost
- **API Gateway**: http://localhost:8000
- **Notes Service**: http://localhost:8001
- **Folders Service**: http://localhost:8002

### API Documentation
- **Gateway Docs**: http://localhost:8000/docs
- **Notes Docs**: http://localhost:8001/docs
- **Folders Docs**: http://localhost:8002/docs

### Health Checks
- **Gateway Health**: http://localhost:8000/health
- **Notes Health**: http://localhost:8001/health
- **Folders Health**: http://localhost:8002/health

## Monitoring Endpoints

### Monitoring Stack (Optional)
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686
- **Loki**: http://localhost:3100
- **Node Exporter**: http://localhost:9100

## Configuration

### Environment Variables

The application uses environment variables for configuration. Key variables:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://notesuser:notespassword@database:5432/notesdb
POSTGRES_USER=notesuser
POSTGRES_PASSWORD=notespassword
POSTGRES_DB=notesdb

# Service Configuration
NOTES_SERVICE_URL=http://notes-service:8001
FOLDERS_SERVICE_URL=http://folders-service:8002

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Docker Services

The microservices stack includes:
- **Database**: PostgreSQL 15 with persistent storage
- **API Gateway**: FastAPI routing and load balancing
- **Notes Service**: Note CRUD operations
- **Folders Service**: Folder management
- **Frontend**: React app served by NGINX

## Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

### Microservices Development
```bash
cd microservices
docker-compose up -d  # Start all services
docker-compose logs   # View logs
docker-compose down   # Stop services
```

### Monitoring Development
```bash
cd monitoring
docker-compose up -d  # Start monitoring stack
docker-compose logs   # View monitoring logs
```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   - Ensure ports 80, 8000, 8001, 8002 are available
   - Check for existing containers: `docker ps`

2. **Container name conflicts**
   - Remove existing containers: `docker rm -f <container-name>`
   - Restart services: `docker-compose up -d`

3. **Database connection errors**
   - Check database container is running: `docker ps | grep database`
   - Verify database health: `curl http://localhost:8000/health`

4. **Frontend not loading**
   - Check API Gateway is running: `curl http://localhost:8000/health`
   - Verify NGINX configuration in frontend container

5. **Monitoring not working**
   - Check monitoring containers: `docker ps | grep monitoring`
   - Verify ports 3000, 9090, 16686 are available

### Health Checks

All services include health checks:
- **API Gateway**: `GET /health`
- **Notes Service**: `GET /health`
- **Folders Service**: `GET /health`
- **Database**: PostgreSQL connection test

### Logs and Debugging

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs api-gateway
docker-compose logs notes-service
docker-compose logs frontend

# Monitor logs in real-time
docker-compose logs -f
```

## Security Testing

### Run Authentication Tests
```bash
cd backend
python test_auth.py
```

This will test:
- User registration with validation
- Login with valid/invalid credentials
- Protected endpoint access
- Token refresh functionality
- Unauthorized access prevention

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security

For security issues, please refer to [SECURITY.md](SECURITY.md) for comprehensive security documentation and contact information.

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the API documentation
- Check the security documentation
- Open an issue on GitHub