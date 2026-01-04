"""
Train deal prediction models for a specific country.
"""

import sys
import os
import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, classification_report
import joblib

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.config import load_config
from src.data_adapters import get_adapter
from src.canonical_preprocess import preprocess_canonical


def train_deal_model(country, random_state=42):
    """
    Train deal prediction model for a specific country.
    
    Parameters:
    -----------
    country : str
        Country name (India, US, Australia)
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
    print(f"Training Deal Prediction Model for {country}")
    print("=" * 60)
    
    # Load country configuration
    config = load_config(country)
    adapter = get_adapter(country)
    adapter.set_config(config)  # Use set_config method
    
    # Load data
    print(f"\n1. Loading data from {config['dataset_path']}...")
    df_raw = adapter.load_data(config['dataset_path'])
    print(f"   Loaded {len(df_raw)} rows")
    
    # Convert to canonical schema
    print("\n2. Converting to canonical schema...")
    df = adapter.to_canonical(df_raw)
    print(f"   Canonical schema: {list(df.columns)}")
    
    # Preprocess
    print("\n3. Preprocessing data...")
    X, y, encoder_dict, scaler = preprocess_canonical(df, fit=True)
    print(f"   Features: {X.shape[1]}")
    print(f"   Target distribution:\n   {y.value_counts().to_dict()}")
    
    # Train-test split (handle imbalanced data)
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state, stratify=y
        )
    except ValueError:
        # If stratification fails (e.g., too few samples in a class), use regular split
        print("   Warning: Stratified split failed, using regular split")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state
        )
    
    # Train models with class weights for imbalanced data
    models = {
        'Logistic Regression': LogisticRegression(random_state=random_state, max_iter=1000, class_weight='balanced'),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=random_state, n_jobs=-1, class_weight='balanced'),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=random_state)
    }
    
    results = {}
    print("\n4. Training models...")
    print("=" * 60)
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        
        # Handle ROC-AUC calculation (may fail for imbalanced data)
        try:
            roc_auc = roc_auc_score(y_test, y_pred_proba)
        except ValueError:
            # If ROC-AUC fails (e.g., only one class in test set), use a default value
            roc_auc = 0.5
            print(f"  Warning: ROC-AUC calculation failed, using default 0.5")
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'roc_auc': roc_auc
        }
        
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  ROC-AUC: {roc_auc:.4f}")
    
    # Select best model - handle NaN ROC-AUC values
    valid_results = {k: v for k, v in results.items() if not np.isnan(v['roc_auc']) and v['roc_auc'] > 0}
    if valid_results:
        best_model_name = max(valid_results.keys(), key=lambda k: valid_results[k]['roc_auc'])
        best_model = results[best_model_name]['model']
        best_metric = results[best_model_name]['roc_auc']
        metric_name = 'ROC-AUC'
    else:
        # Fallback to accuracy if all ROC-AUC are NaN or invalid
        print("  Warning: All ROC-AUC values are invalid, using accuracy for model selection")
        best_model_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
        best_model = results[best_model_name]['model']
        best_metric = results[best_model_name]['accuracy']
        metric_name = 'Accuracy'
    
    print("\n" + "=" * 60)
    print(f"Best Model: {best_model_name}")
    print(f"{metric_name}: {best_metric:.4f}")
    print("=" * 60)
    
    return best_model, encoder_dict, scaler, X.columns.tolist(), results


def save_deal_model(country, model, encoder_dict, scaler, feature_names):
    """
    Save deal model for a country.
    """
    config = load_config(country)
    model_path = config['model_paths']['deal']
    
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
    parser = argparse.ArgumentParser(description='Train deal prediction model')
    parser.add_argument('--country', type=str, required=True, choices=['India', 'US', 'Australia'],
                       help='Country to train model for')
    parser.add_argument('--random-state', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    # Train model
    model, encoder_dict, scaler, feature_names, results = train_deal_model(
        args.country, random_state=args.random_state
    )
    
    # Save model
    save_deal_model(args.country, model, encoder_dict, scaler, feature_names)
    
    print(f"\n✅ Deal model training complete for {args.country}!")

