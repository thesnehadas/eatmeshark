"""
Unified inference interface for country-aware predictions.
"""

import pandas as pd
import numpy as np
import joblib
import os
from src.config import load_config
from src.data_adapters import get_adapter
from src.canonical_preprocess import preprocess_canonical
from src.similarity_finder import find_similar_companies


def load_model(country, model_type='deal'):
    """
    Load a trained model for a specific country.
    
    Parameters:
    -----------
    country : str
        Country name
    model_type : str
        Type of model ('deal', 'valuation', 'sharks')
    
    Returns:
    --------
    model_artifact : dict
        Model artifact dictionary
    """
    config = load_config(country)
    model_path = config['model_paths'][model_type]
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}. Please train the model first.")
    
    return joblib.load(model_path)


def predict_deal(country, input_data):
    """
    Predict deal probability for a country.
    
    Parameters:
    -----------
    country : str
        Country name
    input_data : dict
        Input data in canonical schema
    
    Returns:
    --------
    probability : float
        Deal probability
    prediction : int
        Binary prediction
    """
    # Load model
    model_artifact = load_model(country, 'deal')
    model = model_artifact['model']
    encoder_dict = model_artifact['encoder_dict']
    scaler = model_artifact['scaler']
    feature_names = model_artifact['feature_names']
    
    # Convert to DataFrame
    df = pd.DataFrame([input_data])
    
    # Preprocess
    X, _, _ = preprocess_canonical(df, fit=False, encoder_dict=encoder_dict, 
                                   scaler=scaler, feature_names=feature_names)
    X = X[feature_names]
    
    # Predict probability
    probability = model.predict_proba(X)[0, 1]
    
    # Use a higher threshold (0.65) for more conservative predictions
    # This prevents the model from always predicting DEAL
    # Only predict DEAL if probability is >= 65%
    # This ensures only strong pitches get DEAL predictions
    prediction_threshold = 0.65
    prediction = 1 if probability >= prediction_threshold else 0
    
    return probability, prediction


def predict_valuation(country, input_data):
    """
    Predict valuation for a country.
    
    Parameters:
    -----------
    country : str
        Country name
    input_data : dict
        Input data in canonical schema
    
    Returns:
    --------
    valuation : float
        Predicted valuation
    confidence_range : tuple
        (lower, upper) confidence bounds
    """
    # Load model
    model_artifact = load_model(country, 'valuation')
    model = model_artifact['model']
    encoder_dict = model_artifact['encoder_dict']
    scaler = model_artifact['scaler']
    feature_names = model_artifact['feature_names']
    
    # Convert to DataFrame
    df = pd.DataFrame([input_data])
    
    # Preprocess
    X, _, _ = preprocess_canonical(df, fit=False, encoder_dict=encoder_dict,
                                   scaler=scaler, feature_names=feature_names)
    X = X[feature_names]
    
    # Predict (in log space)
    y_pred_log = model.predict(X)[0]
    valuation = np.expm1(y_pred_log)
    
    # Confidence range
    confidence_range = (valuation * 0.7, valuation * 1.3)
    
    return valuation, confidence_range


