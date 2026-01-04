"""
Base adapter class for mapping country-specific schemas to canonical schema.
"""

import pandas as pd
import numpy as np


class BaseAdapter:
    """
    Base class for country-specific data adapters.
    Maps raw dataset columns to canonical schema.
    """
    
    def __init__(self, config=None):
        """
        Initialize adapter with configuration.
        
        Parameters:
        -----------
        config : dict
            Country configuration dictionary
        """
        self.config = config
        if config:
            self.column_mapping = config.get('column_mapping', {})
            self.sharks = config.get('sharks', [])
        else:
            self.column_mapping = {}
            self.sharks = []
    
    def set_config(self, config):
        """Set configuration after initialization."""
        self.config = config
        if config:
            self.column_mapping = config.get('column_mapping', {})
            self.sharks = config.get('sharks', [])
    
    def load_data(self, data_path):
        """
        Load raw dataset.
        
        Parameters:
        -----------
        data_path : str
            Path to dataset file
        
        Returns:
        --------
        df : pd.DataFrame
            Raw dataframe
        """
        return pd.read_csv(data_path)
    
    def to_canonical(self, df):
        """
        Convert country-specific dataframe to canonical schema.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Raw dataframe with country-specific columns
        
        Returns:
        --------
        df_canonical : pd.DataFrame
            Dataframe with canonical column names
        """
        df = df.copy()
        df_canonical = pd.DataFrame(index=df.index)
        
        # Ensure we have column_mapping (might be set via config)
        if not hasattr(self, 'column_mapping') or not self.column_mapping:
            if hasattr(self, 'config') and self.config:
                self.column_mapping = self.config.get('column_mapping', {})
                self.sharks = self.config.get('sharks', [])
            else:
                self.column_mapping = {}
                self.sharks = []
        
        # Map columns to canonical schema
        for canonical_col, raw_col in self.column_mapping.items():
            if raw_col is None or raw_col == 'null':
                # Column not available in this dataset
                df_canonical[canonical_col] = 0  # Use 0 for missing numeric columns
            elif raw_col in df.columns:
                df_canonical[canonical_col] = df[raw_col]
            else:
                df_canonical[canonical_col] = np.nan
        
        # Add business description if available
        desc_col = self.column_mapping.get('business_description')
        if desc_col and desc_col in df.columns:
            df_canonical['business_description'] = df[desc_col]
        elif 'Business Description' in df.columns:
            df_canonical['business_description'] = df['Business Description']
        
        # Add startup name if available
        name_cols = ['Startup Name', 'Company Name', 'Name']
        for col in name_cols:
            if col in df.columns:
                df_canonical['startup_name'] = df[col]
                break
        
        # Add shark present columns
        sharks_list = self.sharks if hasattr(self, 'sharks') and self.sharks else []
        for shark in sharks_list:
            shark_name = shark.get('name', '')
            if not shark_name:
                continue
                
            present_col = shark.get('present_column')
            shark_lower = shark_name.lower()
            
            if present_col and present_col in df.columns:
                df_canonical[f"{shark_lower}_present"] = df[present_col]
            else:
                df_canonical[f"{shark_lower}_present"] = 0
            
            # Add shark investment columns
            inv_amount_col = shark.get('investment_amount')
            inv_equity_col = shark.get('investment_equity')
            
            if inv_amount_col and inv_amount_col in df.columns:
                df_canonical[f"{shark_lower}_investment_amount"] = df[inv_amount_col]
            else:
                df_canonical[f"{shark_lower}_investment_amount"] = 0
            
            if inv_equity_col and inv_equity_col in df.columns:
                df_canonical[f"{shark_lower}_investment_equity"] = df[inv_equity_col]
            else:
                df_canonical[f"{shark_lower}_investment_equity"] = 0
        
        return df_canonical
    
    def from_canonical(self, data_dict):
        """
        Convert canonical input to country-specific format.
        Used for inference when user provides canonical inputs.
        
        Parameters:
        -----------
        data_dict : dict
            Dictionary with canonical column names
        
        Returns:
        --------
        data_dict : dict
            Dictionary (same format, already canonical)
        """
        # For inference, we work with canonical schema directly
        return data_dict
    
    def get_shark_names(self):
        """
        Get list of shark names for this country.
        
        Returns:
        --------
        shark_names : list
            List of shark names
        """
        return [shark['name'] for shark in self.sharks]

