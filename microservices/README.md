# Microservices Development Setup

This directory contains the microservices for the Notes Application. The linting errors you're seeing are due to missing Python dependencies.

## Quick Fix for Linting Errors

### Option 1: Install Dependencies (Recommended)

Run the dependency installer:

```bash
cd microservices
python install_deps.py
```

### Option 2: Manual Installation

```bash
cd microservices
pip install -r requirements.txt
```

### Option 3: Full Development Setup

For a complete development environment with virtual environment:

```bash
cd microservices
python setup_dev.py
```

## Project Structure

```
microservices/
├── shared/                    # Shared utilities and modules
│   ├── database/             # Database models and connection
│   ├── schemas/              # Pydantic schemas
│   └── utils/                # Monitoring and utilities
├── api-gateway/              # API Gateway service
├── notes-service/            # Notes management service
├── folders-service/          # Folders management service
├── auth-service/             # Authentication service
├── requirements.txt          # Python dependencies
├── install_deps.py           # Dependency installer
└── setup_dev.py              # Full development setup
```

## Services

### API Gateway (Port 8000)
- Routes requests to appropriate microservices
- Provides unified API interface
- Handles service discovery and health checks

### Notes Service (Port 8001)
- Manages note CRUD operations
- Handles note content and metadata
- Supports folder organization

### Folders Service (Port 8002)
- Manages folder hierarchy
- Handles folder CRUD operations
- Supports nested folder structure

### Auth Service (Port 8003)
- Handles user authentication
- Manages JWT tokens
- User registration and login

## Running the Services

### Using Docker Compose (Recommended)

```bash
cd microservices
docker-compose up -d
```

### Running Individually

```bash
# API Gateway
cd microservices/api-gateway/app
python main.py

# Notes Service
cd microservices/notes-service/app
python main.py

# Folders Service
cd microservices/folders-service/app
python main.py
```

### Using the Start Script

```bash
cd microservices
chmod +x start-microservices.sh
./start-microservices.sh
```

## Environment Variables

Create a `.env` file in the microservices directory:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://notesuser:notespassword@localhost:5432/notesdb
SYNC_DATABASE_URL=postgresql://notesuser:notespassword@localhost:5432/notesdb

# Service URLs
NOTES_SERVICE_URL=http://localhost:8001
FOLDERS_SERVICE_URL=http://localhost:8002

# Monitoring
JAEGER_ENDPOINT=http://localhost:14268/api/traces

# Database Settings
DB_ECHO=false
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Dependencies

The main dependencies include:

- **FastAPI**: Web framework for building APIs
- **SQLAlchemy**: Database ORM
- **Prometheus Client**: Metrics collection
- **OpenTelemetry**: Distributed tracing
- **Pydantic**: Data validation
- **httpx**: HTTP client for service communication

## Troubleshooting

### Linting Errors
If you still see linting errors after installing dependencies:

1. **Restart your IDE/editor** to pick up the new Python environment
2. **Check Python interpreter**: Make sure your IDE is using the correct Python interpreter
3. **Verify installation**: Run `python -c "import prometheus_client; print('OK')"` to test

### Import Errors
If you see import errors:

1. **Check Python path**: Make sure the `shared` directory is in your Python path
2. **Install missing packages**: Run `pip install <package-name>`
3. **Use virtual environment**: Create and activate a virtual environment

### Service Communication
If services can't communicate:

1. **Check ports**: Ensure ports 8000-8003 are available
2. **Verify URLs**: Check service URLs in environment variables
3. **Database connection**: Ensure PostgreSQL is running and accessible

## Development

### Adding New Services

1. Create a new service directory
2. Add service configuration to `docker-compose.yml`
3. Update API Gateway routing
4. Add service URL to environment variables

### Adding New Dependencies

1. Add to `requirements.txt`
2. Run `python install_deps.py`
3. Update Docker images if needed

### Testing

```bash
# Run tests for all services
cd microservices
pytest

# Run tests for specific service
cd notes-service
pytest
```

## Monitoring

The services include built-in monitoring:

- **Prometheus metrics**: Available at `/metrics` endpoint
- **Health checks**: Available at `/health` endpoint
- **Jaeger tracing**: Distributed tracing for request flows

## Security

- JWT-based authentication
- Rate limiting
- Input validation
- CORS protection
- Security headers

For more information, see the main [README.md](../README.md) and [SECURITY.md](../SECURITY.md) files. 