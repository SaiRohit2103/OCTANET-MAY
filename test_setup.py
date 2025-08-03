#!/usr/bin/env python3
"""
Test Script for Delhi High Court Case Data Fetcher
Verifies that all dependencies are properly installed
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'selenium',
        'flask',
        'requests',
        'bs4',
        'PIL',
        'cv2', 
        'numpy',
        'pytesseract',
        'sqlite3'
    ]
    
    print("🧪 Testing package imports...")
    print("=" * 40)
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package:<15} - OK")
        except ImportError as e:
            print(f"❌ {package:<15} - FAILED: {e}")
            failed_imports.append(package)
    
    return failed_imports

def test_selenium_webdriver():
    """Test Selenium WebDriver setup"""
    print("\n🌐 Testing Selenium WebDriver...")
    print("=" * 40)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Test ChromeDriver installation
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        print("Checking ChromeDriver installation...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver found at: {driver_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ WebDriver test failed: {e}")
        return False

def test_ocr():
    """Test OCR functionality"""
    print("\n🔍 Testing OCR (Tesseract)...")
    print("=" * 40)
    
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # Create a simple test image
        test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255
        # Add some text-like patterns (simple black rectangles)
        test_image[40:60, 50:100] = 0  # Simulate text
        test_image[40:60, 120:170] = 0
        
        # Convert to PIL Image
        pil_image = Image.fromarray(test_image)
        
        # Test OCR
        text = pytesseract.image_to_string(pil_image)
        print("✅ Tesseract OCR is working")
        print(f"📝 OCR test output: '{text.strip()}'")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

def test_database():
    """Test SQLite database functionality"""
    print("\n🗄️  Testing Database...")
    print("=" * 40)
    
    try:
        import sqlite3
        
        # Test database creation
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        
        # Insert test data
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
        
        # Query test data
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            print("✅ SQLite database functionality working")
            return True
        else:
            print("❌ Database test failed: No data returned")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_flask():
    """Test Flask framework"""
    print("\n🌍 Testing Flask...")
    print("=" * 40)
    
    try:
        from flask import Flask
        
        # Create test Flask app
        app = Flask(__name__)
        
        @app.route('/test')
        def test_route():
            return {'status': 'ok'}
        
        # Test app context
        with app.app_context():
            print("✅ Flask application context working")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🏛️  Delhi High Court Case Data Fetcher - Setup Test")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Package Imports", test_imports),
        ("Selenium WebDriver", test_selenium_webdriver),
        ("OCR (Tesseract)", test_ocr),
        ("Database (SQLite)", test_database),
        ("Flask Framework", test_flask)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if test_name == "Package Imports":
                failed_imports = test_func()
                results[test_name] = len(failed_imports) == 0
                if failed_imports:
                    print(f"\n❌ Failed imports: {', '.join(failed_imports)}")
            else:
                results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} - {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python run.py")
        print("2. Open: http://localhost:5000")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Install system dependencies (Chrome, Tesseract)")
        print("3. Check the README.md for detailed setup instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())