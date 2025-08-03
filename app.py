from flask import Flask, render_template, request, jsonify, send_file
import json
import sqlite3
import os
from datetime import datetime
from court_scraper import DelhiHighCourtScraper
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('court_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_type TEXT NOT NULL,
            case_number TEXT NOT NULL,
            filing_year TEXT,
            search_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            result_data TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS case_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT NOT NULL,
            case_type TEXT,
            filing_year TEXT,
            parties TEXT,
            filing_date TEXT,
            hearings TEXT,
            orders TEXT,
            status TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_case():
    try:
        data = request.get_json()
        case_type = data.get('case_type')
        case_number = data.get('case_number')
        filing_year = data.get('filing_year', '')
        
        if not case_type or not case_number:
            return jsonify({'error': 'Case type and number are required'}), 400
        
        # Store search request in database
        conn = sqlite3.connect('court_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO searches (case_type, case_number, filing_year, status)
            VALUES (?, ?, ?, 'pending')
        ''', (case_type, case_number, filing_year))
        search_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Start scraping in background
        def scrape_data():
            scraper = DelhiHighCourtScraper()
            try:
                result = scraper.search_case(case_type, case_number, filing_year)
                
                # Update database with results
                conn = sqlite3.connect('court_data.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE searches 
                    SET result_data = ?, status = 'completed'
                    WHERE id = ?
                ''', (json.dumps(result), search_id))
                
                if result.get('success'):
                    # Store detailed case data
                    case_info = result.get('data', {})
                    cursor.execute('''
                        INSERT OR REPLACE INTO case_data 
                        (case_number, case_type, filing_year, parties, filing_date, 
                         hearings, orders, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        case_number, case_type, filing_year,
                        json.dumps(case_info.get('parties', [])),
                        case_info.get('filing_date', ''),
                        json.dumps(case_info.get('hearings', [])),
                        json.dumps(case_info.get('orders', [])),
                        case_info.get('status', '')
                    ))
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                logger.error(f"Scraping error: {str(e)}")
                conn = sqlite3.connect('court_data.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE searches 
                    SET status = 'failed', result_data = ?
                    WHERE id = ?
                ''', (json.dumps({'error': str(e)}), search_id))
                conn.commit()
                conn.close()
            finally:
                scraper.close()
        
        thread = threading.Thread(target=scrape_data)
        thread.start()
        
        return jsonify({
            'message': 'Search initiated successfully',
            'search_id': search_id
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status/<int:search_id>')
def get_search_status(search_id):
    try:
        conn = sqlite3.connect('court_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT status, result_data, search_timestamp
            FROM searches WHERE id = ?
        ''', (search_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Search not found'}), 404
        
        status, result_data, timestamp = result
        response = {
            'status': status,
            'timestamp': timestamp
        }
        
        if result_data:
            response['data'] = json.loads(result_data)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def get_search_history():
    try:
        conn = sqlite3.connect('court_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, case_type, case_number, filing_year, 
                   search_timestamp, status
            FROM searches 
            ORDER BY search_timestamp DESC 
            LIMIT 50
        ''')
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'id': row[0],
                'case_type': row[1],
                'case_number': row[2],
                'filing_year': row[3],
                'timestamp': row[4],
                'status': row[5]
            })
        
        return jsonify(history)
        
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<int:search_id>')
def download_results(search_id):
    try:
        conn = sqlite3.connect('court_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT result_data FROM searches WHERE id = ?
        ''', (search_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            return jsonify({'error': 'No data found'}), 404
        
        # Create temporary JSON file
        filename = f"case_data_{search_id}.json"
        with open(filename, 'w') as f:
            f.write(result[0])
        
        return send_file(filename, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)