# Delhi High Court Data Fetcher & Mini-Dashboard

A web application that allows users to fetch case metadata and latest orders/judgments from Delhi High Court with automated CAPTCHA handling and PDF download functionality.

## Features

### 🔍 Core Functionality
- **Case Search**: Search by Case Type, Case Number, and Filing Year
- **CAPTCHA Bypass**: Automated CAPTCHA solving using OCR and 2captcha service
- **Data Extraction**: Extracts parties' names, filing dates, next hearing dates, and order/judgment PDF links
- **PDF Downloads**: Direct download of court orders and judgments

### 🎨 User Interface
- **Modern Design**: Beautiful and responsive web interface
- **Real-time Updates**: Loading indicators and progress feedback
- **Search History**: Local storage of recent searches
- **Mobile Friendly**: Responsive design for all devices

### 🛠 Technical Features
- **Database Storage**: SQLite database for logging queries and responses
- **Error Handling**: User-friendly error messages for invalid case numbers or site downtime
- **Stealth Browsing**: Undetected Chrome driver to bypass anti-bot measures
- **API Architecture**: RESTful API backend with clean separation of concerns

## Court Support

Currently supports **Delhi High Court** with the following case types:
- Criminal Appeal (CRL.A.)
- Criminal Revision (CRL.REV.)
- Writ Petition Civil (W.P.(C))
- Writ Petition Criminal (W.P.(CRL))
- First Appeal from Order (FAO)
- Regular First Appeal (RFA)
- Civil Suit Original Side (CS(OS))
- Civil Miscellaneous Petition (CMP)
- Bail Application (BAIL APPLN.)
- Contempt Petition (CONTEMPT)

## Installation

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver (automatically managed by undetected-chromedriver)

### Setup Instructions

1. **Clone the repository**
```bash
git clone <repository-url>
cd delhi-high-court-fetcher
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration** (Optional)
Create a `.env` file in the root directory:
```env
# Optional: 2captcha API key for advanced CAPTCHA solving
TWOCAPTCHA_API_KEY=your_api_key_here

# Optional: Custom configurations
FLASK_ENV=development
FLASK_DEBUG=True
```

5. **Run the application**
```bash
python app.py
```

6. **Access the application**
Open your browser and navigate to `http://localhost:5000`

## Usage Guide

### Basic Search
1. Select the **Case Type** from the dropdown
2. Enter the **Case Number** (numeric)
3. Enter the **Filing Year** (e.g., 2024)
4. Click **"Fetch Case Details"**

### CAPTCHA Handling
The application automatically handles CAPTCHAs using:
1. **OCR (EasyOCR)**: Primary method for text-based CAPTCHAs
2. **2captcha Service**: Fallback for complex CAPTCHAs (requires API key)
3. **Pattern Matching**: Common patterns for known CAPTCHA types

### PDF Downloads
- Click the **"Download PDF"** button next to any order/judgment
- PDFs are downloaded directly from the court website
- Downloaded files are stored in the `downloads/` directory

### Search History
- Recent searches are automatically saved
- Click on any history item to reload the search
- History is stored locally in your browser

## API Documentation

### Endpoints

#### POST `/api/fetch-case`
Fetch case details from Delhi High Court.

**Request Body:**
```json
{
    "caseType": "W.P.(C)",
    "caseNumber": "1234",
    "filingYear": 2024
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "caseNumber": "W.P.(C) 1234/2024",
        "caseType": "Writ Petition (Civil)",
        "filingDate": "15-01-2024",
        "status": "Pending",
        "petitioner": "John Doe",
        "respondent": "State of Delhi",
        "judge": "Hon'ble Justice XYZ",
        "lastHearing": "15-11-2024",
        "orders": [
            {
                "date": "15-11-2024",
                "details": "Next date of hearing",
                "pdfUrl": "https://delhihighcourt.nic.in/orders/order123.pdf"
            }
        ]
    }
}
```

#### POST `/api/download-pdf`
Download PDF document.

**Request Body:**
```json
{
    "pdfUrl": "https://delhihighcourt.nic.in/orders/order123.pdf",
    "queryId": 1
}
```

#### GET `/api/history`
Get search history from database.

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "case_type": "W.P.(C)",
            "case_number": "1234",
            "filing_year": 2024,
            "timestamp": "2024-01-15T10:30:00Z",
            "status": "success"
        }
    ]
}
```

## Database Schema

### Tables

#### `case_queries`
```sql
CREATE TABLE case_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_type TEXT NOT NULL,
    case_number TEXT NOT NULL,
    filing_year INTEGER NOT NULL,
    query_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',
    raw_response TEXT,
    parsed_data TEXT,
    error_message TEXT
);
```

#### `case_documents`
```sql
CREATE TABLE case_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_query_id INTEGER,
    document_type TEXT,
    document_date TEXT,
    document_url TEXT,
    local_path TEXT,
    download_timestamp DATETIME,
    FOREIGN KEY (case_query_id) REFERENCES case_queries (id)
);
```

## Configuration Options

### Environment Variables
- `TWOCAPTCHA_API_KEY`: API key for 2captcha service
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable debug mode (True/False)

### Chrome Options
The application uses stealth browsing with the following Chrome options:
- `--no-sandbox`: Disable sandbox for compatibility
- `--disable-dev-shm-usage`: Overcome limited resource problems
- `--disable-gpu`: Disable GPU acceleration
- `--disable-blink-features=AutomationControlled`: Hide automation

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   - Ensure Google Chrome is installed
   - The application automatically manages ChromeDriver

2. **CAPTCHA Solving Failures**
   - Check internet connection
   - Verify 2captcha API key if using the service
   - Consider manual CAPTCHA solving for complex cases

3. **Website Access Issues**
   - Verify Delhi High Court website is accessible
   - Check for website maintenance or changes

4. **PDF Download Failures**
   - Ensure sufficient disk space
   - Check PDF URL validity
   - Verify network connectivity

### Error Messages
- **"Could not solve CAPTCHA"**: CAPTCHA solving failed, try again
- **"Network error"**: Connection issues with the court website
- **"Invalid case number"**: Case not found or incorrect details
- **"Missing required fields"**: Incomplete form submission

## Legal Disclaimer

This tool is intended for legitimate legal research purposes only. Users must:
- Respect the Delhi High Court website's terms of service
- Use the tool responsibly and not overload the server
- Ensure compliance with applicable laws and regulations
- Verify all extracted information independently

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
1. Check the troubleshooting section
2. Review the GitHub issues
3. Create a new issue with detailed information

## Acknowledgments

- Delhi High Court for providing public access to case information
- EasyOCR for OCR capabilities
- 2captcha for CAPTCHA solving services
- Selenium WebDriver for browser automation
- Flask framework for the web application

---

**Note**: This tool is for educational and research purposes. Always ensure you have the right to access and use the information you're retrieving.