# 🚀 Quick Start Guide

## Delhi High Court Case Data Fetcher with CAPTCHA Access

### 📋 What You Get

This complete codebase provides:

- **🏛️ Court Data Scraper**: Automated case search for Delhi High Court
- **🔐 CAPTCHA Solver**: Advanced OCR-based CAPTCHA handling with Selenium
- **🌐 Web Interface**: Modern Bootstrap 5 dashboard
- **⚡ Real-time Updates**: Live search status with progress tracking
- **📊 Data Export**: JSON download of case details
- **🗄️ Search History**: SQLite database with persistent storage

### ⚡ Super Quick Start (3 commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the application
python run.py

# 3. Open browser
# Go to: http://localhost:5000
```

### 🔧 Full Setup

```bash
# Option 1: Automated installation
./install.sh

# Option 2: Manual setup
pip install -r requirements.txt
python test_setup.py  # Check if everything works
python run.py         # Start the app
```

### 🎯 Usage Examples

1. **Search a Writ Petition**:
   - Case Type: `WP(C)`
   - Case Number: `12345`
   - Year: `2023`

2. **Search Criminal Appeal**:
   - Case Type: `CRL.A`
   - Case Number: `6789`
   - Year: `2024`

### 🔐 CAPTCHA Features

The system automatically:
- ✅ Detects CAPTCHA images
- ✅ Applies image preprocessing (grayscale, threshold, blur)
- ✅ Uses Tesseract OCR for text extraction
- ✅ Retries failed attempts (up to 3 times)
- ✅ Saves CAPTCHA images for manual review

### 📁 Project Structure

```
delhi-high-court-scraper/
├── app.py                 # Flask web application
├── court_scraper.py       # Selenium scraper with CAPTCHA handling
├── templates/
│   └── index.html         # Modern web interface
├── requirements.txt       # Python dependencies
├── run.py                 # Application launcher
├── demo.py               # Demo script
├── test_setup.py         # Setup verification
├── install.sh            # Automated installer
├── README.md             # Comprehensive documentation
└── .env.example          # Configuration template
```

### 🌟 Key Features Implemented

#### 🔍 Case Search
- Multiple case types (WP(C), CM, CRL.A, etc.)
- Optional filing year
- Background processing
- Real-time status updates

#### 🔐 Advanced CAPTCHA Handling
```python
# Multiple image processing techniques
- Grayscale conversion
- Binary thresholding
- Gaussian blur + OTSU thresholding
- Morphological operations
- Custom Tesseract configuration
```

#### 🎨 Modern UI
- Responsive Bootstrap 5 design
- Tabbed interface (Search + History)
- Loading animations
- Status indicators
- Download functionality

#### 🗄️ Data Management
- SQLite database for persistence
- Search history tracking
- JSON export functionality
- Error logging

### 🚨 Dependencies Required

**Python Packages** (auto-installed):
- selenium==4.16.0
- flask==3.0.0
- requests==2.31.0
- beautifulsoup4==4.12.2
- webdriver-manager==4.0.1
- pillow==10.1.0
- pytesseract==0.3.10
- opencv-python==4.8.1.78
- numpy==1.25.2

**System Dependencies**:
- Google Chrome or Chromium
- Tesseract OCR

### 🎭 Demo Mode

```bash
# Run demo with sample cases
python demo.py

# Choose from:
# 1. Case Search Demo
# 2. CAPTCHA Solving Info  
# 3. Both
```

### 🔧 Configuration

Copy `.env.example` to `.env` and customize:

```env
FLASK_DEBUG=True
CHROME_HEADLESS=True
CAPTCHA_TIMEOUT=30
MAX_RETRY_ATTEMPTS=3
```

### 📊 API Endpoints

- `POST /search` - Start case search
- `GET /status/{id}` - Check search status
- `GET /history` - View search history
- `GET /download/{id}` - Download results

### 🎯 Example Search Flow

1. **User Input**: WP(C) 12345/2023
2. **Backend**: Selenium navigates to court website
3. **CAPTCHA**: Automatic detection and solving
4. **Extraction**: Parse case details, hearings, orders
5. **Storage**: Save to SQLite database
6. **Display**: Show results in web interface
7. **Export**: Download as JSON file

### 🛠️ Troubleshooting

**Common Issues**:
```bash
# Missing dependencies
pip install -r requirements.txt

# System dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr chromium-browser

# Test setup
python test_setup.py
```

### ⚖️ Legal Notice

- For educational and legitimate legal research only
- Respects court website with built-in delays
- Verify all extracted data independently
- Comply with website terms of service

### 🎉 Ready to Use!

Your complete Delhi High Court case data fetcher with CAPTCHA handling is ready. The system includes everything from web scraping to a modern dashboard interface.

**Start now**: `python run.py` → Open `http://localhost:5000`

---

Built with ❤️ for the legal community using Python, Selenium, Flask, and modern web technologies.