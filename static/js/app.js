// Shark Tank Intelligence Platform - Frontend JavaScript

// Auto-detect API base URL based on current path
function getApiBaseUrl() {
    // Get the current path
    const path = window.location.pathname;
    
    // Remove trailing slash and get base path
    const basePath = path.replace(/\/$/, '');
    
    // If we're at /eatmeshark, use that as base, otherwise use root
    if (basePath.includes('/eatmeshark')) {
        return '/eatmeshark/api';
    }
    return '/api';
}

const API_BASE_URL = getApiBaseUrl();

let currentCountry = '';
let countryConfig = null;
let industries = [];

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    await loadCountries();
    setupEventListeners();
});

// Load available countries
async function loadCountries() {
    try {
        const response = await fetch(`${API_BASE_URL}/countries`);
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('country-select');
            select.innerHTML = '<option value="">Select Country...</option>';
            
            data.countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                select.appendChild(option);
            });
            
            select.addEventListener('change', handleCountryChange);
        }
    } catch (error) {
        console.error('Error loading countries:', error);
        showError('Failed to load countries. Make sure the API server is running.');
    }
}

// Handle country selection change
async function handleCountryChange(event) {
    const country = event.target.value;
    if (!country) return;
    
    currentCountry = country;
    
    try {
        const response = await fetch(`${API_BASE_URL}/countries/${country}/config`);
        const data = await response.json();
        
        if (data.success) {
            countryConfig = data;
            updateCurrencyLabels(data.currency);
            loadIndustries(country);
            populateSharks(data.sharks);
        }
    } catch (error) {
        console.error('Error loading country config:', error);
        showError('Failed to load country configuration.');
    }
}

// Load industries for selected country
async function loadIndustries(country) {
    // For now, we'll use a common set of industries
    // In production, this could come from the API
    industries = [
        'Technology', 'Food and Beverage', 'Fashion', 'Healthcare', 'Education',
        'Beauty', 'Fitness', 'Finance', 'Real Estate', 'Entertainment',
        'Agriculture', 'Manufacturing', 'Retail', 'Services', 'Other'
    ];
    
    const select = document.getElementById('industry');
    select.innerHTML = '<option value="">Select Industry...</option>';
    industries.forEach(industry => {
        const option = document.createElement('option');
        option.value = industry;
        option.textContent = industry;
        select.appendChild(option);
    });
}

// Update currency labels
function updateCurrencyLabels(currency) {
    document.getElementById('currency-unit-1').textContent = currency.unit;
    document.getElementById('currency-unit-2').textContent = currency.unit;
    document.getElementById('currency-unit-3').textContent = currency.unit;
}

// Populate sharks checkboxes
function populateSharks(sharks) {
    const container = document.getElementById('sharks-container');
    container.innerHTML = '';
    
    sharks.forEach(shark => {
        const div = document.createElement('div');
        div.className = 'shark-checkbox';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `shark-${shark.toLowerCase()}`;
        checkbox.name = 'sharks';
        checkbox.value = shark;
        
        const label = document.createElement('label');
        label.htmlFor = `shark-${shark.toLowerCase()}`;
        label.textContent = shark;
        
        div.appendChild(checkbox);
        div.appendChild(label);
        container.appendChild(div);
    });
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('predict-deal-btn').addEventListener('click', handlePredictDeal);
    document.getElementById('predict-valuation-btn').addEventListener('click', handlePredictValuation);
    document.getElementById('analyze-sharks-btn').addEventListener('click', handleAnalyzeSharks);
    document.getElementById('find-similar-btn').addEventListener('click', handleFindSimilar);
}

// Get form data
function getFormData() {
    const form = document.getElementById('pitch-form');
    const formData = new FormData(form);
    
    const sharks = Array.from(document.querySelectorAll('input[name="sharks"]:checked'))
        .map(cb => cb.value);
    
    const inputData = {
        industry: document.getElementById('industry').value,
        ask_amount: parseFloat(document.getElementById('ask-amount').value) || 0,
        ask_equity: parseFloat(document.getElementById('ask-equity').value) || 0,
        valuation_requested: parseFloat(document.getElementById('valuation-requested').value) || 0,
        monthly_sales: parseFloat(document.getElementById('monthly-sales').value) || 0,
        business_description: document.getElementById('business-description').value || ''
    };
    
    // Add shark present flags
    if (countryConfig && countryConfig.sharks) {
        countryConfig.sharks.forEach(shark => {
            const sharkLower = shark.toLowerCase();
            inputData[`${sharkLower}_present`] = sharks.includes(shark) ? 1 : 0;
        });
    }
    
    return inputData;
}

