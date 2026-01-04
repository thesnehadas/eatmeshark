"""
Train shark preference models for a specific country.
"""

import sys
import os
import argparse
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, roc_auc_score
import joblib

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.config import load_config
from src.data_adapters import get_adapter
from src.canonical_preprocess import preprocess_canonical, create_canonical_targets


def train_shark_models(country, random_state=42):
    """
    Train shark preference models for a specific country.
    
    Parameters:
    -----------
    country : str
        Country name
    random_state : int
        Random seed
    
    Returns:
    --------
    shark_models : dict
        Dictionary of shark models
    encoder_dict : dict
        Encoder dictionary
    scaler : StandardScaler
        Fitted scaler
    feature_names : list
        Feature names
    results : dict
        Evaluation results
    insights : dict
        Shark insights
    """
    print("=" * 60)
    print(f"Training Shark Preference Models for {country}")
    print("=" * 60)
    
    # Load country configuration
    config = load_config(country)
    adapter = get_adapter(country)
    adapter.set_config(config)  # Use set_config method
    
    # Get shark names
    shark_names = [shark['name'] for shark in config['sharks']]
    print(f"\nSharks for {country}: {', '.join(shark_names)}")
    
    # Load data
    print(f"\n1. Loading data from {config['dataset_path']}...")
    df_raw = adapter.load_data(config['dataset_path'])
    
    # Convert to canonical schema
    print("\n2. Converting to canonical schema...")
    df = adapter.to_canonical(df_raw)
    
    # Create shark targets
    for shark in shark_names:
        shark_lower = shark.lower()
        inv_amount_col = f'{shark_lower}_investment_amount'
        if inv_amount_col in df.columns:
            df[f'{shark_lower}_invested'] = (df[inv_amount_col] > 0).astype(int)
        else:
            df[f'{shark_lower}_invested'] = 0
    
    # Preprocess (exclude outcome variables for shark prediction)
    print("\n3. Preprocessing data...")
    # Temporarily remove outcome variables before preprocessing
    outcome_vars = ['deal_amount', 'deal_equity', 'deal_valuation', 'valuation', 'deal']
    df_for_preprocessing = df.drop(columns=[col for col in outcome_vars if col in df.columns], errors='ignore')
    
    X, _, encoder_dict, scaler = preprocess_canonical(df_for_preprocessing, fit=True)
    
    # Reset indices for alignment
    df = df.reset_index(drop=True)
    X = X.reset_index(drop=True)
    
    # Train models for each shark
    shark_models = {}
    results = {}
    insights = {}
    
    print("\n4. Training individual shark models...")
    print("=" * 60)
    
    for shark in shark_names:
        shark_lower = shark.lower()
        target_col = f'{shark_lower}_invested'
        present_col = f'{shark_lower}_present'
        
        if target_col in df.columns and present_col in df.columns:
            # Only train on episodes where shark was present
            mask = df[present_col] == 1
            if mask.sum() > 0:
                present_indices = df[mask].index.tolist()
                y_shark = df.loc[mask, target_col].values
                X_shark = X.loc[present_indices]
                X_shark = X_shark[X.columns].copy()
                
                # Only train if there are both positive and negative examples
                if y_shark.sum() > 0 and (len(y_shark) - y_shark.sum()) > 0:
                    print(f"\nTraining model for {shark}...")
                    
                    model = RandomForestClassifier(n_estimators=100, random_state=random_state, n_jobs=-1)
                    model.fit(X_shark, y_shark)
                    
                    y_pred = model.predict(X_shark)
                    y_pred_proba = model.predict_proba(X_shark)[:, 1]
                    
                    accuracy = accuracy_score(y_shark, y_pred)
                    precision = precision_score(y_shark, y_pred, zero_division=0)
                    try:
                        roc_auc = roc_auc_score(y_shark, y_pred_proba)
                    except:
                        roc_auc = 0.5
                    
                    shark_models[shark] = model
                    results[shark] = {
                        'accuracy': accuracy,
                        'precision': precision,
                        'roc_auc': roc_auc,
                        'positive_samples': y_shark.sum(),
                        'total_samples': len(y_shark)
                    }
                    
                    # Feature importance
                    if hasattr(model, 'feature_importances_'):
                        importances = model.feature_importances_
                        importance_df = pd.DataFrame({
                            'feature': X.columns.tolist(),
                            'importance': importances
                        }).sort_values('importance', ascending=False)
                        
                        insights[shark] = {
                            'top_features': importance_df.head(5),
                            'investment_rate': y_shark.sum() / len(y_shark)
                        }
                    
                    print(f"  Accuracy: {accuracy:.4f}")
                    print(f"  Precision: {precision:.4f}")
                    print(f"  ROC-AUC: {roc_auc:.4f}")
                    print(f"  Investment rate: {y_shark.sum()}/{len(y_shark)} ({y_shark.sum()/len(y_shark)*100:.1f}%)")
    
    return shark_models, encoder_dict, scaler, X.columns.tolist(), results, insights


def save_shark_models(country, shark_models, encoder_dict, scaler, feature_names, insights):
    """
    Save shark models for a country.
    """
    config = load_config(country)
    model_path = config['model_paths']['sharks']
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    model_artifact = {
        'shark_models': shark_models,
        'encoder_dict': encoder_dict,
        'scaler': scaler,
        'feature_names': feature_names,
        'insights': insights,
        'country': country
    }
    
    joblib.dump(model_artifact, model_path)
    print(f"\nShark models saved to {model_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train shark preference models')
    parser.add_argument('--country', type=str, required=True, choices=['India', 'US', 'Australia'],
                       help='Country to train models for')
    parser.add_argument('--random-state', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    # Train models
    shark_models, encoder_dict, scaler, feature_names, results, insights = train_shark_models(
        args.country, random_state=args.random_state
    )
    
    # Save models
    save_shark_models(args.country, shark_models, encoder_dict, scaler, feature_names, insights)
    
    print(f"\n✅ Shark models training complete for {args.country}!")

