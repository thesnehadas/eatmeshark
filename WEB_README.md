# Shark Tank Intelligence Platform - Web Application

A modern, minimalist dark-mode web application for predicting Shark Tank deal outcomes, estimating valuations, analyzing shark preferences, and finding similar companies.

## Features

- 🎯 **Deal Predictor**: Predict the probability of getting a deal
- 💰 **Valuation Estimator**: Estimate startup valuation based on pitch parameters
- 🦈 **Shark Analyzer**: Analyze which sharks are most likely to invest
- 🔍 **Similar Companies**: Find similar companies that appeared on Shark Tank

## Technology Stack

- **Backend**: Flask (Python) REST API
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **ML Models**: scikit-learn, joblib
- **Design**: Modern minimalist dark mode UI

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Train Models** (if not already trained):
   ```bash
   python train_all_countries.py
   ```

## Running the Application

### Option 1: Using the startup script (Recommended)
```bash
python run_web.py
```

### Option 2: Direct Flask run
```bash
python api.py
```

The web application will be available at: **http://localhost:5000**

## API Endpoints

The Flask API provides the following endpoints:

- `GET /api/health` - Health check
- `GET /api/countries` - List available countries
- `GET /api/countries/<country>/config` - Get country configuration
- `POST /api/predict/deal` - Predict deal probability
- `POST /api/predict/valuation` - Predict valuation
- `POST /api/predict/sharks` - Analyze shark preferences
- `POST /api/predict/similar` - Find similar companies
- `POST /api/predict/all` - Get all predictions at once

## Project Structure

```
shark-tank-deal-predictor/
├── api.py                 # Flask backend API
├── run_web.py            # Startup script
├── templates/
│   └── index.html        # Main frontend page
├── static/
│   ├── css/
│   │   └── style.css    # Dark mode styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── src/                  # ML models and inference
├── models/               # Trained models
└── data/                 # Datasets
```

## Usage

1. **Select Country**: Choose from India, US, or Australia
2. **Fill Pitch Information**:
   - Industry
   - Ask Amount
   - Ask Equity (%)
   - Valuation Requested
   - Monthly Sales
   - Business Description (optional)
   - Select which sharks are present
3. **Run Predictions**: Click any of the prediction buttons
4. **View Results**: Results will appear below the form

## Features

### Dark Mode Design
- Modern minimalist interface
- Smooth animations and transitions
- Responsive design for mobile and desktop
- Gradient accents and clean typography

### Smart Logic
- Shark analyzer automatically checks deal prediction first
- If no deal is predicted, shows appropriate message instead of shark probabilities
- Currency symbols and units adapt based on selected country

## Development

### Running in Development Mode
The Flask server runs in debug mode by default. To disable:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

### Customizing Styles
Edit `static/css/style.css` to customize the appearance. The design uses CSS variables for easy theming.

### Adding New Features
1. Add API endpoint in `api.py`
2. Add frontend function in `static/js/app.js`
3. Update UI in `templates/index.html` if needed

## Troubleshooting

### API Connection Errors
- Make sure the Flask server is running
- Check that port 5000 is not in use
- Verify CORS is enabled (already configured)

### Model Not Found Errors
- Ensure models are trained: `python train_all_countries.py`
- Check that model files exist in `models/<country>/`

### Frontend Not Loading
- Check browser console for errors
- Verify static files are in correct directories
- Clear browser cache

## Notes

- The Streamlit app (`app.py`) is still available but separate from this web application
- This web app uses the same ML models and inference logic as the Streamlit version
- All predictions are based on historical Shark Tank data for the selected country

## License

This project is part of the Global Shark Tank Intelligence Platform.

