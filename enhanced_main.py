"""
Enhanced Investment Comparison Analysis
- Individual investor tracking
- Monthly performance visualization
- TradingView-style interactive charts
- Comparison with NIFTY and GM Funds
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

from config import INVESTMENT_DATE, OUTPUT_DIR, HOLDINGS_FILE, WEIGHTS_FILE
from data_loader import load_holdings_data, load_both_funds_from_sheet
from market_data import fetch_nifty_data
from ticker_resolver import resolve_all_tickers
from nse_data_loader import load_all_nse_data
from enhanced_visualizer import create_interactive_comparison_dashboard


def calculate_individual_investments(holdings_df, stock_data, investment_date='2024-04-01'):
    """
    Calculate the initial investment amount for each investor based on April 2024 prices
    
    Returns:
        dict: Investor name -> initial investment amount
    """
    print("\n📊 Calculating individual investment amounts...")
    
    # Get April 2024 prices for each security
    april_prices = {}
    investment_dt = pd.to_datetime(investment_date)
    
    for security_name in holdings_df['Security Name'].unique():
        if security_name in stock_data:
            security_data = stock_data[security_name]
            # Get price on or after investment date
            valid_dates = security_data.index >= investment_dt
            if valid_dates.any():
                april_price = security_data[valid_dates].iloc[0]
                april_prices[security_name] = april_price
            else:
                # If no data after investment date, use last available
                april_prices[security_name] = security_data.iloc[-1]
        else:
            print(f"  ⚠️ No price data for {security_name}")
    
    # Calculate investment amount for each investor
    investor_investments = {}
    
    if 'NAME' in holdings_df.columns:
        # Group by investor
        for investor_name in holdings_df['NAME'].unique():
            if pd.isna(investor_name):
                continue
                
            investor_holdings = holdings_df[holdings_df['NAME'] == investor_name]
            total_investment = 0
            
            for _, row in investor_holdings.iterrows():
                security = row['Security Name']
                quantity = row['Holding']
                
                if security in april_prices:
                    investment_value = quantity * april_prices[security]
                    total_investment += investment_value
            
            investor_investments[investor_name] = total_investment
            print(f"  {investor_name}: ₹{total_investment:,.0f}")
    else:
        # Single investor case
        total_investment = 0
        for _, row in holdings_df.iterrows():
            security = row['Security Name']
            quantity = row['Holding']
            
            if security in april_prices:
                investment_value = quantity * april_prices[security]
                total_investment += investment_value
        
        investor_investments['Portfolio'] = total_investment
        print(f"  Total Portfolio: ₹{total_investment:,.0f}")
    
    return investor_investments, april_prices


def calculate_monthly_returns(data_series, start_date='2024-04-01'):
    """
    Calculate monthly returns from daily data
    
    Returns:
        pd.Series: Monthly returns
    """
    # Ensure we have a datetime index
    if not isinstance(data_series.index, pd.DatetimeIndex):
        data_series.index = pd.to_datetime(data_series.index)
    
    # Remove timezone info if present to avoid comparison issues
    if hasattr(data_series.index, 'tz') and data_series.index.tz is not None:
        data_series.index = data_series.index.tz_localize(None)
    
    # Filter data from start date
    start_dt = pd.to_datetime(start_date)
    data_series = data_series[data_series.index >= start_dt]
    
    if len(data_series) == 0:
        return pd.Series()
    
    # Resample to monthly (last business day of month)
    monthly_data = data_series.resample('M').last()
    
    # Calculate cumulative returns
    initial_value = data_series.iloc[0]
    if initial_value != 0:
        monthly_returns = ((monthly_data / initial_value) - 1) * 100
    else:
        monthly_returns = pd.Series(0, index=monthly_data.index)
    
    return monthly_returns


def calculate_investor_portfolios(holdings_df, stock_data, investment_date='2024-04-01'):
    """
    Calculate portfolio value over time for each investor
    
    Returns:
        dict: Investor name -> portfolio value series
    """
    print("\n📈 Calculating portfolio performance for each investor...")
    
    portfolios = {}
    
    if 'NAME' in holdings_df.columns:
        # Multiple investors
        for investor_name in holdings_df['NAME'].unique():
            if pd.isna(investor_name):
                continue
            
            investor_holdings = holdings_df[holdings_df['NAME'] == investor_name]
            
            # Calculate portfolio value for this investor
            portfolio_value = None
            
            for _, row in investor_holdings.iterrows():
                security = row['Security Name']
                quantity = row['Holding']
                
                if security in stock_data:
                    # Get security data and remove timezone if present
                    security_series = stock_data[security].copy()
                    if hasattr(security_series.index, 'tz') and security_series.index.tz is not None:
                        security_series.index = security_series.index.tz_localize(None)
                    security_value = security_series * quantity
                    
                    if portfolio_value is None:
                        portfolio_value = security_value.copy()
                    else:
                        # Align indices and add
                        portfolio_value = portfolio_value.add(security_value, fill_value=0)
            
            if portfolio_value is not None:
                portfolios[investor_name] = portfolio_value
                print(f"  ✓ {investor_name}: {len(portfolio_value)} data points")
    else:
        # Single portfolio
        portfolio_value = None
        
        for _, row in holdings_df.iterrows():
            security = row['Security Name']
            quantity = row['Holding']
            
            if security in stock_data:
                # Get security data and remove timezone if present
                security_series = stock_data[security].copy()
                if hasattr(security_series.index, 'tz') and security_series.index.tz is not None:
                    security_series.index = security_series.index.tz_localize(None)
                security_value = security_series * quantity
                
                if portfolio_value is None:
                    portfolio_value = security_value.copy()
                else:
                    portfolio_value = portfolio_value.add(security_value, fill_value=0)
        
        if portfolio_value is not None:
            portfolios['Portfolio'] = portfolio_value
            print(f"  ✓ Portfolio: {len(portfolio_value)} data points")
    
    return portfolios


def calculate_fund_portfolio(stock_data, fund_weights, initial_investment, investment_date='2024-04-01'):
    """
    Calculate fund portfolio value based on weights and initial investment
    """
    if not fund_weights:
        return pd.Series()
    
    # Normalize weights
    total_weight = sum(fund_weights.values())
    if total_weight == 0:
        return pd.Series()
    
    normalized_weights = {k: v/total_weight for k, v in fund_weights.items()}
    
    # Find common date range
    investment_dt = pd.to_datetime(investment_date)
    
    # Get all available dates
    all_dates = set()
    for security_name in fund_weights.keys():
        if security_name in stock_data:
            # Remove timezone if present
            security_series = stock_data[security_name].copy()
            if hasattr(security_series.index, 'tz') and security_series.index.tz is not None:
                security_series.index = security_series.index.tz_localize(None)
            dates = security_series.index[security_series.index >= investment_dt]
            all_dates.update(dates)
    
    if not all_dates:
        return pd.Series()
    
    all_dates = sorted(all_dates)
    
    # Calculate fund portfolio value
    fund_portfolio = pd.Series(0, index=all_dates)
    
    for security_name, weight in normalized_weights.items():
        if security_name in stock_data:
            # Get security data
            security_data = stock_data[security_name].copy()
            
            # Remove timezone if present
            if hasattr(security_data.index, 'tz') and security_data.index.tz is not None:
                security_data.index = security_data.index.tz_localize(None)
            
            # Get initial price
            valid_dates = security_data.index >= investment_dt
            if valid_dates.any():
                initial_price = security_data[valid_dates].iloc[0]
                
                # Calculate shares to buy with weighted investment
                investment_amount = initial_investment * weight
                shares = investment_amount / initial_price
                
                # Calculate portfolio value over time
                security_values = security_data.reindex(all_dates, method='ffill').fillna(0) * shares
                fund_portfolio += security_values
    
    return fund_portfolio


def main():
    """Enhanced main function with individual investor tracking"""
    print("=" * 80)
    print("ENHANCED INVESTMENT COMPARISON ANALYSIS")
    print("=" * 80)
    
    # Step 1: Load holdings data
    print("\nStep 1: Loading holdings data...")
    holdings_df = load_holdings_data()
    if holdings_df is None or len(holdings_df) == 0:
        print("❌ No holdings data loaded")
        return
    
    # Check for individual investors
    has_multiple_investors = 'NAME' in holdings_df.columns
    if has_multiple_investors:
        num_investors = holdings_df['NAME'].nunique()
        print(f"  ✓ Found {num_investors} individual investors")
    else:
        print("  ✓ Processing as single portfolio")
    
    # Step 2: Load fund weights
    print("\nStep 2: Loading mutual fund weights...")
    multi_cap_weights, mid_small_weights = load_both_funds_from_sheet(WEIGHTS_FILE)
    
    # Step 3: Resolve tickers
    print("\nStep 3: Resolving tickers...")
    
    # Get all unique securities
    all_securities = list(holdings_df['Security Name'].unique())
    all_securities.extend(multi_cap_weights.keys())
    all_securities.extend(mid_small_weights.keys())
    all_securities = list(set(all_securities))
    
    # Create temp DataFrame for resolver
    temp_df = pd.DataFrame({'Security Name': all_securities})
    success_map, failed_list = resolve_all_tickers(temp_df, INVESTMENT_DATE)
    
    print(f"  ✅ Success: {len(success_map)}/{len(all_securities)}")
    print(f"  ❌ Failed: {len(failed_list)}/{len(all_securities)}")
    
    # Step 4: Load stock data
    print("\nStep 4: Loading stock price data...")
    stock_data = load_all_nse_data(success_map, INVESTMENT_DATE)
    
    if len(stock_data) == 0:
        print("❌ No stock data available")
        return
    
    print(f"  ✓ Loaded {len(stock_data)} securities")
    
    # Step 5: Calculate initial investments
    investor_investments, april_prices = calculate_individual_investments(
        holdings_df, stock_data, INVESTMENT_DATE
    )
    
    # Step 6: Calculate portfolio values over time
    investor_portfolios = calculate_investor_portfolios(
        holdings_df, stock_data, INVESTMENT_DATE
    )
    
    # Step 7: Calculate monthly returns for each investor
    print("\nStep 7: Calculating monthly returns...")
    monthly_returns = {}
    
    for investor_name, portfolio_series in investor_portfolios.items():
        monthly_ret = calculate_monthly_returns(portfolio_series, INVESTMENT_DATE)
        if len(monthly_ret) > 0:
            monthly_returns[investor_name] = monthly_ret
            print(f"  ✓ {investor_name}: {len(monthly_ret)} months")
    
    # Step 8: Calculate NIFTY returns
    print("\nStep 8: Fetching NIFTY 50 data...")
    nifty_data_dict = fetch_nifty_data(INVESTMENT_DATE)
    
    nifty_monthly = pd.Series()
    if nifty_data_dict and 'NIFTY 50' in nifty_data_dict:
        nifty_series = nifty_data_dict['NIFTY 50']
        nifty_monthly = calculate_monthly_returns(nifty_series, INVESTMENT_DATE)
        print(f"  ✓ NIFTY 50: {len(nifty_monthly)} months")
    
    # Step 9: Calculate fund returns based on investor investments
    print("\nStep 9: Calculating fund portfolio performance...")
    
    # Calculate total investment across all investors
    total_investment = sum(investor_investments.values())
    
    # Calculate fund portfolios
    multi_cap_portfolio = calculate_fund_portfolio(
        stock_data, multi_cap_weights, total_investment, INVESTMENT_DATE
    )
    multi_cap_monthly = calculate_monthly_returns(multi_cap_portfolio, INVESTMENT_DATE)
    
    mid_small_portfolio = calculate_fund_portfolio(
        stock_data, mid_small_weights, total_investment, INVESTMENT_DATE
    )
    mid_small_monthly = calculate_monthly_returns(mid_small_portfolio, INVESTMENT_DATE)
    
    print(f"  ✓ GM Multi Cap: {len(multi_cap_monthly)} months")
    print(f"  ✓ GM Mid & Small Cap: {len(mid_small_monthly)} months")
    
    # Step 10: Create interactive visualization
    print("\nStep 10: Creating interactive dashboard...")
    
    # Prepare data for visualization
    viz_data = {
        'investors': monthly_returns,
        'nifty': nifty_monthly,
        'multi_cap': multi_cap_monthly,
        'mid_small': mid_small_monthly,
        'investments': investor_investments
    }
    
    # Create dashboard
    dashboard_file = create_interactive_comparison_dashboard(viz_data)
    
    # Step 11: Summary statistics
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    
    if len(monthly_returns) > 0:
        # Get latest returns
        latest_month = max([ret.index[-1] for ret in monthly_returns.values()])
        
        print(f"\n📊 Performance as of {latest_month.strftime('%B %Y')}:")
        print("-" * 50)
        
        # Individual investor returns
        investor_performance = []
        for name, returns in monthly_returns.items():
            if len(returns) > 0:
                final_return = returns.iloc[-1]
                investor_performance.append((name, final_return))
        
        # Sort by performance
        investor_performance.sort(key=lambda x: x[1], reverse=True)
        
        # Show top 5 and bottom 5
        print("\n🏆 Top 5 Performers:")
        for i, (name, ret) in enumerate(investor_performance[:5], 1):
            print(f"  {i}. {name[:30]:30s}: {ret:>8.2f}%")
        
        if len(investor_performance) > 10:
            print("\n📉 Bottom 5 Performers:")
            for i, (name, ret) in enumerate(investor_performance[-5:], 1):
                print(f"  {i}. {name[:30]:30s}: {ret:>8.2f}%")
        
        # Average performance
        avg_return = np.mean([ret for _, ret in investor_performance])
        print(f"\n📊 Average Investor Return: {avg_return:.2f}%")
        
        # Benchmark comparison
        if len(nifty_monthly) > 0:
            nifty_return = nifty_monthly.iloc[-1]
            print(f"📈 NIFTY 50 Return: {nifty_return:.2f}%")
            
            # Count outperformers
            outperformers = sum(1 for _, ret in investor_performance if ret > nifty_return)
            print(f"\n✅ {outperformers}/{len(investor_performance)} investors beat NIFTY 50")
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE!")
    print(f"📊 Dashboard saved: {dashboard_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
