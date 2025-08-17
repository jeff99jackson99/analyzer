#!/usr/bin/env python3
"""
Launcher script for Dashboard Claims Analyzer
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import selenium
        import openai
        import requests
        import pandas
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Please run: python setup.py")
        return False

def check_env_file():
    """Check if .env file exists and has required values"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("💡 Please create .env file with your OpenAI API key")
        print("   You can copy from env.example and edit it")
        return False
    
    # Check if OpenAI API key is set
    try:
        with open('.env', 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY=your_openai_api_key_here' in content:
                print("⚠️  Please update your OpenAI API key in .env file")
                return False
            elif 'OPENAI_API_KEY=' in content:
                print("✅ .env file configured")
                return True
            else:
                print("⚠️  OpenAI API key not found in .env file")
                return False
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def main():
    """Main launcher function"""
    print("🚀 Launching Dashboard Claims Analyzer...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment configuration
    if not check_env_file():
        print("\n💡 To fix this:")
        print("1. Copy env.example to .env")
        print("2. Edit .env with your actual OpenAI API key")
        print("3. Run this script again")
        sys.exit(1)
    
    print("✅ All checks passed!")
    print("🌐 Starting Streamlit app...")
    print("📱 The app will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the app")
    print("=" * 50)
    
    try:
        # Run Streamlit app
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start app: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install it first:")
        print("   pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
