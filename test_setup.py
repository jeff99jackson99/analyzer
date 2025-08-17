#!/usr/bin/env python3
"""
Test script to verify Dashboard Claims Analyzer setup
"""

import importlib
import sys
import os

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        if package_name:
            importlib.import_module(module_name, package_name)
        else:
            importlib.import_module(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ {module_name} import failed: {e}")
        return False

def test_selenium():
    """Test Selenium setup"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Test Chrome options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        
        print("✅ Selenium setup is working")
        return True
    except Exception as e:
        print(f"❌ Selenium setup failed: {e}")
        return False

def test_openai():
    """Test OpenAI setup"""
    try:
        import openai
        print("✅ OpenAI package imported successfully")
        return True
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False

def test_streamlit():
    """Test Streamlit setup"""
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

def test_web_scraping():
    """Test web scraping components"""
    try:
        import requests
        from bs4 import BeautifulSoup
        import pandas as pd
        
        print("✅ Web scraping packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Web scraping packages import failed: {e}")
        return False

def test_config():
    """Test configuration setup"""
    try:
        # Check if .env file exists
        if os.path.exists('.env'):
            print("✅ .env file exists")
        else:
            print("⚠️  .env file not found - you may need to create it")
        
        # Test config import
        import config
        print("✅ Configuration module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Dashboard Claims Analyzer Setup...")
    print("=" * 50)
    
    tests = [
        ("Streamlit", test_streamlit),
        ("OpenAI", test_openai),
        ("Selenium", test_selenium),
        ("Web Scraping", test_web_scraping),
        ("Configuration", test_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 You can now run: streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n💡 Try running: python setup.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
