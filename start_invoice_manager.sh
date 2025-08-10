#!/bin/bash

# Professional Invoice Manager v2.1.0 Launcher Script
# For Linux and macOS systems

echo "================================================"
echo "  Professional Invoice Manager v2.1.0"
echo "  Starting application..."
echo "================================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}💡${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    if python -c 'import sys; exit(0 if sys.version_info[0] >= 3 else 1)' &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python 3 is required but only Python 2 was found"
        print_info "Please install Python 3.7+ from https://python.org"
        exit 1
    fi
else
    print_error "Python is not installed or not in PATH"
    print_info "Please install Python 3.7+ from https://python.org"
    exit 1
fi

# Show Python version
echo "🐍 Python version:"
$PYTHON_CMD --version

# Check if required packages are installed
echo
echo "🔍 Checking dependencies..."

if $PYTHON_CMD -c "import PyQt5" &> /dev/null; then
    print_status "PyQt5 found"
else
    print_error "PyQt5 not found"
    echo "🔧 Installing PyQt5..."
    
    if $PYTHON_CMD -m pip install PyQt5; then
        print_status "PyQt5 installed successfully"
    else
        print_error "Failed to install PyQt5"
        print_info "Try installing manually:"
        echo "  $PYTHON_CMD -m pip install PyQt5"
        echo "  Or on Ubuntu/Debian: sudo apt-get install python3-pyqt5"
        echo "  Or on macOS with Homebrew: brew install pyqt5"
        exit 1
    fi
fi

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Launch the application
echo
echo "🚀 Launching Professional Invoice Manager..."
echo

if $PYTHON_CMD launch_app.py; then
    echo
    print_status "Application closed normally"
else
    echo
    print_error "Application exited with error"
    print_info "Check the error messages above"
    exit 1
fi

echo
echo "👋 Thank you for using Professional Invoice Manager!"
read -p "Press Enter to continue..."
