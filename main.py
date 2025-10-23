"""
Main script - Investment Comparison with Mutual Funds
"""
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from config import INVESTMENT_DATE, OUTPUT_DIR, WEIGHTS_FILE
from data_loader import load_holdings_data, load_both_funds_from_sheet
from market_data import fetch_nifty_data
from ticker_resolver import resolve_all_tickers, save_ticker_report
from data_scraper import scrape_all_stocks, load_scraped_data, get_scraper_stats
from smart_calculator import calculate_portfolio_with_partial_data, calculate_coverage_stats, export_coverage_report
from visualizer import create_fund_comparison_chart, save_chart


def remove_timezone(series):
    """Remove timezone from pandas Series"""
    if hasattr(series.index, 'tz') and series.index.tz is not None:
        series.index = series.index.tz_localize(None)
    return series


def calculate_fund_returns(stock_data, fund_weights, fund_name):
    """Calculate returns for a mutual fund based on its weights"""
    
    if not fund_weights:
        print(f"  ⚠️  No weights for {fund_name}")
        return pd.Series()
    
    # Normalize weights to sum to 1
    total_weight = sum(fund_weights.values())
    if total_weight == 0:
        print(f"  ⚠️  Total weight is zero for {fund_name}")
        return pd.Series()
    
    normalized_weights = {k: v/total_weight for k, v in fund_weights.items()}
    
    # Get common date index from first security
    if not stock_data:
        print(f"  ⚠️  No stock data available")
        return pd.Series()
    
    first_security = list(stock_data.keys())[0]
    fund_return = pd.Series(0, index=stock_data[first_security].index)
    total_coverage = 0
    
    for security, weight in normalized_weights.items():
        if security in stock_data:
            # Align data to common index
            security_data = stock_data[security].reindex(fund_return.index, method='ffill')
            returns = security_data.pct_change().fillna(0)
            fund_return += returns * weight
            total_coverage += weight
    
    # Calculate cumulative returns
    cumulative_returns = (1 + fund_return).cumprod() - 1
    
    coverage_pct = total_coverage * 100
    
    print(f"  {fund_name}: {coverage_pct:.1f}% coverage")
    
    return cumulative_returns


