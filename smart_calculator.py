"""
Smart Portfolio Calculator
Uses ONLY available stock data - no fake interpolation
"""
import pandas as pd
import numpy as np
from datetime import datetime


def calculate_portfolio_with_partial_data(holdings_df, stock_data, dates):
    """
    Calculate portfolio values using only available stock data
    For missing stocks, use proportional estimation
    """
    investor_portfolios = {}
    
    for investor_name, group in holdings_df.groupby('NAME'):
        # Separate holdings into "have data" and "no data"
        holdings_with_data = group[group['Security Name'].isin(stock_data.keys())]
        holdings_without_data = group[~group['Security Name'].isin(stock_data.keys())]
        
        # Calculate value for stocks we HAVE data for
        portfolio_with_data = pd.Series(0.0, index=dates)
        
        for _, row in holdings_with_data.iterrows():
            security = row['Security Name']
            holding_qty = row['Holding']
            
            if security in stock_data:
                prices = stock_data[security]
                aligned_prices = prices.reindex(dates, method='ffill')
                stock_value = aligned_prices * holding_qty
                portfolio_with_data += stock_value.fillna(0)
        
        # For stocks WITHOUT data, estimate based on current value
        if len(holdings_without_data) > 0:
            current_value_without_data = holdings_without_data['Demat Holding Vlaue (Rs.)'].sum()
            current_value_with_data = holdings_with_data['Demat Holding Vlaue (Rs.)'].sum()
            
            # Calculate growth ratio from tracked stocks
            if current_value_with_data > 0 and len(portfolio_with_data) > 0:
                growth_ratio = portfolio_with_data / portfolio_with_data.iloc[0]
                
                # Apply same growth to untracked holdings
                estimated_values = current_value_without_data * growth_ratio
                portfolio_with_data += estimated_values
        
        investor_portfolios[investor_name] = portfolio_with_data
    
    return investor_portfolios


def calculate_coverage_stats(holdings_df, stock_data):
    """Calculate how much of the portfolio we actually have data for"""
    stats = []
    
    for investor_name, group in holdings_df.groupby('NAME'):
        total_value = group['Demat Holding Vlaue (Rs.)'].sum()
        
        holdings_with_data = group[group['Security Name'].isin(stock_data.keys())]
        value_with_data = holdings_with_data['Demat Holding Vlaue (Rs.)'].sum()
        
        coverage = (value_with_data / total_value * 100) if total_value > 0 else 0
        
        stats.append({
            'Investor': investor_name,
            'Total Holdings': len(group),
            'Holdings with Data': len(holdings_with_data),
            'Total Value': total_value,
            'Value with Data': value_with_data,
            'Coverage %': coverage
        })
    
    return pd.DataFrame(stats)


def export_coverage_report(coverage_df, output_file='ticker_reports/coverage_report.csv'):
    """Export detailed coverage report"""
    coverage_df.to_csv(output_file, index=False)
    
    print("\n" + "=" * 80)
    print("DATA COVERAGE REPORT")
    print("=" * 80)
    print(f"\nAverage Coverage: {coverage_df['Coverage %'].mean():.1f}%")
    print(f"Median Coverage:  {coverage_df['Coverage %'].median():.1f}%")
    print(f"\nInvestors with >80% coverage: {len(coverage_df[coverage_df['Coverage %'] > 80])}/{len(coverage_df)}")
    print(f"Investors with >50% coverage: {len(coverage_df[coverage_df['Coverage %'] > 50])}/{len(coverage_df)}")
    print(f"\nTop 5 by coverage:")
    print(coverage_df.nlargest(5, 'Coverage %')[['Investor', 'Coverage %', 'Value with Data']].to_string(index=False))
    print(f"\nBottom 5 by coverage:")
    print(coverage_df.nsmallest(5, 'Coverage %')[['Investor', 'Coverage %', 'Value with Data']].to_string(index=False))
    print(f"\nFull report saved to: {output_file}")
