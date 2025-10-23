"""
Module for loading data from Excel files
"""
import pandas as pd
from config import *


def load_holdings_data():
    """
    Load holdings data from the demat holdings Excel file
    
    Returns:
        pd.DataFrame: DataFrame with holdings information
    """
    try:
        df = pd.read_excel(HOLDINGS_FILE, sheet_name=HOLDINGS_SHEET)
        
        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        
        # Filter out rows with empty names or holdings
        df = df.dropna(subset=[NAME_COL, HOLDING_COL, CURRENT_VALUE_COL])
        
        # Convert holdings and current value to numeric
        df[HOLDING_COL] = pd.to_numeric(df[HOLDING_COL], errors='coerce')
        df[CURRENT_VALUE_COL] = pd.to_numeric(df[CURRENT_VALUE_COL], errors='coerce')
        
        return df
    except Exception as e:
        print(f"Error loading holdings data: {e}")
        raise


def load_portfolio_weights():
    """
    Load portfolio weightages from the CURRENT_WEIGHATGE Excel file
    
    Returns:
        tuple: (multi_cap_df, mid_small_cap_df)
    """
    try:
        # Read the entire sheet
        df = pd.read_excel(PORTFOLIO_FILE, sheet_name=PORTFOLIO_SHEET, header=None)
        
        # Find the starting rows for each portfolio
        multi_cap_start = None
        mid_small_cap_start = None
        
        for idx, row in df.iterrows():
            row_str = ' '.join(row.astype(str).values)
            if "GM Multi Cap" in row_str and "As on 31-Aug-2025" in row_str:
                multi_cap_start = idx + 1  # Header is next row
            elif "GM Mid & Small Cap" in row_str and "As on 31-Aug-2025" in row_str:
                mid_small_cap_start = idx + 1
        
        # Extract Multi Cap portfolio
        multi_cap_df = None
        if multi_cap_start is not None:
            # Read from the start position
            temp_df = pd.read_excel(PORTFOLIO_FILE, sheet_name=PORTFOLIO_SHEET, 
                                   header=multi_cap_start, nrows=20)
            # Find where the data ends (Total row or empty rows)
            end_idx = temp_df[temp_df.iloc[:, 1].astype(str).str.contains('Total', na=False, case=False)].index
            if len(end_idx) > 0:
                multi_cap_df = temp_df.iloc[:end_idx[0]]
            else:
                multi_cap_df = temp_df.dropna(how='all')
        
        # Extract Mid & Small Cap portfolio
        mid_small_cap_df = None
        if mid_small_cap_start is not None:
            temp_df = pd.read_excel(PORTFOLIO_FILE, sheet_name=PORTFOLIO_SHEET, 
                                   header=mid_small_cap_start, nrows=20)
            end_idx = temp_df[temp_df.iloc[:, 1].astype(str).str.contains('Total', na=False, case=False)].index
            if len(end_idx) > 0:
                mid_small_cap_df = temp_df.iloc[:end_idx[0]]
            else:
                mid_small_cap_df = temp_df.dropna(how='all')
        
        return multi_cap_df, mid_small_cap_df
        
    except Exception as e:
        print(f"Error loading portfolio weights: {e}")
        raise


def get_investor_summary(holdings_df):
    """
    Get summary of investments per investor
    
    Args:
        holdings_df: DataFrame with holdings data
        
    Returns:
        pd.DataFrame: Summary grouped by investor name
    """
    summary = holdings_df.groupby(NAME_COL).agg({
        CURRENT_VALUE_COL: 'sum',
        HOLDING_COL: 'count'
    }).reset_index()
    
    summary.columns = ['Investor Name', 'Current Total Value', 'Number of Holdings']
    
    return summary
