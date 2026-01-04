"""
Train similarity models for all countries.
"""

import sys
import os
import argparse

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.similarity_finder import train_similarity_model, save_similarity_model
from src.config import get_available_countries


def train_similarity_for_country(country):
    """
    Train similarity model for a specific country.
    """
    print(f"\n{'='*60}")
    print(f"Training Similarity Model for {country}")
    print(f"{'='*60}\n")
    
    try:
        vectorizer, scaler, df_canonical = train_similarity_model(country)
        save_similarity_model(country, vectorizer, scaler, df_canonical)
        print(f"\n✅ Similarity model training complete for {country}!")
        return True
    except Exception as e:
        print(f"\n❌ Error training similarity model for {country}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train similarity models')
    parser.add_argument('--country', type=str, choices=['India', 'US', 'Australia', 'all'],
                       default='all', help='Country to train model for (default: all)')
    
    args = parser.parse_args()
    
    if args.country == 'all':
        countries = get_available_countries()
        print("Training similarity models for all countries...")
        for country in countries:
            train_similarity_for_country(country)
    else:
        train_similarity_for_country(args.country)
    
    print("\n" + "="*60)
    print("Similarity model training complete!")
    print("="*60)

