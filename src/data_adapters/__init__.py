"""
Data adapters for mapping country-specific schemas to canonical schema.
"""

from .base import BaseAdapter
from .india import IndiaAdapter

# Auto-detect and register adapters
import os
import importlib

_ADAPTERS = {}

def get_adapter(country):
    """
    Get the appropriate adapter for a country.
    
    Parameters:
    -----------
    country : str
        Country name
    
    Returns:
    --------
    adapter : BaseAdapter
        Country-specific adapter instance
    """
    country_lower = country.lower()
    
    if country_lower not in _ADAPTERS:
        # Try to import the adapter
        try:
            module_name = f"src.data_adapters.{country_lower}"
            module = importlib.import_module(module_name)
            adapter_class = getattr(module, f"{country}Adapter")
            _ADAPTERS[country_lower] = adapter_class()
        except (ImportError, AttributeError):
            # Fallback to generic adapter
            from .base import BaseAdapter
            _ADAPTERS[country_lower] = BaseAdapter()
    
    return _ADAPTERS[country_lower]

