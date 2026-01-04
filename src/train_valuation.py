"""
Train valuation estimation models for a specific country.
"""

import sys
import os
import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.config import load_config
from src.data_adapters import get_adapter
from src.canonical_preprocess import preprocess_canonical, create_canonical_targets


def train_valuation_model(country, random_state=42):
    """
    Train valuation estimation model for a specific country.
    
    Parameters:
    -----------
    country : str
        Country name
    random_state : int
        Random seed
    
    Returns:
    --------
    model : object
        Best trained model
    encoder_dict : dict
        Encoder dictionary
    scaler : StandardScaler
        Fitted scaler
    feature_names : list
        Feature names
    results : dict
        Evaluation results
    """
    print("=" * 60)
    print(f"Training Valuation Estimation Model for {country}")
    print("=" * 60)
    
    # Load country configuration
    config = load_config(country)
    adapter = get_adapter(country)
    adapter.set_config(config)  # Use set_config method
    
    # Load data
    print(f"\n1. Loading data from {config['dataset_path']}...")
    df_raw = adapter.load_data(config['dataset_path'])
    
    # Convert to canonical schema
    print("\n2. Converting to canonical schema...")
    df = adapter.to_canonical(df_raw)
    
    # Create valuation target (only for deals)
    df = create_canonical_targets(df)
    df = df[df['deal'] == 1].copy()  # Only deals
    df = df[df['valuation'].notna() & (df['valuation'] > 0)].copy()
    
    if len(df) == 0:
        raise ValueError(f"No valid valuation data found for {country}")
    
    print(f"   Dataset size: {len(df)} deals with valid valuations")
    print(f"   Valuation range: {df['valuation'].min():.2f} - {df['valuation'].max():.2f}")
    
    # Log transform target
    y_log = np.log1p(df['valuation'])
    y = df['valuation']
    
    # CRITICAL FIX: Remove outcome variables before preprocessing
    # Outcome variables (deal_amount, deal_equity, deal_valuation) should NOT be features
    # Only 'valuation' is the target, but we need to exclude deal_amount and deal_equity
    outcome_vars = ['deal', 'deal_amount', 'deal_equity', 'deal_valuation']
    df_for_features = df.drop(columns=[col for col in outcome_vars if col in df.columns], errors='ignore')
    
    # Preprocess (without target and outcome variables)
    X, _, encoder_dict, scaler = preprocess_canonical(df_for_features, fit=True)
    
    # Train-test split
    X_train, X_test, y_train, y_test, y_train_log, y_test_log = train_test_split(
        X, y, y_log, test_size=0.2, random_state=random_state
    )
    
    # Train models
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=random_state, n_jobs=-1),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=random_state)
    }
    
    results = {}
    print("\n3. Training models (using log-transformed target)...")
    print("=" * 60)
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train_log)
        
        y_pred_log = model.predict(X_test)
        y_pred = np.expm1(y_pred_log)
        
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {
            'model': model,
            'rmse': rmse,
            'mae': mae,
            'r2': r2
        }
        
        print(f"  RMSE: {rmse:.2f}")
        print(f"  MAE: {mae:.2f}")
        print(f"  R²: {r2:.4f}")
    
    # Select best model
    best_model_name = min(results.keys(), key=lambda k: results[k]['rmse'])
    best_model = results[best_model_name]['model']
    
    print("\n" + "=" * 60)
    print(f"Best Model: {best_model_name}")
    print(f"RMSE: {results[best_model_name]['rmse']:.2f}")
    print("=" * 60)
    
    return best_model, encoder_dict, scaler, X.columns.tolist(), results


def save_valuation_model(country, model, encoder_dict, scaler, feature_names):
    """
    Save valuation model for a country.
    """
    config = load_config(country)
    model_path = config['model_paths']['valuation']
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    model_artifact = {
        'model': model,
        'encoder_dict': encoder_dict,
        'scaler': scaler,
        'feature_names': feature_names,
        'country': country
    }
    
    joblib.dump(model_artifact, model_path)
    print(f"\nModel saved to {model_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train valuation estimation model')
    parser.add_argument('--country', type=str, required=True, choices=['India', 'US', 'Australia'],
                       help='Country to train model for')
    parser.add_argument('--random-state', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    # Train model
    model, encoder_dict, scaler, feature_names, results = train_valuation_model(
        args.country, random_state=args.random_state
    )
    
    # Save model
    save_valuation_model(args.country, model, encoder_dict, scaler, feature_names)
    
    print(f"\n✅ Valuation model training complete for {args.country}!")