def main():
    print("=" * 80)
    print("INVESTMENT COMPARISON ANALYSIS - WITH MUTUAL FUNDS")
    print("=" * 80)
    
    # Step 1: Load holdings data
    print("\nStep 1: Loading holdings data...")
    holdings_df = load_holdings_data()
    if holdings_df is None or len(holdings_df) == 0:
        print("\n❌ No holdings data loaded")
        return
    
    # Step 2: Load fund weights (both from same sheet)
    print("\nStep 2: Loading mutual fund weights...")
    multi_cap_weights, mid_small_weights = load_both_funds_from_sheet(WEIGHTS_FILE)
    
    # Step 3: Create combined securities DataFrame for resolve_all_tickers
    print(f"\nStep 3: Resolving tickers...")
    
    # Get all unique securities (from holdings + funds)
    all_securities = list(holdings_df['Security Name'].unique())
    all_securities.extend(multi_cap_weights.keys())
    all_securities.extend(mid_small_weights.keys())
    
    # Remove duplicates
    all_securities = list(set(all_securities))
    
    # Create a temporary DataFrame for resolve_all_tickers
    temp_df = pd.DataFrame({'Security Name': all_securities})
    
    success_map, failed_list = resolve_all_tickers(temp_df, INVESTMENT_DATE)
    
    print(f"\n  ✅ Success: {len(success_map)}/{len(all_securities)}")
    print(f"  ❌ Failed:  {len(failed_list)}/{len(all_securities)}")
    
    save_ticker_report(success_map, failed_list)
    
    # Step 4: Fetch/Load Stock Data
    print("\nStep 4: Stock data acquisition...")
    
    scraper_stats = get_scraper_stats()
    
    if scraper_stats['total_downloaded'] > 0:
        print(f"  Found {scraper_stats['total_downloaded']} scraped securities")
        print(f"  Last scraped: {scraper_stats['last_run']}")
        stock_data = load_scraped_data()
    else:
        print("  No scraped data found. Downloading now...")
        scrape_all_stocks(success_map, INVESTMENT_DATE)
        stock_data = load_scraped_data()
    
    if len(stock_data) == 0:
        print("\n❌ No stock data available")
        return
    
    print(f"  ✓ Loaded {len(stock_data)} securities")
    
    # Step 5: Calculate portfolio returns
    print(f"\nStep 5: Calculating returns...")
    
    # Get all dates from stock data
    all_dates = set()
    for data in stock_data.values():
        all_dates.update(data.index)
    all_dates = sorted(all_dates)
    
    if not all_dates:
        print("\n❌ No dates in stock data")
        return
    
    # Actual investor portfolio
    investor_portfolios = calculate_portfolio_with_partial_data(
        holdings_df, 
        stock_data, 
        all_dates
    )
    
    # Combine all investor portfolios into one (if multiple investors)
    if len(investor_portfolios) == 0:
        print("\n❌ No portfolio data calculated")
        return
    
    # If multiple investors, combine them
    if len(investor_portfolios) > 1:
        investor_returns = pd.Series(0, index=all_dates)
        for portfolio in investor_portfolios.values():
            investor_returns += portfolio
        # Calculate returns
        investor_returns = (investor_returns / investor_returns.iloc[0]) - 1
    else:
        # Single investor
        portfolio = list(investor_portfolios.values())[0]
        investor_returns = (portfolio / portfolio.iloc[0]) - 1
    
    print(f"  ✓ Investor Portfolio calculated")
    
    # GM Multi Cap Fund
    multi_cap_returns = calculate_fund_returns(
        stock_data,
        multi_cap_weights,
        "GM Multi Cap Fund"
    )
    
    # GM Mid & Small Cap Fund
    mid_small_returns = calculate_fund_returns(
        stock_data,
        mid_small_weights,
        "GM Mid & Small Cap Fund"
    )
    
    # Step 6: Fetch NIFTY 50 data
    print(f"\nStep 6: Fetching NIFTY 50 data...")
    nifty_data_dict = fetch_nifty_data(INVESTMENT_DATE)
    
    if not nifty_data_dict or 'NIFTY 50' not in nifty_data_dict:
        print("  ⚠️  Could not fetch NIFTY data")
        nifty_returns = pd.Series(0, index=investor_returns.index)
    else:
        # Get NIFTY 50 data (it's a dict with 'NIFTY 50' key)
        nifty_data = nifty_data_dict['NIFTY 50']
        
        # Remove timezone if present
        nifty_data = remove_timezone(nifty_data)
        
        # Calculate NIFTY returns
        nifty_returns = nifty_data.pct_change().fillna(0)
        nifty_cumulative = (1 + nifty_returns).cumprod() - 1
        
        # Align dates
        nifty_returns = nifty_cumulative.reindex(investor_returns.index, method='ffill').fillna(0)
        print(f"  ✓ NIFTY 50 data loaded")
    
    # Step 7: Create visualization
    print(f"\nStep 7: Creating visualization...")
    
    # Handle empty fund returns
    if len(multi_cap_returns) == 0:
        multi_cap_returns = pd.Series(0, index=investor_returns.index)
    if len(mid_small_returns) == 0:
        mid_small_returns = pd.Series(0, index=investor_returns.index)
    
    fig = create_fund_comparison_chart(
        investor_returns=investor_returns,
        nifty_returns=nifty_returns,
        multi_cap_returns=multi_cap_returns,
        mid_small_returns=mid_small_returns,
        investor_name="Investor Portfolio"
    )
    
    filename = f"investment_comparison_{datetime.now().strftime('%Y%m%d')}.html"
    save_chart(fig, filename)
    
    # Step 8: Print summary
    print(f"\nStep 8: Analysis Summary")
    print("=" * 80)
    
    final_returns = {
        'Investor Portfolio': investor_returns.iloc[-1] * 100 if len(investor_returns) > 0 else 0,
        'NIFTY 50': nifty_returns.iloc[-1] * 100 if len(nifty_returns) > 0 else 0,
        'GM Multi Cap Fund': multi_cap_returns.iloc[-1] * 100 if len(multi_cap_returns) > 0 else 0,
        'GM Mid & Small Cap Fund': mid_small_returns.iloc[-1] * 100 if len(mid_small_returns) > 0 else 0,
    }
    
    print("\n📊 FINAL RETURNS:")
    for name, ret in final_returns.items():
        print(f"  {name:30s}: {ret:>8.2f}%")
    
    # Show best performer
    best = max(final_returns.items(), key=lambda x: x[1])
    print(f"\n🏆 Best Performer: {best[0]} ({best[1]:.2f}%)")
    
    # Calculate coverage
    cov_stats = calculate_coverage_stats(holdings_df, stock_data)
    print(f"\n📈 Portfolio Coverage:")
    print(f"  Total investors: {len(cov_stats)}")
    print(f"  Average coverage: {cov_stats['Coverage %'].mean():.1f}%")
    
    # Export full report
    import os
    os.makedirs('reports/ticker_reports', exist_ok=True)
    export_coverage_report(cov_stats, 'reports/ticker_reports/coverage_report.csv')
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\n📁 Output folder: output/")
    print(f"📊 Chart: {filename}")
    print(f"📄 Reports: reports/ticker_reports/")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
