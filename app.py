#!/usr/bin/env python3
"""
Delhi High Court Data Fetcher - Backend API
Fetches case metadata and orders/judgments with CAPTCHA bypass
"""

import os
import re
import time
import json
import sqlite3
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

# CAPTCHA solving imports
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: easyocr not available. CAPTCHA solving will be limited.")

try:
    from twocaptcha import TwoCaptcha
    TWOCAPTCHA_AVAILABLE = True
except ImportError:
    TWOCAPTCHA_AVAILABLE = False
    print("Warning: 2captcha not available. Manual CAPTCHA solving only.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DELHI_HC_BASE_URL = "https://delhihighcourt.nic.in"
DELHI_HC_SEARCH_URL = f"{DELHI_HC_BASE_URL}/dhcqry/main.asp"
DATABASE_PATH = "court_data.db"
DOWNLOADS_PATH = "downloads"

# Ensure downloads directory exists
os.makedirs(DOWNLOADS_PATH, exist_ok=True)

class DelhiHighCourtScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        self.init_database()
        
        # Initialize OCR if available
        if OCR_AVAILABLE:
            self.ocr_reader = easyocr.Reader(['en'])
        
        # Initialize 2captcha if API key is provided
        if TWOCAPTCHA_AVAILABLE and os.getenv('TWOCAPTCHA_API_KEY'):
            self.captcha_solver = TwoCaptcha(os.getenv('TWOCAPTCHA_API_KEY'))
        else:
            self.captcha_solver = None

    def setup_driver(self):
        """Setup undetected Chrome driver with stealth options"""
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Additional stealth options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Use undetected chromedriver for better CAPTCHA bypass
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def init_database(self):
        """Initialize SQLite database for storing queries and responses"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_type TEXT NOT NULL,
                case_number TEXT NOT NULL,
                filing_year INTEGER NOT NULL,
                query_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                raw_response TEXT,
                parsed_data TEXT,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_query_id INTEGER,
                document_type TEXT,
                document_date TEXT,
                document_url TEXT,
                local_path TEXT,
                download_timestamp DATETIME,
                FOREIGN KEY (case_query_id) REFERENCES case_queries (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    def solve_captcha_ocr(self, captcha_element):
        """Solve CAPTCHA using OCR"""
        if not OCR_AVAILABLE:
            return None
            
        try:
            # Take screenshot of CAPTCHA
            captcha_screenshot = captcha_element.screenshot_as_png
            
            # Save temporarily
            with open('temp_captcha.png', 'wb') as f:
                f.write(captcha_screenshot)
            
            # Read CAPTCHA using OCR
            results = self.ocr_reader.readtext('temp_captcha.png')
            
            # Clean up
            os.remove('temp_captcha.png')
            
            if results:
                # Extract text and clean it
                captcha_text = ''.join([result[1] for result in results])
                captcha_text = re.sub(r'[^a-zA-Z0-9]', '', captcha_text)
                logger.info(f"OCR solved CAPTCHA: {captcha_text}")
                return captcha_text
                
        except Exception as e:
            logger.error(f"OCR CAPTCHA solving failed: {e}")
        
        return None

    def solve_captcha_2captcha(self, captcha_element):
        """Solve CAPTCHA using 2captcha service"""
        if not self.captcha_solver:
            return None
            
        try:
            # Take screenshot of CAPTCHA
            captcha_screenshot = captcha_element.screenshot_as_png
            
            # Save temporarily
            with open('temp_captcha.png', 'wb') as f:
                f.write(captcha_screenshot)
            
            # Send to 2captcha
            result = self.captcha_solver.normal('temp_captcha.png')
            
            # Clean up
            os.remove('temp_captcha.png')
            
            logger.info(f"2captcha solved CAPTCHA: {result['code']}")
            return result['code']
            
        except Exception as e:
            logger.error(f"2captcha CAPTCHA solving failed: {e}")
        
        return None

    def bypass_captcha(self):
        """Attempt to bypass CAPTCHA using multiple methods"""
        try:
            # Wait for CAPTCHA to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "captcha"))
            )
            
            captcha_input = self.driver.find_element(By.NAME, "captcha")
            captcha_image = self.driver.find_element(By.XPATH, "//img[contains(@src, 'captcha')]")
            
            # Try OCR first
            captcha_text = self.solve_captcha_ocr(captcha_image)
            
            # If OCR fails, try 2captcha
            if not captcha_text:
                captcha_text = self.solve_captcha_2captcha(captcha_image)
            
            # If both fail, try manual patterns/common solutions
            if not captcha_text:
                # Some common CAPTCHA patterns for Indian courts
                captcha_text = self.try_common_patterns()
            
            if captcha_text:
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                logger.info("CAPTCHA filled successfully")
                return True
            else:
                logger.warning("Could not solve CAPTCHA automatically")
                return False
                
        except Exception as e:
            logger.error(f"CAPTCHA bypass failed: {e}")
            return False

    def try_common_patterns(self):
        """Try common CAPTCHA patterns for Indian court websites"""
        # This is a placeholder - you would implement specific patterns
        # based on the actual CAPTCHA system used by Delhi High Court
        common_patterns = ["ADMIN", "12345", "ABCDE", "TEST"]
        return None  # Return None if no pattern works

    def search_case(self, case_type, case_number, filing_year):
        """Search for case details on Delhi High Court website"""
        try:
            # Store query in database
            query_id = self.store_query(case_type, case_number, filing_year)
            
            # Navigate to search page
            self.driver.get(DELHI_HC_SEARCH_URL)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "case_type"))
            )
            
            # Fill case type
            case_type_select = Select(self.driver.find_element(By.NAME, "case_type"))
            case_type_select.select_by_visible_text(case_type)
            
            # Fill case number
            case_number_input = self.driver.find_element(By.NAME, "case_no")
            case_number_input.clear()
            case_number_input.send_keys(str(case_number))
            
            # Fill filing year
            year_input = self.driver.find_element(By.NAME, "case_year")
            year_input.clear()
            year_input.send_keys(str(filing_year))
            
            # Handle CAPTCHA
            captcha_solved = self.bypass_captcha()
            if not captcha_solved:
                raise Exception("Could not solve CAPTCHA")
            
            # Submit form
            submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
            submit_button.click()
            
            # Wait for results
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Extract case data
            case_data = self.extract_case_data()
            
            # Update database with success
            self.update_query_status(query_id, 'success', self.driver.page_source, case_data)
            
            return {
                'success': True,
                'data': case_data,
                'query_id': query_id
            }
            
        except Exception as e:
            logger.error(f"Case search failed: {e}")
            self.update_query_status(query_id, 'error', None, None, str(e))
            return {
                'success': False,
                'error': str(e)
            }

    def extract_case_data(self):
        """Extract case details from the results page"""
        try:
            # This would need to be customized based on the actual HTML structure
            # of Delhi High Court's results page
            
            case_data = {
                'caseNumber': '',
                'caseType': '',
                'filingDate': '',
                'status': '',
                'petitioner': '',
                'respondent': '',
                'judge': '',
                'lastHearing': '',
                'orders': []
            }
            
            # Extract basic case information
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        label = cells[0].text.strip().lower()
                        value = cells[1].text.strip()
                        
                        if 'case number' in label:
                            case_data['caseNumber'] = value
                        elif 'case type' in label:
                            case_data['caseType'] = value
                        elif 'filing date' in label:
                            case_data['filingDate'] = value
                        elif 'status' in label:
                            case_data['status'] = value
                        elif 'petitioner' in label:
                            case_data['petitioner'] = value
                        elif 'respondent' in label:
                            case_data['respondent'] = value
                        elif 'judge' in label:
                            case_data['judge'] = value
                        elif 'last hearing' in label:
                            case_data['lastHearing'] = value
            
            # Extract orders and PDF links
            case_data['orders'] = self.extract_orders()
            
            return case_data
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return {}

    def extract_orders(self):
        """Extract orders and judgment information with PDF links"""
        orders = []
        
        try:
            # Look for PDF links
            pdf_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            
            for link in pdf_links:
                order = {
                    'date': self.extract_date_from_link_text(link.text),
                    'details': link.text.strip(),
                    'pdfUrl': urljoin(DELHI_HC_BASE_URL, link.get_attribute('href'))
                }
                orders.append(order)
            
            # Look for order tables
            order_tables = self.driver.find_elements(By.XPATH, "//table[contains(@class, 'order') or contains(., 'Order') or contains(., 'Judgment')]")
            
            for table in order_tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows[1:]:  # Skip header
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        order = {
                            'date': cells[0].text.strip(),
                            'details': cells[1].text.strip(),
                            'pdfUrl': None
                        }
                        
                        # Check for PDF link in this row
                        pdf_link = row.find_element(By.XPATH, ".//a[contains(@href, '.pdf')]")
                        if pdf_link:
                            order['pdfUrl'] = urljoin(DELHI_HC_BASE_URL, pdf_link.get_attribute('href'))
                        
                        orders.append(order)
            
        except Exception as e:
            logger.warning(f"Order extraction failed: {e}")
        
        return orders

    def extract_date_from_link_text(self, text):
        """Extract date from link text using regex"""
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            r'\d{1,2}\s+\w+\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return "Date not found"

    def download_pdf(self, pdf_url, query_id):
        """Download PDF document"""
        try:
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()
            
            # Generate filename
            filename = f"case_{query_id}_{int(time.time())}.pdf"
            local_path = os.path.join(DOWNLOADS_PATH, filename)
            
            # Save file
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Store in database
            self.store_document(query_id, 'PDF', pdf_url, local_path)
            
            return local_path
            
        except Exception as e:
            logger.error(f"PDF download failed: {e}")
            return None

    def store_query(self, case_type, case_number, filing_year):
        """Store query in database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO case_queries (case_type, case_number, filing_year)
            VALUES (?, ?, ?)
        ''', (case_type, case_number, filing_year))
        
        query_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return query_id

    def update_query_status(self, query_id, status, raw_response, parsed_data, error_message=None):
        """Update query status in database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE case_queries 
            SET status = ?, raw_response = ?, parsed_data = ?, error_message = ?
            WHERE id = ?
        ''', (status, raw_response, json.dumps(parsed_data) if parsed_data else None, error_message, query_id))
        
        conn.commit()
        conn.close()

    def store_document(self, query_id, doc_type, doc_url, local_path):
        """Store document information in database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO case_documents (case_query_id, document_type, document_url, local_path, download_timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (query_id, doc_type, doc_url, local_path, datetime.now()))
        
        conn.commit()
        conn.close()

    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

# Initialize scraper instance
scraper = DelhiHighCourtScraper()

# API Routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_file('index.html')

@app.route('/api/fetch-case', methods=['POST'])
def fetch_case():
    """API endpoint to fetch case details"""
    try:
        data = request.get_json()
        
        case_type = data.get('caseType')
        case_number = data.get('caseNumber')
        filing_year = data.get('filingYear')
        
        if not all([case_type, case_number, filing_year]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Search case
        result = scraper.search_case(case_type, case_number, filing_year)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    """API endpoint to download PDF"""
    try:
        data = request.get_json()
        pdf_url = data.get('pdfUrl')
        query_id = data.get('queryId')
        
        if not pdf_url:
            return jsonify({
                'success': False,
                'error': 'PDF URL required'
            }), 400
        
        local_path = scraper.download_pdf(pdf_url, query_id)
        
        if local_path:
            return send_file(local_path, as_attachment=True)
        else:
            return jsonify({
                'success': False,
                'error': 'Download failed'
            }), 500
            
    except Exception as e:
        logger.error(f"PDF download error: {e}")
        return jsonify({
            'success': False,
            'error': 'Download failed'
        }), 500

@app.route('/api/history')
def get_history():
    """Get search history"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, case_type, case_number, filing_year, query_timestamp, status
            FROM case_queries
            ORDER BY query_timestamp DESC
            LIMIT 50
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'case_type': row[1],
                'case_number': row[2],
                'filing_year': row[3],
                'timestamp': row[4],
                'status': row[5]
            })
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch history'
        }), 500

# Static file routes
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        return send_file(filename)
    except:
        return "File not found", 404

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        scraper.close()