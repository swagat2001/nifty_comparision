"""
Module for loading data from Excel files
Auto-detects column names and handles multiple funds in one sheet
"""
import pandas as pd
from config import HOLDINGS_FILE, HOLDINGS_SHEET, WEIGHTS_FILE


def detect_columns(df):
    """Auto-detect column names from dataframe"""
    cols = {str(col).lower().strip(): col for col in df.columns}
    
    # Detect NAME column
    name_col = None
    for key in ['name', 'investor name', 'investor', 'client name']:
        if key in cols:
            name_col = cols[key]
            break
    
    # Detect Security Name column
    security_col = None
    for key in ['security name', 'security', 'stock name', 'stock', 'company', 'scrip name']:
        if key in cols:
            security_col = cols[key]
            break
    
    # Detect Holding/Quantity column
    holding_col = None
    for key in ['holding', 'holdings', 'quantity', 'qty', 'shares']:
        if key in cols:
            holding_col = cols[key]
            break
    
    # Detect Current Value column
    value_col = None
    for key in ['demat holding vlaue (rs.)', 'current value', 'value', 'market value', 
                'holding value', 'amount', 'demat holding value']:
        if key in cols:
            value_col = cols[key]
            break
    
    return name_col, security_col, holding_col, value_col


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
        
        # Auto-detect columns
        name_col, security_col, holding_col, value_col = detect_columns(df)
        
        if not all([security_col, holding_col, value_col]):
            print("⚠️  Could not auto-detect all required columns")
            print(f"Available columns: {df.columns.tolist()}")
            raise ValueError("Missing required columns")
        
        # Rename to standard names for easier processing
        rename_map = {}
        if name_col:
            rename_map[name_col] = 'NAME'
        if security_col:
            rename_map[security_col] = 'Security Name'
        if holding_col:
            rename_map[holding_col] = 'Holding'
        if value_col:
            rename_map[value_col] = 'Demat Holding Vlaue (Rs.)'
        
        df = df.rename(columns=rename_map)
        
        # Filter out rows with empty values
        required_cols = ['Security Name', 'Holding', 'Demat Holding Vlaue (Rs.)']
        if 'NAME' in df.columns:
            required_cols.insert(0, 'NAME')
        
        df = df.dropna(subset=required_cols)
        
        # Convert to numeric
        df['Holding'] = pd.to_numeric(df['Holding'], errors='coerce')
        df['Demat Holding Vlaue (Rs.)'] = pd.to_numeric(df['Demat Holding Vlaue (Rs.)'], errors='coerce')
        
        # Remove any rows that became NaN after conversion
        df = df.dropna(subset=['Holding', 'Demat Holding Vlaue (Rs.)'])
        
        print(f"  ✓ Loaded {len(df)} holdings")
        print(f"  ✓ Columns used: {', '.join(rename_map.keys())}")
        
        return df
        
    except Exception as e:
        print(f"Error loading holdings data: {e}")
        raise


