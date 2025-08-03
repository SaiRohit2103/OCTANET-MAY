#!/usr/bin/env python3
"""
Delhi High Court Case Data Fetcher - Demo Script
Demonstrates the scraper functionality with sample cases
"""

import json
import time
from court_scraper import DelhiHighCourtScraper

def demo_search():
    """Demo function to test case searching"""
    print("🎯 Delhi High Court Case Data Fetcher Demo")
    print("=" * 50)
    
    # Sample test cases (these may not exist, just for demo)
    test_cases = [
        {"case_type": "WP(C)", "case_number": "12345", "filing_year": "2023"},
        {"case_type": "CM", "case_number": "6789", "filing_year": "2022"},
        {"case_type": "CRL.A", "case_number": "1111", "filing_year": "2024"}
    ]
    
    scraper = DelhiHighCourtScraper()
    
    try:
        for i, case in enumerate(test_cases, 1):
            print(f"\n🔍 Test Case {i}: {case['case_type']} {case['case_number']}/{case['filing_year']}")
            print("-" * 30)
            
            # Perform search
            result = scraper.search_case(
                case_type=case['case_type'],
                case_number=case['case_number'],
                filing_year=case['filing_year']
            )
            
            # Display results
            if result.get('success'):
                print("✅ Search successful!")
                data = result.get('data', {})
                
                if data.get('case_number'):
                    print(f"📋 Case Number: {data['case_number']}")
                if data.get('filing_date'):
                    print(f"📅 Filing Date: {data['filing_date']}")
                if data.get('status'):
                    print(f"📊 Status: {data['status']}")
                if data.get('parties'):
                    print(f"👥 Parties: {len(data['parties'])} found")
                if data.get('hearings'):
                    print(f"📝 Hearings: {len(data['hearings'])} records")
                if data.get('orders'):
                    print(f"⚖️  Orders: {len(data['orders'])} found")
                    
                # Save detailed results
                filename = f"demo_result_{i}.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"💾 Detailed results saved to: {filename}")
                
            else:
                print("❌ Search failed!")
                print(f"Error: {result.get('message', 'Unknown error')}")
                if result.get('error'):
                    print(f"Details: {result['error']}")
            
            # Wait between searches to be respectful
            if i < len(test_cases):
                print("⏳ Waiting before next search...")
                time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
    finally:
        scraper.close()
        print("\n✅ Demo completed")

def demo_captcha_solving():
    """Demo CAPTCHA solving capabilities"""
    print("\n🔐 CAPTCHA Solving Demo")
    print("=" * 30)
    
    print("This demo would:")
    print("1. Navigate to Delhi High Court website")
    print("2. Locate CAPTCHA images")
    print("3. Apply image processing techniques:")
    print("   - Grayscale conversion")
    print("   - Threshold operations")
    print("   - Gaussian blur")
    print("   - Morphological operations")
    print("4. Extract text using Tesseract OCR")
    print("5. Submit CAPTCHA solution")
    print("6. Retry if unsuccessful (up to 3 attempts)")
    
    print("\n🖼️  CAPTCHA images are saved locally for review")
    print("📊 OCR accuracy depends on image quality")

def main():
    """Main demo function"""
    print("Welcome to Delhi High Court Case Data Fetcher Demo!")
    print("\nAvailable demos:")
    print("1. Case Search Demo")
    print("2. CAPTCHA Solving Info")
    print("3. Both")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (0-3): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                demo_search()
                break
            elif choice == "2":
                demo_captcha_solving()
                break
            elif choice == "3":
                demo_captcha_solving()
                demo_search()
                break
            else:
                print("❌ Invalid choice. Please enter 0-3.")
                
        except KeyboardInterrupt:
            print("\n👋 Demo stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()