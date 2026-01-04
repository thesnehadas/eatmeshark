"""
Canonical preprocessing pipeline.
Works with canonical schema (industry, ask_amount, etc.) regardless of country.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import joblib
import os


def get_canonical_features():
    """
    Get the list of canonical feature columns.
    
    Returns:
    --------
    feature_cols : list
        List of canonical feature column names
    """
    return [
        'industry',
        'ask_amount',
        'ask_equity',
        'valuation_requested',
        'monthly_sales',  # May be null for some countries
    ]


def get_shark_present_columns(df):
    """
    Get shark present columns from dataframe.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with canonical schema
    
    Returns:
    --------
    shark_cols : list
        List of shark present column names
    """
    return [col for col in df.columns if col.endswith('_present')]


def select_canonical_features(df, include_target=False):
    """
    Select canonical features from dataframe.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with canonical schema
    include_target : bool
        Whether to include target columns (only 'deal' and 'valuation', NOT outcome variables)
    
    Returns:
    --------
    df_selected : pd.DataFrame
        Dataframe with selected features
    """
    feature_cols = get_canonical_features()
    shark_cols = get_shark_present_columns(df)
    
    selected_cols = feature_cols + shark_cols
    
    if include_target:
        # Only include target labels, NOT outcome variables (deal_amount, deal_equity, deal_valuation)
        # Outcome variables should NEVER be used as features
        target_cols = ['deal', 'valuation']
        selected_cols += [col for col in target_cols if col in df.columns]
    
    # CRITICAL: Explicitly exclude outcome variables from features
    outcome_vars = ['deal_amount', 'deal_equity', 'deal_valuation']
    selected_cols = [col for col in selected_cols if col not in outcome_vars]
    
    available_cols = [col for col in selected_cols if col in df.columns]
    return df[available_cols].copy()


def handle_missing_values_canonical(df):
    """
    Handle missing values in canonical schema.
    
    CRITICAL: Do NOT fill outcome variables (deal_amount, deal_equity, deal_valuation)
    with median, as this causes data leakage. Outcome variables should remain as-is
    or be set to 0/NaN for proper target creation.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with canonical schema
    
    Returns:
    --------
    df : pd.DataFrame
        Dataframe with filled missing values
    """
    df = df.copy()
    
    # CRITICAL: Exclude outcome variables from missing value handling
    # These should NOT be filled with median as they are used to create targets
    outcome_vars = ['deal_amount', 'deal_equity', 'deal_valuation', 'deal', 'valuation']
    
    # Numeric columns (excluding outcome variables)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [col for col in numeric_cols if col not in outcome_vars]
    
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            if pd.isna(median_val):
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna(median_val)
    
    # Categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna('Unknown')
    
    # For outcome variables, set NaN to 0 (they will be used to create binary targets)
    for col in ['deal_amount', 'deal_equity', 'deal_valuation']:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    return df


def create_canonical_targets(df):
    """
    Create target variables from canonical schema.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with canonical schema
    
    Returns:
    --------
    df : pd.DataFrame
        Dataframe with target columns added
    """
    df = df.copy()
    
    # Deal target - check multiple possible columns
    if 'got_deal' in df.columns:
        # US dataset has explicit got_deal column
        df['deal'] = df['got_deal'].astype(int)
    elif 'received_offer' in df.columns:
        # Australia dataset has received_offer column
        df['deal'] = df['received_offer'].astype(int)
    elif 'deal_amount' in df.columns:
        # India and others - use deal_amount > 0
        df['deal'] = (df['deal_amount'] > 0).astype(int)
    else:
        df['deal'] = 0
    
    # Valuation target (for valuation model)
    if 'deal_valuation' in df.columns:
        df['valuation'] = df['deal_valuation']
    elif 'deal_amount' in df.columns and 'deal_equity' in df.columns:
        mask = (df['deal_amount'] > 0) & (df['deal_equity'] > 0) & (df['deal_equity'] <= 100)
        df.loc[mask, 'valuation'] = (df.loc[mask, 'deal_amount'] / df.loc[mask, 'deal_equity']) * 100
        df.loc[~mask, 'valuation'] = np.nan
    else:
        df['valuation'] = np.nan
    
    return df


def encode_canonical_features(df, fit=True, encoder_dict=None):
    """
    Encode canonical features (one-hot encode industry).
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with canonical schema
    fit : bool
        Whether to fit encoder
    encoder_dict : dict
        Encoder dictionary (required if fit=False)
    
    Returns:
    --------
    df_encoded : pd.DataFrame
        Encoded dataframe
    encoder_dict : dict
        Encoder dictionary (only if fit=True)
    """
    df = df.copy()
    
    if fit:
        # One-hot encode industry
        if 'industry' in df.columns:
            industry_encoded = pd.get_dummies(df['industry'], prefix='industry')
            df = pd.concat([df.drop('industry', axis=1), industry_encoded], axis=1)
            
            encoder_dict = {
                'industry_columns': industry_encoded.columns.tolist()
            }
        else:
            encoder_dict = {'industry_columns': []}
        
        return df, encoder_dict
    else:
        # For inference
        if encoder_dict is None:
            raise ValueError("encoder_dict required for inference")
        
        if 'industry' in df.columns:
            # Create temporary encoding
            temp_encoded = pd.get_dummies(df['industry'], prefix='industry')
            
            # Align with training columns
            industry_encoded = pd.DataFrame(index=df.index, columns=encoder_dict['industry_columns'])
            industry_encoded = industry_encoded.fillna(0)
            
            # Copy matching columns
            for col in encoder_dict['industry_columns']:
                if col in temp_encoded.columns:
                    industry_encoded[col] = temp_encoded[col]
            
            df = pd.concat([df.drop('industry', axis=1), industry_encoded], axis=1)
        else:
            # Create zero columns for all industry features
            for col in encoder_dict['industry_columns']:
                df[col] = 0
        
        return df


def preprocess_canonical(df, fit=True, encoder_dict=None, scaler=None, feature_names=None):
    """
    Complete canonical preprocessing pipeline.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with canonical schema
    fit : bool
        Whether to fit preprocessors
    encoder_dict : dict
        Encoder dictionary (required if fit=False)
    scaler : StandardScaler
        Fitted scaler (required if fit=False)
    feature_names : list
        Feature names from training (required if fit=False)
    
    Returns:
    --------
    X : pd.DataFrame
        Preprocessed features
    y : pd.Series or None
        Target variable (only if fit=True and target exists)
    encoder_dict : dict
        Encoder dictionary
    scaler : StandardScaler
        Fitted scaler
    """
    df = df.copy()
    
    # Handle missing values
    df = handle_missing_values_canonical(df)
    
    # Create targets if fitting
    if fit:
        df = create_canonical_targets(df)
    
    # Select features
    include_target = fit and 'deal' in df.columns
    df = select_canonical_features(df, include_target=include_target)
    
    # Separate features and target
    if fit and 'deal' in df.columns:
        # CRITICAL FIX: Drop ALL outcome variables, not just 'deal' and 'valuation'
        # Outcome variables (deal_amount, deal_equity, deal_valuation) should NEVER be features
        outcome_vars = ['deal', 'valuation', 'deal_amount', 'deal_equity', 'deal_valuation']
        X = df.drop(outcome_vars, axis=1, errors='ignore')
        y = df.get('deal', None)
    else:
        # For inference, also drop any outcome variables that might have leaked in
        outcome_vars = ['deal', 'valuation', 'deal_amount', 'deal_equity', 'deal_valuation']
        X = df.drop(outcome_vars, axis=1, errors='ignore')
        y = None
    
    # Encode features
    if fit:
        X, encoder_dict = encode_canonical_features(X, fit=True)
    else:
        X = encode_canonical_features(X, fit=False, encoder_dict=encoder_dict)
        
        # Align columns to feature_names
        if feature_names is not None:
            X_aligned = pd.DataFrame(index=X.index)
            for col in feature_names:
                if col in X.columns:
                    X_aligned[col] = X[col]
                else:
                    X_aligned[col] = 0
            X = X_aligned[feature_names].copy()
    
    # Scale numeric features
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    binary_cols = [col for col in numeric_cols if X[col].nunique() == 2]
    numeric_cols = [col for col in numeric_cols if col not in binary_cols]
    
    if fit:
        scaler = StandardScaler()
        X_scaled = X.copy()
        if numeric_cols:
            X_scaled[numeric_cols] = scaler.fit_transform(X[numeric_cols])
    else:
        X_scaled = X.copy()
        if scaler is not None and numeric_cols:
            scaler_feature_names = getattr(scaler, 'feature_names_in_', None)
            
            if scaler_feature_names is not None:
                available_numeric = [col for col in scaler_feature_names if col in numeric_cols and col in X.columns]
            else:
                available_numeric = [col for col in numeric_cols if col in feature_names] if feature_names else numeric_cols
            
            if available_numeric:
                if scaler_feature_names is not None:
                    ordered_cols = [col for col in scaler_feature_names if col in available_numeric]
                    X_to_scale = X[ordered_cols].copy()
                else:
                    X_to_scale = X[available_numeric].copy()
                
                scaled_values = scaler.transform(X_to_scale)
                for i, col in enumerate(X_to_scale.columns):
                    X_scaled[col] = scaled_values[:, i]
    
    if fit:
        return X_scaled, y, encoder_dict, scaler
    else:
        return X_scaled, encoder_dict, scaler

