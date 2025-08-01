# Scalable Microservices Note-taking App

## Overview
A modern, scalable note-taking application built with microservices architecture:

- **Frontend:** React (Vite + TypeScript) with rich text editor
- **Backend:** Python (FastAPI) with async database operations
- **Database:** PostgreSQL with connection pooling
- **Orchestration:** Docker, Kubernetes, Helm
- **Ingress:** NGINX Ingress Controller
- **Secrets:** Kubernetes Secrets
- **Monitoring:** Prometheus & Grafana (optional)

## Features
- 📝 Rich text editing with markdown support
- 🔄 Real-time note synchronization
- 📱 Responsive design for all devices
- 🚀 Fast API responses with async operations
- 🔒 Secure database connections
- 📊 Optional monitoring and metrics
- 🐳 Containerized deployment
- ☸️ Kubernetes-ready with Helm charts

## Project Structure
```
├── frontend/          # React + Vite app with TypeScript
├── backend/           # FastAPI app with async SQLAlchemy
├── helm/              # Helm charts for Kubernetes deployment
│   └── notes-app/
├── k8s/               # Kubernetes manifests
├── monitoring/        # Prometheus & Grafana setup
├── scripts/           # Deployment and utility scripts
├── db/               # Database initialization scripts
├── docker-compose.yml # Local development setup
└── docker.env.example # Environment variables template
```

## Prerequisites

### For Local Development
- **Docker & Docker Compose** (recommended)
- **Node.js** 18+ (for frontend development)
- **Python** 3.9+ (for backend development)
- **PostgreSQL** 15+ (if running locally)

### For Production Deployment
- **Kubernetes** cluster (1.20+)
- **Helm** 3.0+
- **NGINX Ingress Controller**
- **kubectl** configured

## Quick Start

### Option 1: Docker Compose (Recommended for Development)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Scalable-Notetaking-App
   ```

2. **Set up environment variables**
   ```bash
   cp docker.env.example docker.env
   # Edit docker.env with your preferred settings
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

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

#### Database Setup
```bash
# Install PostgreSQL locally or use Docker
docker run -d \
  --name postgres \
  -e POSTGRES_USER=notesuser \
  -e POSTGRES_PASSWORD=notespassword \
  -e POSTGRES_DB=notesdb \
  -p 5432:5432 \
  postgres:15-alpine
```

### Option 3: Kubernetes Deployment

1. **Add the Helm repository**
   ```bash
   helm repo add notes-app https://your-helm-repo-url
   helm repo update
   ```

2. **Install the application**
   ```bash
   helm install notes-app ./helm/notes-app
   ```

3. **Access the application**
   - Frontend: http://your-cluster-ip
   - Backend API: http://your-cluster-ip/api

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://notesuser:notespassword@localhost:5432/notesdb
POSTGRES_USER=notesuser
POSTGRES_PASSWORD=notespassword
POSTGRES_DB=notesdb

# Backend Configuration
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

### Docker Configuration

The application uses Docker Compose with the following services:
- **Database**: PostgreSQL 15 with persistent storage
- **Backend**: FastAPI with health checks
- **Frontend**: React app served by NGINX

## API Documentation

Once the backend is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json

## Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

### Backend Development
```bash
cd backend
python main.py       # Run development server
python migrate_db.py # Run database migrations
```

### Database Migrations
```bash
cd backend
python migrate_db.py
```

## Monitoring (Optional)

The application includes optional monitoring with Prometheus and Grafana:

```bash
cd monitoring
docker-compose up -d
```

Access monitoring dashboards:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Ensure PostgreSQL is running
   - Check database credentials in environment variables
   - Verify database port (5432) is accessible

2. **Frontend not loading**
   - Check if backend API is running
   - Verify API URL in frontend configuration
   - Check browser console for errors

3. **Docker issues**
   - Ensure Docker and Docker Compose are installed
   - Check if ports 80 and 8000 are available
   - Run `docker-compose logs` for detailed error messages

### Health Checks

The application includes health checks for all services:
- **Backend**: `GET /health`
- **Database**: PostgreSQL connection test
- **Frontend**: NGINX status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the API documentation
- Open an issue on GitHub