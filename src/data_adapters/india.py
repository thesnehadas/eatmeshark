"""
India-specific data adapter.
"""

from .base import BaseAdapter
import pandas as pd
import numpy as np


class IndiaAdapter(BaseAdapter):
    """
    Adapter for Shark Tank India dataset.
    """
    
    def to_canonical(self, df):
        """
        Convert India-specific dataframe to canonical schema.
        """
        df = df.copy()
        df_canonical = pd.DataFrame(index=df.index)
        
        # Map main columns
        mapping = self.column_mapping
        if 'Industry' in df.columns:
            df_canonical['industry'] = df['Industry']
        if 'Original Ask Amount' in df.columns:
            df_canonical['ask_amount'] = df['Original Ask Amount']
        if 'Original Offered Equity' in df.columns:
            df_canonical['ask_equity'] = df['Original Offered Equity']
        if 'Valuation Requested' in df.columns:
            df_canonical['valuation_requested'] = df['Valuation Requested']
        if 'Monthly Sales' in df.columns:
            df_canonical['monthly_sales'] = df['Monthly Sales']
        if 'Season Number' in df.columns:
            df_canonical['season'] = df['Season Number']
        if 'Total Deal Amount' in df.columns:
            df_canonical['deal_amount'] = df['Total Deal Amount']
        if 'Total Deal Equity' in df.columns:
            df_canonical['deal_equity'] = df['Total Deal Equity']
        if 'Deal Valuation' in df.columns:
            df_canonical['deal_valuation'] = df['Deal Valuation']
        if 'Business Description' in df.columns:
            df_canonical['business_description'] = df['Business Description']
        
        # Add shark columns
        sharks = ['Namita', 'Vineeta', 'Anupam', 'Aman', 'Peyush', 'Ritesh', 'Amit']
        for shark in sharks:
            present_col = f'{shark} Present'
            if present_col in df.columns:
                df_canonical[f'{shark.lower()}_present'] = df[present_col]
            else:
                df_canonical[f'{shark.lower()}_present'] = 0
            
            inv_amount_col = f'{shark} Investment Amount'
            if inv_amount_col in df.columns:
                df_canonical[f'{shark.lower()}_investment_amount'] = df[inv_amount_col]
            else:
                df_canonical[f'{shark.lower()}_investment_amount'] = 0
            
            inv_equity_col = f'{shark} Investment Equity'
            if inv_equity_col in df.columns:
                df_canonical[f'{shark.lower()}_investment_equity'] = df[inv_equity_col]
            else:
                df_canonical[f'{shark.lower()}_investment_equity'] = 0
        
        # Handle Ashneer (may not have all columns)
        if 'Ashneer Present' in df.columns:
            df_canonical['ashneer_present'] = df['Ashneer Present']
        else:
            df_canonical['ashneer_present'] = 0
        
        return df_canonical

