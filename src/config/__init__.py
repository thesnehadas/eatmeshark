"""
Configuration module for country-specific settings.
"""

import yaml
import os

def load_config(country):
    """
    Load configuration for a specific country.
    
    Parameters:
    -----------
    country : str
        Country name (India, US, Australia)
    
    Returns:
    --------
    config : dict
        Configuration dictionary
    """
    country_lower = country.lower()
    config_path = os.path.join(os.path.dirname(__file__), f"{country_lower}.yaml")
    
    if not os.path.exists(config_path):
        raise ValueError(f"Configuration file not found for country: {country}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

def get_available_countries():
    """
    Get list of available countries based on config files.
    
    Returns:
    --------
    countries : list
        List of country names
    """
    config_dir = os.path.dirname(__file__)
    countries = []
    
    for filename in os.listdir(config_dir):
        if filename.endswith('.yaml') and filename != '__init__.py':
            country_lower = filename.replace('.yaml', '')
            # Capitalize properly
            if country_lower == 'us':
                country = 'US'
            else:
                country = country_lower.title()
            countries.append(country)
    
    # Sort with India first, then US, then others
    return sorted(countries, key=lambda x: (x != 'India', x != 'US', x))

