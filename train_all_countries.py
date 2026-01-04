"""
Master script to train all models for all countries.
"""

import sys
import os
import subprocess

from src.config import get_available_countries

if __name__ == '__main__':
    print("=" * 60)
    print("Global Shark Tank Intelligence - Training All Models")
    print("=" * 60)
    
    countries = get_available_countries()
    print(f"\nAvailable countries: {', '.join(countries)}")
    
    for country in countries:
        print("\n" + "=" * 60)
        print(f"Training models for {country}")
        print("=" * 60)
        
        # Train deal model
        print(f"\n[1/3] Training deal model for {country}...")
        try:
            subprocess.run([
                sys.executable, "src/train_deal.py", 
                "--country", country
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error training deal model: {e}")
        
        # Train valuation model
        print(f"\n[2/3] Training valuation model for {country}...")
        try:
            subprocess.run([
                sys.executable, "src/train_valuation.py",
                "--country", country
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error training valuation model: {e}")
        
        # Train shark models
        print(f"\n[3/4] Training shark models for {country}...")
        try:
            subprocess.run([
                sys.executable, "src/train_sharks.py",
                "--country", country
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error training shark models: {e}")
        
        # Train similarity model
        print(f"\n[4/4] Training similarity model for {country}...")
        try:
            subprocess.run([
                sys.executable, "src/train_similarity.py",
                "--country", country
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error training similarity model: {e}")
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print("\nYou can now run the app with: streamlit run app.py")

