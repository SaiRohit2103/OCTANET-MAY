# Court Data Fetcher & Mini-Dashboard

A web application that allows users to fetch case metadata and latest orders/judgments from Indian Courts, specifically designed for Delhi High Court and District Courts portals.

## Features

- **Case Search**: Search for cases using Case Type, Case Number, and Filing Year
- **Court Selection**: Choose between Delhi High Court and District Courts portal
- **Case Details**: View comprehensive case information including:
  - Case number and court details
  - Filing date and current status
  - Petitioner and respondent information
  - Hearing dates (last and next)
  - Presiding judge information
- **Orders & Judgments**: Display latest orders with:
  - Order dates and titles
  - Order content/summary
  - PDF download links (mock implementation)
- **Search History**: Track recent searches with local storage
- **Error Handling**: User-friendly error messages for invalid inputs and site issues
- **Responsive Design**: Modern, mobile-friendly interface
- **CAPTCHA Protection**: 
  - Simple mathematical CAPTCHA (default)
  - Google reCAPTCHA v2 (optional)
  - Toggle between CAPTCHA types
  - Real-time validation feedback

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python Flask
- **Database**: SQLite
- **Web Scraping**: BeautifulSoup4, Requests
- **Styling**: Modern CSS with gradients and animations

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project files**
   ```bash
   # If using git
   git clone <repository-url>
   cd court-data-fetcher
   
   # Or download and extract the files to a directory
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Configure reCAPTCHA (Optional)**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your reCAPTCHA keys (get them from https://www.google.com/recaptcha/admin/create)
   # RECAPTCHA_SITE_KEY=your-site-key-here
   # RECAPTCHA_SECRET_KEY=your-secret-key-here
   ```

5. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - The application should be running and ready to use

### Alternative Setup with Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv court_fetcher_env

# Activate virtual environment
# On Windows:
court_fetcher_env\Scripts\activate
# On macOS/Linux:
source court_fetcher_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Usage

1. **Select Case Type**: Choose from dropdown (CRL, CIV, WP, FAO, etc.)
2. **Enter Case Number**: Format should be `123/2023`
3. **Enter Filing Year**: Year when the case was filed
4. **Select Court**: Choose between Delhi High Court or District Courts
5. **Complete CAPTCHA**: 
   - **Math CAPTCHA**: Solve the simple math problem (default)
   - **reCAPTCHA**: Check the "Use Google reCAPTCHA instead" box for reCAPTCHA
6. **Search**: Click the search button to fetch case data
7. **View Results**: Case details and orders will be displayed
8. **Download Orders**: Click download links for PDF files (demo functionality)

### Example Search

- **Case Type**: WP (Writ Petition)
- **Case Number**: 1234/2023
- **Filing Year**: 2023
- **Court**: Delhi High Court

## Court Choice Explanation

### Delhi High Court
- **URL**: https://delhihighcourt.nic.in/
- **Status**: ✅ **Implemented** (with mock data for demonstration)
- **Features**: 
  - Case status search
  - Order and judgment retrieval
  - Party information
  - Hearing dates
- **Note**: The current implementation uses mock data for demonstration. Real implementation would require:
  - CAPTCHA solving mechanisms
  - Session management
  - Form token handling
  - Proper HTML parsing based on actual website structure

### District Courts Portal
- **URL**: https://districts.ecourts.gov.in/
- **Status**: ❌ **Not Implemented**
- **Reason**: District Courts portal has complex authentication and CAPTCHA systems
- **Implementation Notes**: Would require additional development for:
  - Multi-step authentication
  - CAPTCHA solving (potentially using services like 2captcha)
  - State-specific court selection
  - Different data formats and structures

**Recommendation**: Start with Delhi High Court for reliable scraping, as it has a more consistent structure and fewer anti-bot measures.

## CAPTCHA Configuration

The application includes two types of CAPTCHA protection:

### 1. Mathematical CAPTCHA (Default)
- **Status**: ✅ **Ready to use**
- **Features**: 
  - Simple arithmetic problems (addition, subtraction, multiplication)
  - Real-time validation feedback
  - Automatic refresh on incorrect answers
  - No external dependencies
- **Best for**: Quick setup, offline environments, simple bot protection

### 2. Google reCAPTCHA v2
- **Status**: ⚙️ **Requires configuration**
- **Setup Steps**:
  1. Visit [Google reCAPTCHA Admin](https://www.google.com/recaptcha/admin/create)
  2. Create a new site with reCAPTCHA v2 "I'm not a robot" checkbox
  3. Add your domain (use `localhost` for development)
  4. Copy the Site Key and Secret Key
  5. Update your `.env` file:
     ```bash
     RECAPTCHA_SITE_KEY=your-site-key-here
     RECAPTCHA_SECRET_KEY=your-secret-key-here
     ```
  6. Restart the application
- **Best for**: Production environments, advanced bot protection

### CAPTCHA Features
- **Toggle Option**: Users can switch between math and reCAPTCHA
- **Visual Feedback**: Green/red borders indicate correct/incorrect answers
- **Auto-refresh**: New CAPTCHA generated after each submission
- **Mobile Responsive**: Works on all device sizes

## Database Schema

The application uses SQLite with two main tables:

### queries
- Logs all search queries with timestamps
- Tracks success/failure rates
- Stores error messages for debugging

### case_data
- Stores cached case information
- Reduces redundant API calls
- Enables offline viewing of previously searched cases

## File Structure

```
court-data-fetcher/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── court_data.db         # SQLite database (created automatically)
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── styles.css        # CSS styling
    └── script.js         # Frontend JavaScript
```

## API Endpoints

- `GET /` - Serve main application page
- `POST /api/search` - Search for case data
- `GET /api/history` - Get query history
- `GET /download_order/<filename>` - Download order PDFs (mock)

## Error Handling

The application includes comprehensive error handling for:

- **Invalid case number format**: Must be in format `123/2023`
- **Missing required fields**: All form fields are validated
- **Network errors**: Graceful handling of connection issues
- **Court website downtime**: User-friendly error messages
- **Invalid year ranges**: Year validation between 2000 and current year

## Security Considerations

- Input validation and sanitization
- SQL injection prevention using parameterized queries
- CORS configuration for API access
- Rate limiting should be implemented for production use

## Future Enhancements

1. **Real Web Scraping**: Implement actual scraping logic for Delhi HC
2. **CAPTCHA Solving**: Integrate CAPTCHA solving services
3. **District Courts**: Complete implementation for district courts portal
4. **PDF Processing**: Extract and index PDF content
5. **Advanced Search**: Add filters for date ranges, case types, etc.
6. **User Authentication**: Add user accounts and saved searches
7. **Notifications**: Email/SMS alerts for case updates
8. **API Rate Limiting**: Implement proper rate limiting
9. **Caching**: Redis-based caching for better performance
10. **Monitoring**: Add logging and monitoring capabilities

## Legal Disclaimer

This application is built for educational and research purposes. Users should:

- Respect the terms of service of court websites
- Use the application responsibly and not overload court servers
- Verify all information obtained through official channels
- Understand that web scraping may have legal implications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or contributions, please:

1. Check the existing issues in the repository
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

---

**Note**: This is a demonstration application. For production use, additional security measures, error handling, and legal compliance checks should be implemented.