# Delhi High Court Case Data Fetcher & Mini-Dashboard

A comprehensive web application that allows users to search and retrieve case details from Delhi High Court with automated CAPTCHA handling using Selenium.

## 🎯 Features

- **Automated Case Search**: Search cases by type, number, and filing year
- **CAPTCHA Handling**: Advanced OCR-based CAPTCHA solving with multiple image processing techniques
- **Real-time Status Updates**: Live updates on search progress
- **Search History**: Track and revisit previous searches
- **Data Export**: Download case details in JSON format
- **Modern UI**: Beautiful, responsive interface with Bootstrap 5
- **Background Processing**: Non-blocking searches with threaded execution
- **SQLite Database**: Persistent storage for searches and results

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Chrome browser
- Tesseract OCR

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd delhi-high-court-scraper
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies**

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   sudo apt-get install chromium-browser
   ```

   **macOS:**
   ```bash
   brew install tesseract
   brew install --cask google-chrome
   ```

   **Windows:**
   - Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add Tesseract to your PATH
   - Install Google Chrome

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 📋 Usage

### Searching Cases

1. **Select Case Type**: Choose from common Delhi High Court case types
   - WP(C) - Writ Petition (Civil)
   - WP(Crl) - Writ Petition (Criminal)
   - CM - Civil Miscellaneous
   - CRL.A - Criminal Appeal
   - And more...

2. **Enter Case Number**: Input the case number (e.g., 12345)

3. **Select Filing Year** (Optional): Choose the year when the case was filed

4. **Submit Search**: Click "Search Case" and wait for results

### CAPTCHA Handling

The system automatically:
- Detects CAPTCHA images on the court website
- Applies multiple image processing techniques
- Uses OCR to extract text
- Submits the CAPTCHA solution
- Retries if unsuccessful (up to 3 attempts)

### Viewing Results

Case details include:
- Case number and filing date
- Party names (petitioners, respondents)
- Current status
- Hearing dates and details
- Orders and judgments
- Complete case timeline

### Search History

- View all previous searches
- Click on any historical search to view results
- Track search status (pending, completed, failed)
- Download results from completed searches

## 🏗️ Architecture

### Backend Components

1. **Flask Application** (`app.py`)
   - RESTful API endpoints
   - Background task management
   - Database operations

2. **Selenium Scraper** (`court_scraper.py`)
   - Web automation with Chrome WebDriver
   - CAPTCHA detection and solving
   - Data extraction and parsing

3. **Database** (SQLite)
   - Search history tracking
   - Case data storage
   - Status management

### Frontend Components

1. **Modern Web Interface** (`templates/index.html`)
   - Bootstrap 5 styling
   - Real-time status updates
   - Responsive design

2. **JavaScript Features**
   - AJAX requests
   - Status polling
   - Dynamic content updates

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configurations:

```env
FLASK_DEBUG=True
FLASK_PORT=5000
CHROME_HEADLESS=True
CAPTCHA_TIMEOUT=30
MAX_RETRY_ATTEMPTS=3
```

### Selenium Options

Modify Chrome options in `court_scraper.py`:

```python
chrome_options.add_argument('--headless')  # Run in background
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
```

### OCR Configuration

Tesseract settings for better CAPTCHA recognition:

```python
custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
```

## 📊 API Endpoints

### POST /search
Start a new case search
```json
{
  "case_type": "WP(C)",
  "case_number": "12345",
  "filing_year": "2023"
}
```

### GET /status/{search_id}
Get search status and results
```json
{
  "status": "completed",
  "data": { ... },
  "timestamp": "2024-01-01T12:00:00"
}
```

### GET /history
Get search history
```json
[
  {
    "id": 1,
    "case_type": "WP(C)",
    "case_number": "12345",
    "status": "completed",
    "timestamp": "2024-01-01T12:00:00"
  }
]
```

### GET /download/{search_id}
Download case data as JSON file

## 🧪 Testing

### Manual Testing

1. **Test Case Search**
   ```bash
   python court_scraper.py
   ```

2. **Test CAPTCHA Solving**
   - Monitor saved CAPTCHA images in project directory
   - Check OCR accuracy in logs

3. **Test Web Interface**
   - Open browser developer tools
   - Monitor network requests
   - Verify real-time updates

### Unit Testing

```bash
python -m pytest tests/
```

## 🚨 Troubleshooting

### Common Issues

1. **ChromeDriver Issues**
   - Ensure Chrome browser is installed
   - WebDriver automatically downloads compatible ChromeDriver

2. **CAPTCHA Solving Failures**
   - Check Tesseract installation
   - Verify image processing dependencies
   - Monitor CAPTCHA images saved locally

3. **Network Timeouts**
   - Check internet connection
   - Verify Delhi High Court website accessibility
   - Increase timeout values in configuration

4. **Permission Errors**
   - Run with appropriate permissions
   - Check file system access for database and temp files

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Legal Considerations

- **Ethical Usage**: This tool is for educational and legitimate legal research purposes
- **Rate Limiting**: Built-in delays to avoid overwhelming court servers
- **Compliance**: Ensure compliance with court website terms of service
- **No Warranty**: Use at your own risk, verify all extracted data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Delhi High Court for providing online case status services
- Selenium WebDriver team for web automation tools
- Tesseract OCR for optical character recognition
- Bootstrap team for UI components

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**⚡ Quick Demo**

1. `python app.py`
2. Open `http://localhost:5000`
3. Select "WP(C)" case type
4. Enter case number "12345"
5. Select year "2023"
6. Click "Search Case"
7. Watch real-time status updates
8. View extracted case details
9. Download results as JSON

**Built with ❤️ for the legal community**