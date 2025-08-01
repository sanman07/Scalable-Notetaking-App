#!/usr/bin/env python3
"""
Development setup script for microservices
This script installs dependencies and configures the Python environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    # Install dependencies
    return run_command(
        f"{sys.executable} -m pip install -r {requirements_file}",
        "Installing Python dependencies"
    )

def create_pyproject_toml():
    """Create pyproject.toml for better Python path handling"""
    pyproject_content = """[tool.poetry]
name = "notes-microservices"
version = "1.0.0"
description = "Microservices for Notes Application"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlalchemy = "^2.0.23"
asyncpg = "^0.29.0"
psycopg2-binary = "^2.9.9"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
httpx = "^0.25.2"
prometheus-client = "^0.19.0"
opentelemetry-api = "^1.21.0"
opentelemetry-sdk = "^1.21.0"
opentelemetry-instrumentation-fastapi = "^0.42b0"
opentelemetry-instrumentation-sqlalchemy = "^0.42b0"
opentelemetry-instrumentation-httpx = "^0.42b0"
opentelemetry-exporter-jaeger = "^1.21.0"
opentelemetry-exporter-prometheus = "^1.21.0"
python-dotenv = "^1.0.0"
pydantic = "^2.5.0"
alembic = "^1.13.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
pythonpath = [
    ".",
    "shared"
]
"""
    
    pyproject_file = Path(__file__).parent / "pyproject.toml"
    with open(pyproject_file, 'w') as f:
        f.write(pyproject_content)
    
    print("✅ Created pyproject.toml")
    return True

def create_vscode_settings():
    """Create VS Code settings for better Python path handling"""
    vscode_dir = Path(__file__).parent / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    settings_content = """{
    "python.analysis.extraPaths": [
        "./shared",
        "./api-gateway/app",
        "./notes-service/app", 
        "./folders-service/app"
    ],
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
"""
    
    settings_file = vscode_dir / "settings.json"
    with open(settings_file, 'w') as f:
        f.write(settings_content)
    
    print("✅ Created VS Code settings")
    return True

def create_env_file():
    """Create .env file with default configuration"""
    env_content = """# Database Configuration
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
"""
    
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("ℹ️  .env file already exists")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up microservices development environment...")
    print()
    
    # Change to microservices directory
    os.chdir(Path(__file__).parent)
    
    # Create virtual environment if it doesn't exist
    venv_path = Path("venv")
    if not venv_path.exists():
        print("🔄 Creating virtual environment...")
        if run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
            print("✅ Virtual environment created")
        else:
            print("❌ Failed to create virtual environment")
            return False
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"
    
    if not python_path.exists():
        print(f"❌ Python not found at {python_path}")
        return False
    
    # Upgrade pip
    run_command(f"{python_path} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create configuration files
    create_pyproject_toml()
    create_vscode_settings()
    create_env_file()
    
    print()
    print("🎉 Setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Start the services:")
    print("   python start-microservices.sh")
    print("3. Or start individual services:")
    print("   cd api-gateway/app && python main.py")
    print("   cd notes-service/app && python main.py")
    print("   cd folders-service/app && python main.py")
    print()
    print("The linting errors should now be resolved!")

if __name__ == "__main__":
    main() 