"""
Main script - REAL DATA with Smart Ticker Resolution
"""
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from config import INVESTMENT_DATE, OUTPUT_DIR
from data_loader import load_holdings_data
from market_data import fetch_nifty_data
from ticker_resolver import resolve_all_tickers, save_ticker_report
from data_scraper import scrape_all_stocks, load_scraped_data, get_scraper_stats
from smart_calculator import calculate_portfolio_with_partial_data, calculate_coverage_stats, export_coverage_report
from visualizer import create_comparison_chart, create_multi_investor_dashboard, save_chart


def main():
    print("=" * 80)
    print("INVESTMENT COMPARISON ANALYSIS - REAL DATA")
    print("=" * 80)
    print()
    
    # Step 1: Load Holdings
    print("Step 1: Loading holdings data...")
    holdings_df = load_holdings_data()
    print(f"✓ Loaded {len(holdings_df)} holdings")
    print(f"✓ Found {holdings_df['NAME'].nunique()} investors")
    
    # Step 2: Resolve Tickers (Smart Detection)
    print("\nStep 2: Resolving stock tickers...")
    success_map, failed_list = resolve_all_tickers(holdings_df, INVESTMENT_DATE)
    
    # Save report
    save_ticker_report(success_map, failed_list)
    
    if len(success_map) == 0:
        print("\n❌ No tickers could be resolved. Please check the report.")
        return
    
    # Step 3: Fetch/Load Stock Data
    print("\nStep 3: Stock data acquisition...")
    
    # Check if we have scraped data
    scraper_stats = get_scraper_stats()
    
    if scraper_stats['total_downloaded'] > 0:
        # Load from scraped data
        print(f"  Found {scraper_stats['total_downloaded']} scraped securities")
        print(f"  Last scraped: {scraper_stats['last_run']}")
        stock_data = load_scraped_data()
    else:
        # Need to scrape first
        print("  No scraped data found. Downloading now...")
        scrape_all_stocks(success_map, INVESTMENT_DATE)
        stock_data = load_scraped_data()
    
    if len(stock_data) == 0:
        print("\n❌ No stock data available")
        return
    
    # Step 4: Fetch NIFTY Data
    print("\nStep 4: Fetching NIFTY indices...")
    nifty_data = fetch_nifty_data(INVESTMENT_DATE)
    
    # Step 5: Calculate Smart Portfolio Values
    print("\nStep 5: Calculating portfolio values (smart estimation)...")
    dates = pd.date_range(start=INVESTMENT_DATE, end=datetime.now(), freq='ME')
    
    # Calculate using smart method (partial data + estimation)
    investor_portfolios = calculate_portfolio_with_partial_data(holdings_df, stock_data, dates)
    print(f"✓ Calculated for {len(investor_portfolios)} investors")
    
    # Generate coverage report
    coverage_df = calculate_coverage_stats(holdings_df, stock_data)
    export_coverage_report(coverage_df)
    
    # Step 6: Prepare Comparison Data
    print("\nStep 6: Preparing comparison data...")
    investors_chart_data = {}
    
    for investor_name, portfolio_values in investor_portfolios.items():
        if len(portfolio_values) == 0 or portfolio_values.sum() == 0:
            continue
        
        initial_investment = portfolio_values.iloc[0]
        current_value = portfolio_values.iloc[-1]
        
        if initial_investment == 0:
            continue
        
        monthly_data = {}
        monthly_data['Actual Portfolio'] = portfolio_values
        
        # Add NIFTY comparisons
        for index_name, nifty_prices in nifty_data.items():
            if len(nifty_prices) > 0:
                if hasattr(nifty_prices.index, 'tz'):
                    nifty_prices = nifty_prices.tz_localize(None)
                
                aligned = nifty_prices.reindex(dates, method='ffill')
                units = initial_investment / aligned.iloc[0]
                nifty_values = aligned * units
                monthly_data[index_name] = nifty_values
        
        investors_chart_data[investor_name] = {
            'initial_investment': initial_investment,
            'current_value': current_value,
            'monthly_data': monthly_data
        }
    
    print(f"✓ Prepared {len(investors_chart_data)} investors")
    
    if len(investors_chart_data) == 0:
        print("\n❌ No investor data could be prepared.")
        return
    
    # Step 7: Create Visualizations
    print("\nStep 7: Creating visualizations...")
    
    # Sort by investment size
    sorted_investors = sorted(
        investors_chart_data.items(),
        key=lambda x: x[1]['initial_investment'],
        reverse=True
    )
    
    # Top 5 individual charts
    for idx, (investor_name, data) in enumerate(sorted_investors[:5], 1):
        fig = create_comparison_chart(
            investor_name,
            data['initial_investment'],
            data['monthly_data']
        )
        filename = f"comparison_{investor_name.replace(' ', '_')}.html"
        save_chart(fig, filename)
    
    print(f"✓ Created {min(5, len(sorted_investors))} individual charts")
    
    # Dashboard
    dashboard_fig = create_multi_investor_dashboard(investors_chart_data)
    save_chart(dashboard_fig, "investment_comparison_dashboard.html")
    print("✓ Dashboard created")
    
    # Summary
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    total_current = sum(d['current_value'] for d in investors_chart_data.values())
    total_initial = sum(d['initial_investment'] for d in investors_chart_data.values())
    
    print(f"\nData Coverage:")
    print(f"  Tickers resolved:     {len(success_map)}/{len(holdings_df['Security Name'].unique())}")
    print(f"  Tickers with data:    {len(stock_data)}/{len(success_map)}")
    print(f"  Avg portfolio coverage: {coverage_df['Coverage %'].mean():.1f}%")
    print(f"  Investors >50% coverage: {len(coverage_df[coverage_df['Coverage %'] > 50])}/{len(coverage_df)}")
    
    print(f"\nInvestment Summary:")
    print(f"  Total Investors:      {len(investors_chart_data)}")
    print(f"  Total Current Value:  ₹{total_current:,.2f}")
    print(f"  Total Initial:        ₹{total_initial:,.2f}")
    print(f"  Overall Return:       {((total_current/total_initial - 1) * 100):.2f}%")
    
    print(f"\nOutput:")
    print(f"  Charts: {OUTPUT_DIR}")
    print(f"  Reports: ticker_reports/")
    print(f"    - successful_tickers.csv")
    print(f"    - failed_tickers.csv")
    print(f"    - coverage_report.csv")
    
    if len(failed_list) > 0:
        print(f"\n⚠ Warning: {len(failed_list)} securities without tickers")
        print(f"  Missing data is estimated using tracked holdings growth")
        print(f"  Run manual_mapper.py to find more tickers")
    
    print()


if __name__ == "__main__":
    main()