// Handle deal prediction
async function handlePredictDeal() {
    if (!currentCountry) {
        showError('Please select a country first.');
        return;
    }
    
    const inputData = getFormData();
    showLoading('Predicting deal probability...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/deal`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                country: currentCountry,
                input_data: inputData
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayDealResult(data);
        } else {
            showError(data.error || 'Failed to predict deal.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to API. Make sure the server is running.');
    }
}

// Handle valuation prediction
async function handlePredictValuation() {
    if (!currentCountry) {
        showError('Please select a country first.');
        return;
    }
    
    const inputData = getFormData();
    showLoading('Estimating valuation...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/valuation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                country: currentCountry,
                input_data: inputData
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayValuationResult(data);
        } else {
            showError(data.error || 'Failed to estimate valuation.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to API. Make sure the server is running.');
    }
}

// Handle shark analysis
async function handleAnalyzeSharks() {
    if (!currentCountry) {
        showError('Please select a country first.');
        return;
    }
    
    const inputData = getFormData();
    showLoading('Analyzing shark preferences...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/sharks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                country: currentCountry,
                input_data: inputData
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySharksResult(data);
        } else {
            showError(data.error || 'Failed to analyze sharks.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to API. Make sure the server is running.');
    }
}

// Handle similar companies
async function handleFindSimilar() {
    if (!currentCountry) {
        showError('Please select a country first.');
        return;
    }
    
    const businessDescription = document.getElementById('business-description').value;
    if (!businessDescription || !businessDescription.trim()) {
        showError('Please enter a business description to find similar companies.');
        return;
    }
    
    showLoading('Finding similar companies...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/similar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                country: currentCountry,
                business_description: businessDescription
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySimilarCompaniesResult(data);
        } else {
            showError(data.error || 'Failed to find similar companies.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to API. Make sure the server is running.');
    }
}

// Display deal result
function displayDealResult(data) {
    const resultsContent = document.getElementById('results-content');
    const currency = countryConfig?.currency || { symbol: '$', unit: 'USD' };
    
    const isDeal = data.prediction === 1;
    const badgeClass = isDeal ? 'badge-success' : 'badge-error';
    const badgeText = isDeal ? '✅ DEAL' : '❌ NO DEAL';
    
    resultsContent.innerHTML = `
        <div class="result-card">
            <h3>🎯 Deal Prediction</h3>
            <div class="result-metric">
                <span class="result-metric-label">Deal Probability</span>
                <span class="result-metric-value">${(data.probability * 100).toFixed(2)}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${data.probability * 100}%"></div>
            </div>
            <div style="margin-top: 1rem;">
                <span class="result-badge ${badgeClass}">${badgeText}</span>
            </div>
            <p style="margin-top: 1rem; color: var(--text-secondary);">
                💡 Based on Shark Tank ${currentCountry} data
            </p>
        </div>
    `;
    
    document.getElementById('results-section').style.display = 'block';
    resultsContent.scrollIntoView({ behavior: 'smooth' });
}

// Display valuation result
function displayValuationResult(data) {
    const resultsContent = document.getElementById('results-content');
    const currency = countryConfig?.currency || { symbol: '$', unit: 'USD' };
    
    resultsContent.innerHTML = `
        <div class="result-card">
            <h3>💰 Valuation Estimation</h3>
            <div class="result-metric">
                <span class="result-metric-label">Estimated Valuation</span>
                <span class="result-metric-value">${currency.symbol}${data.valuation.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} ${currency.unit}</span>
            </div>
            <div style="margin-top: 1rem;">
                <div class="result-metric">
                    <span class="result-metric-label">Lower Bound</span>
                    <span>${currency.symbol}${data.confidence_range.lower.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} ${currency.unit}</span>
                </div>
                <div class="result-metric">
                    <span class="result-metric-label">Upper Bound</span>
                    <span>${currency.symbol}${data.confidence_range.upper.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} ${currency.unit}</span>
                </div>
            </div>
            <p style="margin-top: 1rem; color: var(--text-secondary);">
                💡 Based on Shark Tank ${currentCountry} data
            </p>
        </div>
    `;
    
    document.getElementById('results-section').style.display = 'block';
    resultsContent.scrollIntoView({ behavior: 'smooth' });
}

