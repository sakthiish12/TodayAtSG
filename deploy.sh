#!/bin/bash

# TodayAtSG Deployment Script for Vercel
# This script prepares the application for deployment to Vercel

set -e  # Exit on any error

echo "🚀 Starting TodayAtSG deployment preparation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if we're in the project root
if [ ! -f "vercel.json" ]; then
    print_error "vercel.json not found. Please run this script from the project root."
    exit 1
fi

# Environment check
ENVIRONMENT=${1:-production}
print_status "Deploying for environment: $ENVIRONMENT"

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf frontend/dist
rm -rf frontend/node_modules/.cache
rm -rf api/__pycache__
print_success "Cleaned previous builds"

# Check Node.js version
print_status "Checking Node.js version..."
NODE_VERSION=$(node --version)
print_status "Node.js version: $NODE_VERSION"

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
npm ci --production=false
print_success "Frontend dependencies installed"

# Build frontend
print_status "Building frontend for production..."
npm run build:vercel
if [ ! -d "dist" ]; then
    print_error "Frontend build failed - dist directory not created"
    exit 1
fi
print_success "Frontend build completed"

# Return to project root
cd ..

# Check API structure
print_status "Validating API structure..."
if [ ! -f "api/index.py" ]; then
    print_error "API entry point not found at api/index.py"
    exit 1
fi

if [ ! -f "api/requirements.txt" ]; then
    print_error "API requirements.txt not found"
    exit 1
fi
print_success "API structure validated"

# Validate environment files
print_status "Checking environment configuration..."
if [ ! -f "frontend/.env.example" ]; then
    print_warning "Frontend environment example not found"
fi

if [ ! -f "backend/.env.example" ]; then
    print_warning "Backend environment example not found"
fi

# Create deployment summary
print_status "Creating deployment summary..."
cat > deployment-summary.txt << EOF
TodayAtSG Deployment Summary
===========================
Date: $(date)
Environment: $ENVIRONMENT
Node.js Version: $NODE_VERSION
Frontend Build: $([ -d "frontend/dist" ] && echo "✅ Success" || echo "❌ Failed")
API Structure: $([ -f "api/index.py" ] && echo "✅ Valid" || echo "❌ Invalid")

Frontend Build Output:
$(ls -la frontend/dist/ 2>/dev/null || echo "No build output found")

API Files:
$(ls -la api/ 2>/dev/null || echo "No API files found")

Environment Files:
$(ls -la frontend/.env* backend/.env* 2>/dev/null || echo "No environment files found")
EOF

print_success "Deployment summary created"

# Final validation
print_status "Running final validation..."

# Check frontend build
if [ ! -f "frontend/dist/index.html" ]; then
    print_error "Frontend index.html not found in build output"
    exit 1
fi

# Check if static assets exist
if [ ! -d "frontend/dist/static" ] && [ ! -d "frontend/dist/assets" ]; then
    print_warning "No static assets directory found in build"
fi

# Deployment instructions
print_success "🎉 Deployment preparation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Push your changes to your Git repository"
echo "2. Connect your repository to Vercel"
echo "3. Configure environment variables in Vercel dashboard:"
echo "   - Database connection strings"
echo "   - API keys (Google Maps, Stripe, etc.)"
echo "   - Security tokens"
echo "4. Deploy using: vercel --prod"
echo ""
echo "Environment variables needed:"
echo "Frontend (VITE_ prefix):"
echo "  - VITE_API_BASE_URL"
echo "  - VITE_GOOGLE_MAPS_API_KEY"
echo "  - VITE_STRIPE_PUBLISHABLE_KEY"
echo ""
echo "Backend:"
echo "  - DATABASE_URL"
echo "  - SECRET_KEY"
echo "  - GOOGLE_MAPS_API_KEY"
echo "  - STRIPE_SECRET_KEY"
echo ""
print_success "Ready for Vercel deployment! 🚀"