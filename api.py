"""
Flask API backend for Shark Tank Intelligence Platform.
"""

from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.inference import predict_all, predict_deal, predict_valuation, predict_sharks
from src.config import get_available_countries, load_config
from src.similarity_finder import find_similar_companies

# Get base path from environment variable or use default
BASE_PATH = os.environ.get('BASE_PATH', '/eatmeshark')

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS for frontend

# Create a blueprint for the base path
from flask import Blueprint
main_bp = Blueprint('main', __name__, url_prefix=BASE_PATH)

@main_bp.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@main_bp.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory(app.static_folder, path)

@main_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'Shark Tank Intelligence API is running'})


@main_bp.route('/api/countries', methods=['GET'])
def get_countries():
    """Get list of available countries."""
    try:
        countries = get_available_countries()
        return jsonify({
            'success': True,
            'countries': countries
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@main_bp.route('/api/countries/<country>/config', methods=['GET'])
def get_country_config(country):
    """Get configuration for a specific country."""
    try:
        config = load_config(country)
        # Return only necessary config (sharks, currency info)
        sharks = [shark['name'] for shark in config.get('sharks', [])]
        
        # Determine currency based on country
        currency_map = {
            'India': {'symbol': '₹', 'unit': 'Lakhs'},
            'US': {'symbol': '$', 'unit': 'USD'},
            'Australia': {'symbol': '$', 'unit': 'AUD'}
        }
        currency = currency_map.get(country, {'symbol': '$', 'unit': 'USD'})
        
        return jsonify({
            'success': True,
            'country': country,
            'sharks': sharks,
            'currency': currency
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@main_bp.route('/api/predict/deal', methods=['POST'])
def predict_deal_endpoint():
    """Predict deal probability."""
    try:
        data = request.json
        country = data.get('country')
        input_data = data.get('input_data', {})
        
        if not country:
            return jsonify({
                'success': False,
                'error': 'Country is required'
            }), 400
        
        probability, prediction = predict_deal(country, input_data)
        
        return jsonify({
            'success': True,
            'probability': float(probability),
            'prediction': int(prediction),
            'prediction_label': 'DEAL' if prediction == 1 else 'NO DEAL'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@main_bp.route('/api/predict/valuation', methods=['POST'])
def predict_valuation_endpoint():
    """Predict startup valuation."""
    try:
        data = request.json
        country = data.get('country')
        input_data = data.get('input_data', {})
        
        if not country:
            return jsonify({
                'success': False,
                'error': 'Country is required'
            }), 400
        
        valuation, confidence_range = predict_valuation(country, input_data)
        
        return jsonify({
            'success': True,
            'valuation': float(valuation),
            'confidence_range': {
                'lower': float(confidence_range[0]),
                'upper': float(confidence_range[1])
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@main_bp.route('/api/predict/sharks', methods=['POST'])
def predict_sharks_endpoint():
    """Predict shark investment probabilities."""
    try:
        data = request.json
        country = data.get('country')
        input_data = data.get('input_data', {})
        
        if not country:
            return jsonify({
                'success': False,
                'error': 'Country is required'
            }), 400
        
        # Check deal prediction first
        deal_prob, deal_pred = predict_deal(country, input_data)
        
        if deal_pred == 0 or deal_prob < 0.3:
            return jsonify({
                'success': True,
                'no_deal': True,
                'deal_probability': float(deal_prob),
                'message': 'No deal predicted - no sharks would invest'
            })
        
        shark_probs, ranked_sharks, insights = predict_sharks(country, input_data)
        
        return jsonify({
            'success': True,
            'no_deal': False,
            'probabilities': {k: float(v) for k, v in shark_probs.items()},
            'ranked': [(shark, float(prob)) for shark, prob in ranked_sharks],
            'insights': insights
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@main_bp.route('/api/predict/similar', methods=['POST'])
def find_similar_companies_endpoint():
    """Find similar companies."""
    try:
        data = request.json
        country = data.get('country')
        business_description = data.get('business_description', '')
        
        if not country:
            return jsonify({
                'success': False,
                'error': 'Country is required'
            }), 400
        
        if not business_description or not business_description.strip():
            return jsonify({
                'success': False,
                'error': 'Business description is required'
            }), 400
        
        similar_companies = find_similar_companies(country, business_description, top_n=5)
        
        return jsonify({
            'success': True,
            'companies': similar_companies
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@main_bp.route('/api/predict/all', methods=['POST'])
def predict_all_endpoint():
    """Get all predictions at once."""
    try:
        data = request.json
        country = data.get('country')
        input_data = data.get('input_data', {})
        
        if not country:
            return jsonify({
                'success': False,
                'error': 'Country is required'
            }), 400
        
        predictions = predict_all(country, input_data)
        
        # Convert to JSON-serializable format
        result = {
            'success': True,
            'deal': {},
            'valuation': {},
            'sharks': {},
            'similar_companies': {}
        }
        
        # Deal prediction
        if predictions.get('deal', {}).get('available'):
            result['deal'] = {
                'available': True,
                'probability': float(predictions['deal']['probability']),
                'prediction': int(predictions['deal']['prediction']),
                'prediction_label': 'DEAL' if predictions['deal']['prediction'] == 1 else 'NO DEAL'
            }
        else:
            result['deal'] = {'available': False}
        
        # Valuation
        if predictions.get('valuation', {}).get('available'):
            result['valuation'] = {
                'available': True,
                'valuation': float(predictions['valuation']['valuation']),
                'confidence_range': {
                    'lower': float(predictions['valuation']['confidence_range'][0]),
                    'upper': float(predictions['valuation']['confidence_range'][1])
                }
            }
        else:
            result['valuation'] = {'available': False}
        
        # Sharks
        if predictions.get('sharks', {}).get('available'):
            deal_pred = predictions.get('deal', {}).get('prediction', 1)
            deal_prob = predictions.get('deal', {}).get('probability', 1.0)
            
            if deal_pred == 0 or deal_prob < 0.3:
                result['sharks'] = {
                    'available': True,
                    'no_deal': True,
                    'message': 'No deal predicted - no sharks would invest'
                }
            else:
                result['sharks'] = {
                    'available': True,
                    'no_deal': False,
                    'probabilities': {k: float(v) for k, v in predictions['sharks']['probabilities'].items()},
                    'ranked': [(shark, float(prob)) for shark, prob in predictions['sharks']['ranked']],
                    'insights': predictions['sharks']['insights']
                }
        else:
            result['sharks'] = {'available': False}
        
        # Similar companies
        if predictions.get('similar_companies', {}).get('available'):
            result['similar_companies'] = {
                'available': True,
                'companies': predictions['similar_companies']['companies']
            }
        else:
            result['similar_companies'] = {'available': False}
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Register blueprint AFTER all routes are defined
app.register_blueprint(main_bp)


if __name__ == '__main__':
    print("=" * 60)
    print("Shark Tank Intelligence Platform - API Server")
    print("=" * 60)
    print("\nStarting Flask server...")
    print("API will be available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/countries - List available countries")
    print("  POST /api/predict/deal - Predict deal probability")
    print("  POST /api/predict/valuation - Predict valuation")
    print("  POST /api/predict/sharks - Predict shark investments")
    print("  POST /api/predict/similar - Find similar companies")
    print("  POST /api/predict/all - Get all predictions")
    print("\n" + "=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

