from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import re
from datetime import datetime
import logging
from urllib.parse import urljoin, quote
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    """Initialize SQLite database for logging queries and responses"""
    conn = sqlite3.connect('court_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_type TEXT NOT NULL,
            case_number TEXT NOT NULL,
            filing_year INTEGER NOT NULL,
            court_type TEXT NOT NULL,
            query_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN NOT NULL,
            response_data TEXT,
            error_message TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS case_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_identifier TEXT UNIQUE NOT NULL,
            court_type TEXT NOT NULL,
            case_info TEXT NOT NULL,
            orders_data TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

class DelhiHighCourtScraper:
    """Scraper for Delhi High Court website"""
    
    def __init__(self):
        self.base_url = "https://delhihighcourt.nic.in"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_case(self, case_type, case_number, filing_year):
        """Search for a case on Delhi High Court website"""
        try:
            # Construct search URL and parameters
            search_url = f"{self.base_url}/case_status"
            
            # Parameters for the search (these would need to be adjusted based on actual website structure)
            search_params = {
                'case_type': case_type,
                'case_number': case_number,
                'filing_year': filing_year
            }
            
            # Note: This is a simplified implementation
            # Real implementation would need to handle:
            # 1. CAPTCHA solving
            # 2. Session management
            # 3. Form tokens/CSRF protection
            # 4. Proper error handling for different response types
            
            # For demonstration, we'll return mock data
            # In real implementation, you would:
            # response = self.session.post(search_url, data=search_params)
            # soup = BeautifulSoup(response.content, 'html.parser')
            # return self.parse_case_data(soup)
            
            return self.get_mock_case_data(case_type, case_number, filing_year)
            
        except Exception as e:
            logger.error(f"Error searching case: {str(e)}")
            raise
    
    def get_mock_case_data(self, case_type, case_number, filing_year):
        """Return mock case data for demonstration"""
        return {
            'case_info': {
                'case_number': f"{case_type} {case_number}",
                'court': 'Delhi High Court',
                'filing_date': f"15-03-{filing_year}",
                'status': 'Pending',
                'petitioner': 'ABC Corporation',
                'respondent': 'State of Delhi & Ors.',
                'last_hearing': '10-12-2023',
                'next_hearing': '15-01-2024',
                'judge': 'Hon\'ble Justice A.K. Sharma',
                'case_type': case_type,
                'filing_year': filing_year
            },
            'orders': [
                {
                    'date': '10-12-2023',
                    'title': 'Order on Application for Interim Relief',
                    'content': 'The court has considered the application for interim relief filed by the petitioner. After hearing the learned counsel for both parties and perusing the record, the court is of the opinion that prima facie case has been made out. However, considering the balance of convenience and irreparable injury, the court deems it appropriate to grant limited interim relief.',
                    'download_url': f'/download_order/{case_type}_{case_number}_{filing_year}_1.pdf'
                },
                {
                    'date': '25-11-2023',
                    'title': 'Notice to Respondent',
                    'content': 'Notice issued to the respondent to file reply within 4 weeks from today. The respondent is directed to serve advance copy of the reply to the counsel for the petitioner. Next date of hearing is fixed for 10-12-2023.',
                    'download_url': f'/download_order/{case_type}_{case_number}_{filing_year}_2.pdf'
                },
                {
                    'date': f'15-03-{filing_year}',
                    'title': 'Case Filed - Admission Hearing',
                    'content': f'{case_type} Petition filed by the petitioner against the respondents. Registry to check compliance with rules and regulations. List for admission hearing on 25-11-2023.',
                    'download_url': f'/download_order/{case_type}_{case_number}_{filing_year}_3.pdf'
                }
            ]
        }
    
    def parse_case_data(self, soup):
        """Parse case data from BeautifulSoup object"""
        # This would contain the actual parsing logic for the Delhi HC website
        # Implementation would depend on the actual HTML structure
        pass

class DistrictCourtScraper:
    """Scraper for District Courts eCourts portal"""
    
    def __init__(self):
        self.base_url = "https://districts.ecourts.gov.in"
        self.session = requests.Session()
    
    def search_case(self, case_type, case_number, filing_year):
        """Search for a case on District Courts portal"""
        # This would implement district court scraping
        # For now, return an error as mentioned in requirements
        raise NotImplementedError("District Courts portal integration not yet implemented")

def log_query(case_type, case_number, filing_year, court_type, success, response_data=None, error_message=None):
    """Log query to database"""
    conn = sqlite3.connect('court_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO queries (case_type, case_number, filing_year, court_type, success, response_data, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (case_type, case_number, filing_year, court_type, success, 
          json.dumps(response_data) if response_data else None, error_message))
    
    conn.commit()
    conn.close()

def save_case_data(case_identifier, court_type, case_info, orders_data):
    """Save or update case data in database"""
    conn = sqlite3.connect('court_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO case_data (case_identifier, court_type, case_info, orders_data, last_updated)
        VALUES (?, ?, ?, ?, ?)
    ''', (case_identifier, court_type, json.dumps(case_info), 
          json.dumps(orders_data), datetime.now()))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_case():
    """API endpoint to search for case data"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['caseType', 'caseNumber', 'filingYear', 'courtType']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        case_type = data['caseType']
        case_number = data['caseNumber']
        filing_year = int(data['filingYear'])
        court_type = data['courtType']
        
        # Validate case number format
        if not re.match(r'^\d+/\d{4}$', case_number):
            return jsonify({
                'success': False,
                'error': 'Invalid case number format. Use format: 123/2023'
            }), 400
        
        # Choose appropriate scraper
        if court_type == 'delhi-hc':
            scraper = DelhiHighCourtScraper()
        elif court_type == 'district-courts':
            scraper = DistrictCourtScraper()
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid court type'
            }), 400
        
        # Perform search
        try:
            case_data = scraper.search_case(case_type, case_number, filing_year)
            
            # Save to database
            case_identifier = f"{court_type}_{case_type}_{case_number}_{filing_year}"
            save_case_data(case_identifier, court_type, case_data['case_info'], case_data['orders'])
            
            # Log successful query
            log_query(case_type, case_number, filing_year, court_type, True, case_data)
            
            return jsonify({
                'success': True,
                'data': case_data
            })
            
        except NotImplementedError as e:
            error_msg = str(e)
            log_query(case_type, case_number, filing_year, court_type, False, error_message=error_msg)
            return jsonify({
                'success': False,
                'error': error_msg
            }), 501
            
        except Exception as e:
            error_msg = f"Error fetching case data: {str(e)}"
            logger.error(error_msg)
            log_query(case_type, case_number, filing_year, court_type, False, error_message=error_msg)
            return jsonify({
                'success': False,
                'error': 'Failed to fetch case data. Please try again later.'
            }), 500
    
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/history')
def get_query_history():
    """Get query history from database"""
    try:
        conn = sqlite3.connect('court_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT case_type, case_number, filing_year, court_type, query_time, success
            FROM queries
            ORDER BY query_time DESC
            LIMIT 50
        ''')
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'case_type': row[0],
                'case_number': row[1],
                'filing_year': row[2],
                'court_type': row[3],
                'query_time': row[4],
                'success': bool(row[5])
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch query history'
        }), 500

@app.route('/download_order/<filename>')
def download_order(filename):
    """Mock endpoint for downloading order PDFs"""
    # In a real implementation, this would serve actual PDF files
    return jsonify({
        'message': 'PDF download functionality would be implemented here',
        'filename': filename
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)