def load_both_funds_from_sheet(weights_file):
    """
    Load BOTH fund weights from the same sheet
    Sheet has Multi Cap at top, Mid & Small Cap below it
    
    Returns:
        tuple: (multi_cap_weights, mid_small_weights)
    """
    try:
        # Read the entire sheet
        df = pd.read_excel(weights_file, sheet_name='Sheet', header=None)
        
        # Find the two fund sections
        multi_cap_start = None
        mid_small_start = None
        
        for idx, row in df.iterrows():
            row_str = ' '.join(str(cell) for cell in row if pd.notna(cell))
            
            if 'GM Multi Cap' in row_str and 'Aug-2025' in row_str:
                multi_cap_start = idx + 1  # Next row is header
            elif 'GM Mid & Small Cap' in row_str and 'Aug-2025' in row_str:
                mid_small_start = idx + 1  # Next row is header
        
        if not multi_cap_start or not mid_small_start:
            print(f"⚠️  Could not find fund sections")
            print(f"   Multi Cap start: {multi_cap_start}")
            print(f"   Mid & Small start: {mid_small_start}")
            return {}, {}
        
        # Extract Multi Cap Fund
        multi_cap_df = pd.read_excel(weights_file, sheet_name='Sheet', 
                                     header=multi_cap_start, 
                                     nrows=mid_small_start - multi_cap_start - 3)
        
        # Extract Mid & Small Cap Fund
        mid_small_df = pd.read_excel(weights_file, sheet_name='Sheet', 
                                     header=mid_small_start, 
                                     nrows=20)
        
        # Clean both dataframes
        def extract_weights(df, fund_name):
            # First, drop rows where Scrip Name column is NaN
            # Find Scrip Name column first
            scrip_col = None
            for col_name in df.columns:
                col_lower = str(col_name).lower().strip()
                if 'scrip name' in col_lower or 'security name' in col_lower:
                    scrip_col = col_name
                    break
            
            if scrip_col:
                df = df.dropna(subset=[scrip_col])
            
            # Remove rows with 'Total' in first column or scrip column
            df = df[~df.iloc[:, 0].astype(str).str.contains('Total', na=False, case=False)]
            if scrip_col:
                df = df[~df[scrip_col].astype(str).str.contains('Total', na=False, case=False)]
            
            # Find Weightage column - use substring matching
            weight_col = None
            for col_name in df.columns:
                col_lower = str(col_name).lower().strip()
                if 'weightage' in col_lower or 'allocation' in col_lower:
                    weight_col = col_name
                    break
            
            if not scrip_col or not weight_col:
                print(f"  ⚠️  Could not find columns in {fund_name}")
                print(f"     Available: {df.columns.tolist()}")
                return {}
            
            print(f"  ✓ {fund_name}: Using '{scrip_col}' and '{weight_col}'")
            
            # Create weights dictionary - with extra validation
            weights = {}
            for _, row in df.iterrows():
                security = row[scrip_col]
                weight = row[weight_col]
                
                # Skip if either is NaN
                if pd.isna(security) or pd.isna(weight):
                    continue
                
                # Convert to string and strip
                security_str = str(security).strip()
                
                # Skip if empty or looks like garbage
                if not security_str or security_str.lower() in ['nan', 'total', '']:
                    continue
                
                # Convert weight to float
                try:
                    weight_float = float(weight)
                    # Only add if weight is positive
                    if weight_float > 0:
                        weights[security_str] = weight_float
                except (ValueError, TypeError):
                    continue
            
            return weights
        
        multi_cap_weights = extract_weights(multi_cap_df, "GM Multi Cap Fund")
        mid_small_weights = extract_weights(mid_small_df, "GM Mid & Small Cap Fund")
        
        print(f"  ✓ GM Multi Cap Fund: {len(multi_cap_weights)} securities")
        print(f"  ✓ GM Mid & Small Cap Fund: {len(mid_small_weights)} securities")
        
        return multi_cap_weights, mid_small_weights
        
    except Exception as e:
        print(f"  ⚠️  Error loading funds: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}


def get_investor_summary(holdings_df):
    """
    Get summary of investments per investor
    
    Args:
        holdings_df: DataFrame with holdings data
        
    Returns:
        pd.DataFrame: Summary grouped by investor name
    """
    if 'NAME' not in holdings_df.columns:
        # No investor names, return single summary
        return pd.DataFrame([{
            'Investor Name': 'Portfolio',
            'Current Total Value': holdings_df['Demat Holding Vlaue (Rs.)'].sum(),
            'Number of Holdings': len(holdings_df)
        }])
    
    summary = holdings_df.groupby('NAME').agg({
        'Demat Holding Vlaue (Rs.)': 'sum',
        'Holding': 'count'
    }).reset_index()
    
    summary.columns = ['Investor Name', 'Current Total Value', 'Number of Holdings']
    
    return summary


if __name__ == "__main__":
    # Test loading
    print("\n" + "="*80)
    print("TESTING DATA LOADER")
    print("="*80)
    
    try:
        holdings_df = load_holdings_data()
        print(f"\n✓ Holdings loaded successfully")
        print(f"  Shape: {holdings_df.shape}")
        
        multi_cap, mid_small = load_both_funds_from_sheet(WEIGHTS_FILE)
        print(f"\n✓ Funds loaded successfully")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    print("\n" + "="*80 + "\n")
