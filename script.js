// Court Data Fetcher Frontend JavaScript

class CourtDataFetcher {
    constructor() {
        this.apiUrl = '/api';
        this.searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSearchHistory();
    }

    bindEvents() {
        const form = document.getElementById('caseForm');
        const clearBtn = document.getElementById('clearForm');

        form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        clearBtn.addEventListener('click', () => this.clearForm());

        // Auto-save form data
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => this.saveFormData());
        });

        // Load saved form data
        this.loadFormData();
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const caseData = {
            caseType: formData.get('caseType'),
            caseNumber: formData.get('caseNumber'),
            filingYear: formData.get('filingYear')
        };

        // Validate form
        if (!this.validateForm(caseData)) {
            return;
        }

        // Show loading state
        this.showLoading();

        try {
            // Call backend API
            const response = await this.fetchCaseData(caseData);
            
            if (response.success) {
                this.displayResults(response.data);
                this.addToHistory(caseData, response.data, 'success');
            } else {
                this.showError(response.error || 'Failed to fetch case data');
                this.addToHistory(caseData, null, 'error');
            }
        } catch (error) {
            console.error('Error fetching case data:', error);
            this.showError('Network error. Please check your connection and try again.');
            this.addToHistory(caseData, null, 'error');
        } finally {
            this.hideLoading();
        }
    }

    validateForm(data) {
        if (!data.caseType) {
            this.showError('Please select a case type');
            return false;
        }

        if (!data.caseNumber || isNaN(data.caseNumber)) {
            this.showError('Please enter a valid case number');
            return false;
        }

        if (!data.filingYear || data.filingYear < 1950 || data.filingYear > new Date().getFullYear()) {
            this.showError('Please enter a valid filing year');
            return false;
        }

        return true;
    }

    async fetchCaseData(caseData) {
        const response = await fetch(`${this.apiUrl}/fetch-case`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(caseData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    showLoading() {
        const resultsContainer = document.getElementById('resultsContainer');
        const loading = document.getElementById('loading');
        const caseDetails = document.getElementById('caseDetails');

        resultsContainer.style.display = 'block';
        loading.style.display = 'block';
        caseDetails.innerHTML = '';
        
        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        loading.style.display = 'none';
    }

    displayResults(data) {
        const caseDetails = document.getElementById('caseDetails');
        
        let html = `
            <div class="case-info">
                <div class="info-item">
                    <label>Case Number:</label>
                    <div class="value">${data.caseNumber || 'N/A'}</div>
                </div>
                <div class="info-item">
                    <label>Case Type:</label>
                    <div class="value">${data.caseType || 'N/A'}</div>
                </div>
                <div class="info-item">
                    <label>Filing Date:</label>
                    <div class="value">${data.filingDate || 'N/A'}</div>
                </div>
                <div class="info-item">
                    <label>Status:</label>
                    <div class="value">${data.status || 'N/A'}</div>
                </div>
                <div class="info-item">
                    <label>Petitioner:</label>
                    <div class="value">${data.petitioner || 'N/A'}</div>
                </div>
                <div class="info-item">
                    <label>Respondent:</label>
                    <div class="value">${data.respondent || 'N/A'}</div>
                </div>
                <div class="info-item">
                    <label>Judge:</label>
                    <div class="value">${data.judge || 'N/A'}</div>
                </div>
                <div class="info-item">
                    <label>Last Hearing:</label>
                    <div class="value">${data.lastHearing || 'N/A'}</div>
                </div>
            </div>
        `;

        if (data.orders && data.orders.length > 0) {
            html += `
                <div class="orders-list">
                    <h3><i class="fas fa-file-pdf"></i> Orders & Judgments</h3>
                    ${data.orders.map(order => `
                        <div class="order-item">
                            <div class="order-date">${order.date}</div>
                            <div class="order-details">${order.details}</div>
                            ${order.pdfUrl ? `
                                <a href="${order.pdfUrl}" class="download-btn" target="_blank" rel="noopener noreferrer">
                                    <i class="fas fa-download"></i> Download PDF
                                </a>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            `;
        }

        caseDetails.innerHTML = html;
    }

    showError(message) {
        const caseDetails = document.getElementById('caseDetails');
        caseDetails.innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i> ${message}
            </div>
        `;

        const resultsContainer = document.getElementById('resultsContainer');
        resultsContainer.style.display = 'block';
        this.hideLoading();
    }

    addToHistory(caseData, resultData, status) {
        const historyItem = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            caseRef: `${caseData.caseType} ${caseData.caseNumber}/${caseData.filingYear}`,
            caseData: caseData,
            resultData: resultData,
            status: status
        };

        this.searchHistory.unshift(historyItem);
        
        // Keep only last 10 searches
        if (this.searchHistory.length > 10) {
            this.searchHistory = this.searchHistory.slice(0, 10);
        }

        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
        this.loadSearchHistory();
    }

    loadSearchHistory() {
        const historyList = document.getElementById('historyList');
        
        if (this.searchHistory.length === 0) {
            historyList.innerHTML = '<p class="no-history">No searches yet. Start by entering case details above.</p>';
            return;
        }

        const historyHTML = this.searchHistory.map(item => `
            <div class="history-item" onclick="courtFetcher.loadHistoryItem('${item.id}')">
                <div class="case-ref">${item.caseRef}</div>
                <div class="timestamp">${new Date(item.timestamp).toLocaleString()}</div>
                <span class="status ${item.status}">${item.status.toUpperCase()}</span>
            </div>
        `).join('');

        historyList.innerHTML = historyHTML;
    }

    loadHistoryItem(itemId) {
        const item = this.searchHistory.find(h => h.id == itemId);
        if (!item) return;

        // Fill form with historical data
        document.getElementById('caseType').value = item.caseData.caseType;
        document.getElementById('caseNumber').value = item.caseData.caseNumber;
        document.getElementById('filingYear').value = item.caseData.filingYear;

        // Show results if available
        if (item.status === 'success' && item.resultData) {
            document.getElementById('resultsContainer').style.display = 'block';
            this.displayResults(item.resultData);
        }
    }

    clearForm() {
        document.getElementById('caseForm').reset();
        document.getElementById('resultsContainer').style.display = 'none';
        localStorage.removeItem('courtFormData');
    }

    saveFormData() {
        const form = document.getElementById('caseForm');
        const formData = new FormData(form);
        const data = {
            caseType: formData.get('caseType'),
            caseNumber: formData.get('caseNumber'),
            filingYear: formData.get('filingYear')
        };
        localStorage.setItem('courtFormData', JSON.stringify(data));
    }

    loadFormData() {
        const savedData = localStorage.getItem('courtFormData');
        if (!savedData) return;

        try {
            const data = JSON.parse(savedData);
            if (data.caseType) document.getElementById('caseType').value = data.caseType;
            if (data.caseNumber) document.getElementById('caseNumber').value = data.caseNumber;
            if (data.filingYear) document.getElementById('filingYear').value = data.filingYear;
        } catch (error) {
            console.error('Error loading saved form data:', error);
        }
    }

    // Utility function to format case reference
    formatCaseRef(caseType, caseNumber, filingYear) {
        return `${caseType} ${caseNumber}/${filingYear}`;
    }

    // Clear search history
    clearHistory() {
        this.searchHistory = [];
        localStorage.removeItem('searchHistory');
        this.loadSearchHistory();
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.courtFetcher = new CourtDataFetcher();
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}