// Display sharks result
function displaySharksResult(data) {
    const resultsContent = document.getElementById('results-content');
    
    if (data.no_deal) {
        resultsContent.innerHTML = `
            <div class="result-card">
                <h3>🦈 Shark Analysis</h3>
                <div class="warning-message">
                    <strong>⚠️ No Deal Predicted</strong>
                    <p style="margin-top: 0.5rem;">
                        Since the deal prediction indicates <strong>NO DEAL</strong>${data.deal_probability ? ` (probability: ${(data.deal_probability * 100).toFixed(1)}%)` : ''}, 
                        no sharks would invest in this pitch.
                    </p>
                    <p style="margin-top: 0.5rem;">
                        To see which sharks might invest, improve your pitch parameters (ask amount, equity, valuation, monthly sales) to increase the likelihood of getting a deal.
                    </p>
                </div>
                <p style="margin-top: 1rem; color: var(--text-secondary);">
                    💡 Based on Shark Tank ${currentCountry} data
                </p>
            </div>
        `;
    } else {
        let sharksHTML = '<div class="shark-list">';
        data.ranked.forEach(([shark, prob]) => {
            sharksHTML += `
                <div class="shark-item">
                    <div class="shark-name">${shark}</div>
                    <div class="shark-probability">${(prob * 100).toFixed(1)}%</div>
                    <div class="progress-bar" style="margin-top: 0.5rem;">
                        <div class="progress-fill" style="width: ${prob * 100}%"></div>
                    </div>
                </div>
            `;
        });
        sharksHTML += '</div>';
        
        let insightsHTML = '';
        if (data.insights && data.insights.length > 0) {
            insightsHTML = '<div style="margin-top: 1.5rem;"><h4 style="margin-bottom: 1rem;">🔍 Insights</h4>';
            data.insights.forEach(insight => {
                insightsHTML += `<div class="insight-item">${insight}</div>`;
            });
            insightsHTML += '</div>';
        }
        
        resultsContent.innerHTML = `
            <div class="result-card">
                <h3>🦈 Shark Investment Probabilities</h3>
                ${sharksHTML}
                ${insightsHTML}
                <p style="margin-top: 1rem; color: var(--text-secondary);">
                    💡 Based on Shark Tank ${currentCountry} data
                </p>
            </div>
        `;
    }
    
    document.getElementById('results-section').style.display = 'block';
    resultsContent.scrollIntoView({ behavior: 'smooth' });
}

// Display similar companies result
function displaySimilarCompaniesResult(data) {
    const resultsContent = document.getElementById('results-content');
    const currency = countryConfig?.currency || { symbol: '$', unit: 'USD' };
    
    if (!data.companies || data.companies.length === 0) {
        resultsContent.innerHTML = `
            <div class="result-card">
                <h3>🔍 Similar Companies</h3>
                <div class="info-message">
                    No similar companies found. Try providing a more detailed business description.
                </div>
            </div>
        `;
    } else {
        let companiesHTML = '';
        data.companies.forEach(company => {
            companiesHTML += `
                <div class="similar-company">
                    <div class="similar-company-header">
                        <span class="similar-company-name">${company.company_name || 'Unknown Company'}</span>
                        <span class="similarity-score">${(company.similarity_score * 100).toFixed(1)}% similar</span>
                    </div>
                    ${company.industry ? `<p style="color: var(--text-secondary); margin: 0.5rem 0;"><strong>Industry:</strong> ${company.industry}</p>` : ''}
                    ${company.ask_amount ? `<p style="color: var(--text-secondary); margin: 0.5rem 0;"><strong>Ask Amount:</strong> ${currency.symbol}${company.ask_amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} ${currency.unit}</p>` : ''}
                    ${company.description ? `<p style="color: var(--text-secondary); margin-top: 0.5rem;">${company.description}</p>` : ''}
                </div>
            `;
        });
        
        resultsContent.innerHTML = `
            <div class="result-card">
                <h3>🔍 Similar Companies</h3>
                ${companiesHTML}
                <p style="margin-top: 1rem; color: var(--text-secondary);">
                    💡 Based on Shark Tank ${currentCountry} data
                </p>
            </div>
        `;
    }
    
    document.getElementById('results-section').style.display = 'block';
    resultsContent.scrollIntoView({ behavior: 'smooth' });
}

// Show loading state
function showLoading(message) {
    const resultsContent = document.getElementById('results-content');
    resultsContent.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    document.getElementById('results-section').style.display = 'block';
    resultsContent.scrollIntoView({ behavior: 'smooth' });
}

// Show error message
function showError(message) {
    const resultsContent = document.getElementById('results-content');
    resultsContent.innerHTML = `
        <div class="error-message">
            <strong>Error:</strong> ${message}
        </div>
    `;
    document.getElementById('results-section').style.display = 'block';
    resultsContent.scrollIntoView({ behavior: 'smooth' });
}

