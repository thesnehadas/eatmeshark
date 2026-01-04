"""
Find similar companies based on business description and features.
Works with canonical schema and country-specific data.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import joblib
import os

from src.config import load_config
from src.data_adapters import get_adapter
from src.canonical_preprocess import preprocess_canonical


def train_similarity_model(country):
    """
    Train similarity model for a country.
    
    Parameters:
    -----------
    country : str
        Country name
    
    Returns:
    --------
    vectorizer : TfidfVectorizer
        Fitted TF-IDF vectorizer
    scaler : StandardScaler
        Fitted scaler for numeric features
    df_canonical : pd.DataFrame
        Canonical dataframe with all companies
    """
    print("=" * 60)
    print(f"Training Similarity Model for {country}")
    print("=" * 60)
    
    # Load country configuration
    from src.config import load_config
    from src.data_adapters import get_adapter
    
    config = load_config(country)
    adapter = get_adapter(country)
    adapter.set_config(config)
    
    # Load data
    print(f"\n1. Loading data from {config['dataset_path']}...")
    df_raw = adapter.load_data(config['dataset_path'])
    print(f"   Loaded {len(df_raw)} rows")
    
    # Convert to canonical schema
    print("\n2. Converting to canonical schema...")
    df = adapter.to_canonical(df_raw)
    
    # Get business descriptions
    if 'business_description' in df.columns:
        descriptions = df['business_description'].fillna('').astype(str)
    elif 'Business Description' in df_raw.columns:
        descriptions = df_raw['Business Description'].fillna('').astype(str)
    else:
        # Try to get from config mapping
        desc_col = config.get('column_mapping', {}).get('business_description')
        if desc_col and desc_col in df_raw.columns:
            descriptions = df_raw[desc_col].fillna('').astype(str)
        else:
            descriptions = pd.Series([''] * len(df))
    
    # Train TF-IDF vectorizer
    print("\n3. Training TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=100,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2
    )
    
    try:
        description_vectors = vectorizer.fit_transform(descriptions)
        print(f"   Vocabulary size: {len(vectorizer.vocabulary_)}")
    except:
        # If TF-IDF fails (e.g., all empty descriptions), create dummy vectorizer
        print("   Warning: Empty descriptions, using dummy vectorizer")
        vectorizer = TfidfVectorizer(max_features=10)
        description_vectors = vectorizer.fit_transform(['dummy'] * len(df))
    
    # Prepare numeric features for similarity
    numeric_features = ['ask_amount', 'ask_equity', 'valuation_requested', 'monthly_sales']
    available_numeric = [f for f in numeric_features if f in df.columns]
    
    if available_numeric:
        numeric_data = df[available_numeric].fillna(0)
        scaler = StandardScaler()
        numeric_scaled = scaler.fit_transform(numeric_data)
    else:
        scaler = StandardScaler()
        numeric_scaled = np.zeros((len(df), 1))
        scaler.fit(numeric_scaled)
    
    # Store company info
    df_canonical = df.copy()
    df_canonical['description_vector'] = list(description_vectors.toarray())
    df_canonical['numeric_features'] = list(numeric_scaled)
    
    # Get company names if available
    if 'startup_name' in df.columns:
        df_canonical['company_name'] = df['startup_name']
    else:
        # Try to get from raw data
        name_cols = ['Startup Name', 'Company Name', 'Name']
        company_name = None
        for col in name_cols:
            if col in df_raw.columns:
                company_name = df_raw[col]
                break
        df_canonical['company_name'] = company_name if company_name is not None else [f"Company {i+1}" for i in range(len(df))]
    
    return vectorizer, scaler, df_canonical


def save_similarity_model(country, vectorizer, scaler, df_canonical):
    """
    Save similarity model for a country.
    """
    config = load_config(country)
    model_path = config.get('model_paths', {}).get('similarity', f"models/{country.lower()}/similarity_model.joblib")
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    model_artifact = {
        'vectorizer': vectorizer,
        'scaler': scaler,
        'df_canonical': df_canonical,
        'country': country
    }
    
    joblib.dump(model_artifact, model_path)
    print(f"\nSimilarity model saved to {model_path}")


def find_similar_companies(country, business_description, top_n=5):
    """
    Find similar companies for a given business description.
    
    Parameters:
    -----------
    country : str
        Country name
    business_description : str
        Business description text
    top_n : int
        Number of similar companies to return
    
    Returns:
    --------
    similar_companies : list
        List of dictionaries with company info and similarity scores
    """
    # Load model
    config = load_config(country)
    model_path = config.get('model_paths', {}).get('similarity', f"models/{country.lower()}/similarity_model.joblib")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Similarity model not found: {model_path}. Please train the model first.")
    
    model_artifact = joblib.load(model_path)
    vectorizer = model_artifact['vectorizer']
    scaler = model_artifact['scaler']
    df_canonical = model_artifact['df_canonical']
    
    # Process input description
    if not business_description or business_description.strip() == '':
        return []
    
    # Vectorize description
    try:
        desc_vector = vectorizer.transform([business_description])
    except:
        return []
    
    # Calculate text similarity
    text_similarities = []
    for idx, row in df_canonical.iterrows():
        stored_vector = row['description_vector']
        if len(stored_vector) > 0:
            similarity = cosine_similarity(desc_vector, [stored_vector])[0][0]
            text_similarities.append(similarity)
        else:
            text_similarities.append(0.0)
    
    # Combine with numeric features (if available)
    # For now, we'll use text similarity as primary metric
    
    # Get top similar companies
    similarities = np.array(text_similarities)
    top_indices = np.argsort(similarities)[::-1][:top_n]
    
    similar_companies = []
    for idx in top_indices:
        if similarities[idx] > 0:  # Only include if there's some similarity
            row = df_canonical.iloc[idx]
            similar_companies.append({
                'company_name': row.get('company_name', f"Company {idx+1}"),
                'industry': row.get('industry', 'Unknown'),
                'ask_amount': row.get('ask_amount', 0),
                'ask_equity': row.get('ask_equity', 0),
                'similarity_score': float(similarities[idx]),
                'description': row.get('business_description', '')[:200] + '...' if len(str(row.get('business_description', ''))) > 200 else row.get('business_description', '')
            })
    
    return similar_companies