def predict_sharks(country, input_data):
    """
    Predict shark investment probabilities for a country.
    
    Parameters:
    -----------
    country : str
        Country name
    input_data : dict
        Input data in canonical schema
    
    Returns:
    --------
    shark_probs : dict
        Dictionary of shark probabilities
    ranked_sharks : list
        List of (shark, probability) tuples, sorted
    insights : list
        List of insight strings
    """
    # Load model
    model_artifact = load_model(country, 'sharks')
    shark_models = model_artifact['shark_models']
    encoder_dict = model_artifact['encoder_dict']
    scaler = model_artifact['scaler']
    feature_names = model_artifact['feature_names']
    insights_data = model_artifact.get('insights', {})
    
    # Convert to DataFrame
    df = pd.DataFrame([input_data])
    
    # Preprocess
    X, _, _ = preprocess_canonical(df, fit=False, encoder_dict=encoder_dict,
                                   scaler=scaler, feature_names=feature_names)
    X = X[feature_names]
    
    # Predict for each shark
    shark_probs = {}
    for shark, model in shark_models.items():
        try:
            prob = model.predict_proba(X)[0, 1]
            shark_probs[shark] = prob
        except:
            shark_probs[shark] = 0.0
    
    # Rank sharks
    ranked_sharks = sorted(shark_probs.items(), key=lambda x: x[1], reverse=True)
    
    # Generate insights
    insights = []
    for shark, insight_data in insights_data.items():
        if shark in shark_models:
            top_features = insight_data.get('top_features', pd.DataFrame())
            investment_rate = insight_data.get('investment_rate', 0)
            
            insight_parts = []
            
            # Check if top_features is a DataFrame and not empty
            if isinstance(top_features, pd.DataFrame) and not top_features.empty:
                # Get feature column name
                if 'feature' in top_features.columns:
                    feature_col = 'feature'
                else:
                    feature_col = top_features.columns[0] if len(top_features.columns) > 0 else None
                
                if feature_col:
                    # Filter out outcome variables (deal_amount, deal_equity, deal_valuation, etc.)
                    outcome_vars = ['deal_amount', 'deal_equity', 'deal_valuation', 'valuation', 'deal']
                    valid_features = top_features[~top_features[feature_col].isin(outcome_vars)]
                    
                    if not valid_features.empty:
                        # Find industry features first
                        industry_features = valid_features[valid_features[feature_col].astype(str).str.startswith('industry_')]
                        if not industry_features.empty:
                            top_industry = industry_features.iloc[0][feature_col].replace('industry_', '').replace('_', ' ')
                            insight_parts.append(f"prefers {top_industry} industry")
                        
                        # If no industry preference, check other important features
                        if not insight_parts:
                            non_industry = valid_features[~valid_features[feature_col].astype(str).str.startswith('industry_')]
                            if not non_industry.empty:
                                top_feat = non_industry.iloc[0][feature_col]
                                # Make feature names more readable
                                readable_feat = top_feat.replace('_', ' ').title()
                                if 'importance' in top_features.columns:
                                    importance = non_industry.iloc[0].get('importance', 0)
                                    if importance > 0.05:  # Only mention if significant
                                        insight_parts.append(f"key factor: {readable_feat}")
            
            # Build insight string
            base_text = f"**{shark}**: Investment rate {investment_rate*100:.1f}%"
            if insight_parts:
                insights.append(f"{base_text}. {', '.join(insight_parts)}.")
            else:
                insights.append(f"{base_text}. General investor profile.")
    
    return shark_probs, ranked_sharks, insights


def predict_all(country, input_data):
    """
    Run all predictions for a country.
    
    Parameters:
    -----------
    country : str
        Country name
    input_data : dict
        Input data in canonical schema
    
    Returns:
    --------
    predictions : dict
        Dictionary containing all predictions
    """
    predictions = {}
    
    # Deal prediction
    try:
        probability, prediction = predict_deal(country, input_data)
        predictions['deal'] = {
            'probability': probability,
            'prediction': prediction,
            'available': True
        }
    except FileNotFoundError:
        predictions['deal'] = {'available': False}
    except Exception as e:
        predictions['deal'] = {'available': False, 'error': str(e)}
    
    # Valuation prediction
    try:
        valuation, confidence_range = predict_valuation(country, input_data)
        predictions['valuation'] = {
            'valuation': valuation,
            'confidence_range': confidence_range,
            'available': True
        }
    except FileNotFoundError:
        predictions['valuation'] = {'available': False}
    except Exception as e:
        predictions['valuation'] = {'available': False, 'error': str(e)}
    
    # Shark predictions
    try:
        shark_probs, ranked_sharks, insights = predict_sharks(country, input_data)
        predictions['sharks'] = {
            'probabilities': shark_probs,
            'ranked': ranked_sharks,
            'insights': insights,
            'available': True
        }
    except FileNotFoundError:
        predictions['sharks'] = {'available': False}
    except Exception as e:
        predictions['sharks'] = {'available': False, 'error': str(e)}
    
    # Similar companies
    try:
        business_desc = input_data.get('business_description', '')
        if business_desc and business_desc.strip():
            similar_companies = find_similar_companies(country, business_desc, top_n=5)
            predictions['similar_companies'] = {
                'companies': similar_companies,
                'available': True
            }
        else:
            predictions['similar_companies'] = {'available': False, 'message': 'No description provided'}
    except FileNotFoundError:
        predictions['similar_companies'] = {'available': False}
    except Exception as e:
        predictions['similar_companies'] = {'available': False, 'error': str(e)}
    
    return predictions
