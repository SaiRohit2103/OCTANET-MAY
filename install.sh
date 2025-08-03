#!/bin/bash

# Delhi High Court Case Data Fetcher - Installation Script
# This script sets up the environment and installs dependencies

set -e  # Exit on any error

echo "🏛️  Delhi High Court Case Data Fetcher Installation"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Python 3 is installed
check_python() {
    print_info "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python 3 found: $PYTHON_VERSION"
        
        # Check if version is 3.8 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_status "Python version is compatible"
        else
            print_error "Python 3.8+ required. Please upgrade Python."
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8+."
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            print_info "Detected Debian/Ubuntu system"
            sudo apt-get update
            sudo apt-get install -y tesseract-ocr chromium-browser python3-pip
            print_status "System dependencies installed"
        elif command -v yum &> /dev/null; then
            # RHEL/CentOS
            print_info "Detected RHEL/CentOS system"
            sudo yum install -y tesseract chromium python3-pip
            print_status "System dependencies installed"
        else
            print_warning "Unknown Linux distribution. Please install tesseract-ocr and chromium manually."
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_info "Detected macOS system"
        if command -v brew &> /dev/null; then
            brew install tesseract
            brew install --cask google-chrome
            print_status "System dependencies installed via Homebrew"
        else
            print_warning "Homebrew not found. Please install tesseract and Chrome manually."
        fi
    else
        print_warning "Unknown operating system. Please install tesseract-ocr and Chrome manually."
    fi
}

# Create virtual environment
setup_virtual_env() {
    print_info "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_status "Pip upgraded"
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_status "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Create directories and set permissions
setup_directories() {
    print_info "Setting up directories and permissions..."
    
    # Create templates directory if it doesn't exist
    mkdir -p templates
    
    # Make scripts executable
    chmod +x run.py demo.py
    
    # Create .env file from example if it doesn't exist
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Environment file created from example"
        print_warning "Please review and update .env file with your settings"
    fi
    
    print_status "Directories and permissions set up"
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    # Test Python imports
    python3 -c "
import selenium
import flask
import requests
import PIL
import cv2
import numpy
import pytesseract
print('✓ All Python packages imported successfully')
"
    
    if [ $? -eq 0 ]; then
        print_status "Installation test passed"
    else
        print_error "Installation test failed"
        exit 1
    fi
}

# Main installation process
main() {
    echo
    print_info "Starting installation process..."
    echo
    
    check_python
    echo
    
    read -p "Install system dependencies? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_system_deps
        echo
    fi
    
    setup_virtual_env
    echo
    
    install_python_deps
    echo
    
    setup_directories
    echo
    
    test_installation
    echo
    
    print_status "Installation completed successfully!"
    echo
    print_info "Next steps:"
    echo "  1. Review and update .env file if needed"
    echo "  2. Activate virtual environment: source venv/bin/activate"
    echo "  3. Start the application: python run.py"
    echo "  4. Open browser to: http://localhost:5000"
    echo
    print_info "For demo: python demo.py"
    echo
}

# Run main function
main "$@"