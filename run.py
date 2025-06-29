#!/usr/bin/env python3
"""
Face Anti-Spoofing Attendance System Startup Script
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'flask_sqlalchemy', 
        'face_recognition',
        'cv2',
        'numpy',
        'PIL',
        'torch',
        'torchvision'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if package == 'cv2':
            spec = importlib.util.find_spec('cv2')
        elif package == 'PIL':
            spec = importlib.util.find_spec('PIL')
        else:
            spec = importlib.util.find_spec(package)
            
        if spec is None:
            missing_packages.append(package)
        else:
            print(f"✅ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    return True

def check_model_files():
    """Check if required model files exist"""
    model_files = [
        'best_liveness_model.pth',
        'models/slip_model.py'
    ]
    
    missing_files = []
    
    for file_path in model_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n⚠️  Missing model files: {', '.join(missing_files)}")
        print("The system will work without liveness detection if models are missing.")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'instance']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def main():
    """Main startup function"""
    print("🚀 Face Anti-Spoofing Attendance System")
    print("=" * 50)
    
    # Check Python version
    print("\n📋 Checking Python version...")
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("\n💡 To install dependencies, run:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Check model files
    print("\n🤖 Checking model files...")
    check_model_files()
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Start the application
    print("\n🌐 Starting the application...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 