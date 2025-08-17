#!/usr/bin/env python3
"""
Setup script for Dashboard Claims Analyzer
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def create_env_file():
    """Create .env file from example"""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            try:
                with open('env.example', 'r') as example_file:
                    content = example_file.read()
                
                with open('.env', 'w') as env_file:
                    env_file.write(content)
                
                print("✅ Created .env file from env.example")
                print("⚠️  Please edit .env file with your actual API keys and configuration")
                return True
            except Exception as e:
                print(f"❌ Failed to create .env file: {e}")
                return False
        else:
            print("⚠️  env.example file not found, skipping .env creation")
            return True
    else:
        print("✅ .env file already exists")
        return True

def check_chromedriver():
    """Check if ChromeDriver is available"""
    try:
        result = subprocess.run("chromedriver --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ChromeDriver is available")
            return True
        else:
            print("❌ ChromeDriver not found or not working")
            return False
    except Exception:
        print("❌ ChromeDriver not found")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Dashboard Claims Analyzer...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("❌ Setup failed during environment file creation")
        sys.exit(1)
    
    # Check ChromeDriver
    if not check_chromedriver():
        print("⚠️  ChromeDriver not found. Please install it manually:")
        print("   macOS: brew install chromedriver")
        print("   Or download from: https://chromedriver.chromium.org/")
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your OpenAI API key")
    print("2. Install ChromeDriver if not already installed")
    print("3. Run: streamlit run app.py")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
