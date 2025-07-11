#!/bin/bash

# AI-Powered Interview Management Platform Setup Script
# This script sets up the complete platform with all dependencies

set -e

echo "🚀 Setting up AI-Powered Interview Management Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Installing Node.js 18..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    
    print_success "Node.js is installed"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
    
    print_success "Python is installed"
}

# Create environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please edit .env file with your configuration before continuing"
    else
        print_warning ".env file already exists"
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up Django backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create necessary directories
    mkdir -p media static logs
    
    # Run migrations
    print_status "Running database migrations..."
    python manage.py makemigrations
    python manage.py migrate
    
    # Create superuser
    print_status "Creating superuser..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin@company.com', 'admin123') if not User.objects.filter(email='admin@company.com').exists() else None" | python manage.py shell
    
    # Load seed data
    print_status "Loading seed data..."
    python manage.py loaddata seed_data.json
    
    # Collect static files
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up React frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Build the application
    print_status "Building frontend application..."
    npm run build
    
    cd ..
    print_success "Frontend setup completed"
}

# Setup Docker
setup_docker() {
    print_status "Setting up Docker containers..."
    
    # Build and start containers
    docker-compose build
    
    print_success "Docker containers built successfully"
    print_status "To start the application, run: docker-compose up -d"
}

# Create nginx configuration
setup_nginx() {
    print_status "Setting up Nginx configuration..."
    
    mkdir -p nginx
    
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Admin panel
        location /admin/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Static files
        location /static/ {
            proxy_pass http://backend;
        }
        
        # Media files
        location /media/ {
            proxy_pass http://backend;
        }
    }
}
EOF
    
    print_success "Nginx configuration created"
}

# Create management scripts
create_scripts() {
    print_status "Creating management scripts..."
    
    # Start script
    cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Interview Management Platform..."
docker-compose up -d
echo "✅ Platform is starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "⚙️  Admin Panel: http://localhost:8000/admin"
echo "📚 API Docs: http://localhost:8000/api/docs/"
EOF
    chmod +x start.sh
    
    # Stop script
    cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Interview Management Platform..."
docker-compose down
echo "✅ Platform stopped"
EOF
    chmod +x stop.sh
    
    # Restart script
    cat > restart.sh << 'EOF'
#!/bin/bash
echo "🔄 Restarting Interview Management Platform..."
docker-compose down
docker-compose up -d
echo "✅ Platform restarted"
EOF
    chmod +x restart.sh
    
    # Logs script
    cat > logs.sh << 'EOF'
#!/bin/bash
echo "📋 Showing platform logs..."
docker-compose logs -f
EOF
    chmod +x logs.sh
    
    print_success "Management scripts created"
}

# Create development setup
setup_development() {
    print_status "Setting up development environment..."
    
    # Backend development script
    cat > dev-backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
EOF
    chmod +x dev-backend.sh
    
    # Frontend development script
    cat > dev-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm start
EOF
    chmod +x dev-frontend.sh
    
    print_success "Development scripts created"
}

# Main setup function
main() {
    echo "🎯 AI-Powered Interview Management Platform Setup"
    echo "================================================"
    
    # Check prerequisites
    check_docker
    check_node
    check_python
    
    # Setup environment
    setup_environment
    
    # Setup components
    setup_backend
    setup_frontend
    setup_nginx
    setup_docker
    
    # Create scripts
    create_scripts
    setup_development
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Run './start.sh' to start the platform"
    echo "3. Access the application at http://localhost:3000"
    echo ""
    echo "🔑 Default admin credentials:"
    echo "   Email: admin@company.com"
    echo "   Password: admin123"
    echo ""
    echo "📚 Documentation:"
    echo "   - API Docs: http://localhost:8000/api/docs/"
    echo "   - Admin Panel: http://localhost:8000/admin"
    echo ""
    echo "🛠️  Management commands:"
    echo "   - Start: ./start.sh"
    echo "   - Stop: ./stop.sh"
    echo "   - Restart: ./restart.sh"
    echo "   - Logs: ./logs.sh"
    echo ""
    echo "💻 Development:"
    echo "   - Backend: ./dev-backend.sh"
    echo "   - Frontend: ./dev-frontend.sh"
}

# Run main function
main "$@"