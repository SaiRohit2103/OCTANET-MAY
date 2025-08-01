// Court Data Fetcher Frontend JavaScript
class CourtDataFetcher {
    constructor() {
        this.apiUrl = '/api';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSearchHistory();
    }

    bindEvents() {
        const form = document.getElementById('caseForm');
        form.addEventListener('submit', (e) => this.handleFormSubmit(e));
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const searchData = {
            caseType: formData.get('caseType'),
            caseNumber: formData.get('caseNumber'),
            filingYear: formData.get('filingYear'),
            courtType: formData.get('courtType')
        };

        // Validate form data
        if (!this.validateForm(searchData)) {
            return;
        }

        // Show loading state
        this.showLoading();
        this.hideError();
        this.hideResults();

        try {
            // Make API call
            const response = await this.fetchCaseData(searchData);
            
            if (response.success) {
                this.displayResults(response.data);
                this.saveToHistory(searchData, response.data);
            } else {
                this.showError(response.error || 'Failed to fetch case data');
            }
        } catch (error) {
            console.error('Error fetching case data:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.hideLoading();
        }
    }

    validateForm(data) {
        if (!data.caseType || !data.caseNumber || !data.filingYear || !data.courtType) {
            this.showError('Please fill in all required fields');
            return false;
        }

        // Validate case number format
        const caseNumberPattern = /^\d+\/\d{4}$/;
        if (!caseNumberPattern.test(data.caseNumber)) {
            this.showError('Please enter case number in format: 123/2023');
            return false;
        }

        // Validate year
        const currentYear = new Date().getFullYear();
        const year = parseInt(data.filingYear);
        if (year < 2000 || year > currentYear) {
            this.showError(`Please enter a valid year between 2000 and ${currentYear}`);
            return false;
        }

        return true;
    }

    async fetchCaseData(searchData) {
        // Make actual API call to backend
        const response = await fetch(`${this.apiUrl}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(searchData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    getMockDelhiHCData(searchData) {
        // Mock successful response for Delhi HC
        return {
            success: true,
            data: {
                caseInfo: {
                    caseNumber: `${searchData.caseType} ${searchData.caseNumber}`,
                    court: 'Delhi High Court',
                    filingDate: '15-03-2023',
                    status: 'Pending',
                    petitioner: 'John Doe',
                    respondent: 'State of Delhi',
                    lastHearing: '10-12-2023',
                    nextHearing: '15-01-2024',
                    judge: 'Hon\'ble Justice A.K. Sharma'
                },
                orders: [
                    {
                        date: '10-12-2023',
                        title: 'Order on Application for Interim Relief',
                        content: 'The court has considered the application for interim relief. After hearing both parties, the court is of the opinion that...',
                        downloadUrl: '#'
                    },
                    {
                        date: '25-11-2023',
                        title: 'Notice to Respondent',
                        content: 'Notice issued to the respondent to file reply within 4 weeks. Next date of hearing is fixed for...',
                        downloadUrl: '#'
                    },
                    {
                        date: '15-03-2023',
                        title: 'Case Filed',
                        content: 'Writ Petition filed. Registry to check compliance with rules. List for admission hearing on...',
                        downloadUrl: '#'
                    }
                ]
            }
        };
    }

    getMockDistrictCourtData(searchData) {
        // Mock response for District Courts
        return {
            success: false,
            error: 'District Courts portal integration is not yet implemented. Please use Delhi High Court option for demonstration.'
        };
    }

    displayResults(data) {
        this.showResults();
        this.renderCaseDetails(data.caseInfo);
        this.renderOrders(data.orders);
    }

    renderCaseDetails(caseInfo) {
        const caseDetails = document.getElementById('caseDetails');
        caseDetails.innerHTML = `
            <div class="case-detail-item">
                <span class="case-detail-label">Case Number:</span>
                <span class="case-detail-value">${caseInfo.caseNumber}</span>
            </div>
            <div class="case-detail-item">
                <span class="case-detail-label">Court:</span>
                <span class="case-detail-value">${caseInfo.court}</span>
            </div>
            <div class="case-detail-item">
                <span class="case-detail-label">Filing Date:</span>
                <span class="case-detail-value">${caseInfo.filingDate}</span>
            </div>
            <div class="case-detail-item">
                <span class="case-detail-label">Status:</span>
                <span class="case-detail-value">${caseInfo.status}</span>
            </div>
            <div class="case-detail-item">
                <span class="case-detail-label">Petitioner:</span>
                <span class="case-detail-value">${caseInfo.petitioner}</span>
            </div>
            <div class="case-detail-item">
                <span class="case-detail-label">Respondent:</span>
                <span class="case-detail-value">${caseInfo.respondent}</span>
            </div>
            <div class="case-detail-item">
                <span class="case-detail-label">Last Hearing:</span>
                <span class="case-detail-value">${caseInfo.lastHearing}</span>
            </div>
            <div class="case-detail-item">
                <span class="case-detail-label">Next Hearing:</span>
                <span class="case-detail-value">${caseInfo.nextHearing}</span>
            </div>
            <div class="case-detail-item">
                <span class="case-detail-label">Judge:</span>
                <span class="case-detail-value">${caseInfo.judge}</span>
            </div>
        `;
    }

    renderOrders(orders) {
        const ordersList = document.getElementById('ordersList');
        ordersList.innerHTML = orders.map(order => `
            <div class="order-item">
                <div class="order-date">${order.date}</div>
                <div class="order-title">${order.title}</div>
                <div class="order-content">${order.content}</div>
                <a href="${order.downloadUrl}" class="download-link" onclick="this.preventDefault(); alert('PDF download functionality would be implemented here');">
                    <i class="fas fa-download"></i> Download PDF
                </a>
            </div>
        `).join('');
    }

    saveToHistory(searchData, responseData) {
        let history = JSON.parse(localStorage.getItem('courtSearchHistory') || '[]');
        
        const historyItem = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            query: `${searchData.caseType} ${searchData.caseNumber}/${searchData.filingYear}`,
            court: searchData.courtType,
            caseNumber: responseData.caseInfo.caseNumber,
            status: responseData.caseInfo.status
        };

        history.unshift(historyItem);
        history = history.slice(0, 10); // Keep only last 10 searches

        localStorage.setItem('courtSearchHistory', JSON.stringify(history));
        this.renderSearchHistory(history);
    }

    loadSearchHistory() {
        const history = JSON.parse(localStorage.getItem('courtSearchHistory') || '[]');
        this.renderSearchHistory(history);
    }

    renderSearchHistory(history) {
        const historyList = document.getElementById('historyList');
        
        if (history.length === 0) {
            historyList.innerHTML = '<p style="text-align: center; color: #6c757d;">No recent searches</p>';
            return;
        }

        historyList.innerHTML = history.map(item => `
            <div class="history-item" onclick="courtFetcher.fillFormFromHistory('${item.query}', '${item.court}')">
                <div class="history-query">${item.query} (${item.court})</div>
                <div class="history-time">${this.formatDate(item.timestamp)} - Status: ${item.status}</div>
            </div>
        `).join('');
    }

    fillFormFromHistory(query, court) {
        const parts = query.split(' ');
        if (parts.length >= 2) {
            const caseType = parts[0];
            const caseNumberYear = parts[1];
            const [caseNum, year] = caseNumberYear.split('/');

            document.getElementById('caseType').value = caseType;
            document.getElementById('caseNumber').value = caseNumberYear;
            document.getElementById('filingYear').value = year;
            document.getElementById('courtType').value = court;
        }
    }

    formatDate(isoString) {
        const date = new Date(isoString);
        return date.toLocaleDateString('en-IN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showLoading() {
        document.getElementById('loading').style.display = 'block';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    showResults() {
        document.getElementById('resultsSection').style.display = 'block';
    }

    hideResults() {
        document.getElementById('resultsSection').style.display = 'none';
    }

    showError(message) {
        const errorElement = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        errorText.textContent = message;
        errorElement.style.display = 'block';
    }

    hideError() {
        document.getElementById('errorMessage').style.display = 'none';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.courtFetcher = new CourtDataFetcher();
});