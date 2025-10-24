"""
Investment Calculator Module
Calculate initial investment amounts based on April 2024 prices
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json


def get_april_2024_price(stock_data, security_name, investment_date='2024-04-01'):
    """
    Get the price of a security on or nearest to April 2024
    
    Args:
        stock_data: Dict of security_name -> price series
        security_name: Name of the security
        investment_date: Investment start date
        
    Returns:
        float: Price on investment date
    """
    if security_name not in stock_data:
        return None
    
    price_series = stock_data[security_name].copy()
    
    # Remove timezone if present
    if hasattr(price_series.index, 'tz') and price_series.index.tz is not None:
        price_series.index = price_series.index.tz_localize(None)
    
    investment_dt = pd.to_datetime(investment_date)
    
    # Try to get exact date first
    if investment_dt in price_series.index:
        return float(price_series[investment_dt])
    
    # Get the nearest date after investment date
    future_dates = price_series.index[price_series.index >= investment_dt]
    if len(future_dates) > 0:
        nearest_date = future_dates[0]
        return float(price_series[nearest_date])
    
    # If no future dates, get the last available date before
    past_dates = price_series.index[price_series.index < investment_dt]
    if len(past_dates) > 0:
        nearest_date = past_dates[-1]
        # Warn if data is too old (more than 30 days)
        days_diff = (investment_dt - nearest_date).days
        if days_diff > 30:
            print(f"  ⚠️ Warning: Using price from {days_diff} days before investment date for {security_name}")
        return float(price_series[nearest_date])
    
    return None


def calculate_investment_values(holdings_df, stock_data, investment_date='2024-04-01'):
    """
    Calculate the investment value for each holding based on April 2024 prices
    
    Args:
        holdings_df: DataFrame with holdings
        stock_data: Dict of security_name -> price series
        investment_date: Investment start date
        
    Returns:
        DataFrame with investment values added
    """
    print("\n📊 Calculating April 2024 Investment Values:")
    print("-" * 50)
    
    # Create a copy of holdings
    investment_df = holdings_df.copy()
    
    # Add columns for April price and investment value
    investment_df['April_2024_Price'] = 0.0
    investment_df['Investment_Value'] = 0.0
    investment_df['Current_Price'] = 0.0
    investment_df['Gain_Loss'] = 0.0
    investment_df['Gain_Loss_Percent'] = 0.0
    
    # Calculate for each security
    for idx, row in investment_df.iterrows():
        security_name = row['Security Name']
        holding = row['Holding']
        current_value = row['Demat Holding Vlaue (Rs.)']
        
        # Get April 2024 price
        april_price = get_april_2024_price(stock_data, security_name, investment_date)
        
        if april_price is not None:
            investment_value = holding * april_price
            investment_df.at[idx, 'April_2024_Price'] = april_price
            investment_df.at[idx, 'Investment_Value'] = investment_value
            
            # Calculate current price from current value
            if holding > 0:
                current_price = current_value / holding
                investment_df.at[idx, 'Current_Price'] = current_price
                
                # Calculate gain/loss
                gain_loss = current_value - investment_value
                investment_df.at[idx, 'Gain_Loss'] = gain_loss
                
                if investment_value > 0:
                    gain_loss_pct = (gain_loss / investment_value) * 100
                    investment_df.at[idx, 'Gain_Loss_Percent'] = gain_loss_pct
        else:
            print(f"  ⚠️ No price data for {security_name}")
    
    # Summary statistics
    total_investment = investment_df['Investment_Value'].sum()
    total_current = investment_df['Demat Holding Vlaue (Rs.)'].sum()
    total_gain = total_current - total_investment
    
    if total_investment > 0:
        total_gain_pct = (total_gain / total_investment) * 100
    else:
        total_gain_pct = 0
    
    print(f"\n📈 Portfolio Summary:")
    print(f"  Total Investment (April 2024): ₹{total_investment:,.0f}")
    print(f"  Total Current Value: ₹{total_current:,.0f}")
    print(f"  Total Gain/Loss: ₹{total_gain:,.0f} ({total_gain_pct:+.2f}%)")
    
    return investment_df


def calculate_investor_wise_investments(investment_df):
    """
    Calculate investment summary for each investor
    
    Args:
        investment_df: DataFrame with investment values
        
    Returns:
        DataFrame with investor-wise summary
    """
    if 'NAME' not in investment_df.columns:
        # Single portfolio case
        return pd.DataFrame([{
            'Investor': 'Portfolio',
            'Investment_April_2024': investment_df['Investment_Value'].sum(),
            'Current_Value': investment_df['Demat Holding Vlaue (Rs.)'].sum(),
            'Gain_Loss': investment_df['Gain_Loss'].sum(),
            'Gain_Loss_Percent': (investment_df['Gain_Loss'].sum() / 
                                 investment_df['Investment_Value'].sum() * 100) 
                                if investment_df['Investment_Value'].sum() > 0 else 0,
            'Num_Securities': len(investment_df)
        }])
    
    # Group by investor
    investor_summary = investment_df.groupby('NAME').agg({
        'Investment_Value': 'sum',
        'Demat Holding Vlaue (Rs.)': 'sum',
        'Gain_Loss': 'sum',
        'Security Name': 'count'
    }).reset_index()
    
    investor_summary.columns = ['Investor', 'Investment_April_2024', 
                                'Current_Value', 'Gain_Loss', 'Num_Securities']
    
    # Calculate percentage gain/loss
    investor_summary['Gain_Loss_Percent'] = (
        investor_summary['Gain_Loss'] / investor_summary['Investment_April_2024'] * 100
    ).fillna(0)
    
    # Sort by performance
    investor_summary = investor_summary.sort_values('Gain_Loss_Percent', ascending=False)
    
    return investor_summary


def export_investment_report(investment_df, investor_summary, output_dir='reports'):
    """
    Export detailed investment report to Excel
    
    Args:
        investment_df: Detailed holdings with investment values
        investor_summary: Investor-wise summary
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = output_path / f'investment_analysis_{timestamp}.xlsx'
    
    # Create Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Write investor summary
        investor_summary.to_excel(writer, sheet_name='Investor Summary', index=False)
        
        # Write detailed holdings
        investment_df.to_excel(writer, sheet_name='Detailed Holdings', index=False)
        
        # Format the Excel file
        workbook = writer.book
        
        # Format investor summary sheet
        ws_summary = writer.sheets['Investor Summary']
        
        # Add number formatting
        for row in ws_summary.iter_rows(min_row=2):
            row[1].number_format = '₹#,##0'  # Investment
            row[2].number_format = '₹#,##0'  # Current Value
            row[3].number_format = '₹#,##0'  # Gain/Loss
            row[4].number_format = '0.00%'   # Percentage
        
        # Format detailed holdings sheet
        ws_detail = writer.sheets['Detailed Holdings']
        
        # Add number formatting for currency columns
        for col_letter in ['E', 'F', 'G', 'H', 'I', 'J']:  # Adjust based on actual columns
            for cell in ws_detail[col_letter]:
                if cell.row > 1:  # Skip header
                    if col_letter in ['E', 'F', 'G', 'H', 'I']:
                        cell.number_format = '₹#,##0.00'
                    elif col_letter == 'J':
                        cell.number_format = '0.00%'
    
    print(f"\n📄 Investment report saved: {filename}")
    
    # Also save as JSON for programmatic access
    json_filename = output_path / f'investment_data_{timestamp}.json'
    
    json_data = {
        'timestamp': timestamp,
        'summary': {
            'total_investment': float(investor_summary['Investment_April_2024'].sum()),
            'total_current_value': float(investor_summary['Current_Value'].sum()),
            'total_gain_loss': float(investor_summary['Gain_Loss'].sum()),
            'total_gain_loss_percent': float(
                investor_summary['Gain_Loss'].sum() / 
                investor_summary['Investment_April_2024'].sum() * 100
            ) if investor_summary['Investment_April_2024'].sum() > 0 else 0,
            'num_investors': len(investor_summary),
            'num_securities': int(investor_summary['Num_Securities'].sum())
        },
        'investors': investor_summary.to_dict('records'),
        'top_performers': investor_summary.head(5).to_dict('records'),
        'bottom_performers': investor_summary.tail(5).to_dict('records')
    }
    
    with open(json_filename, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)
    
    print(f"📄 Investment data JSON saved: {json_filename}")
    
    return filename


if __name__ == "__main__":
    print("Investment Calculator Module")
    print("Handles April 2024 investment value calculations")
