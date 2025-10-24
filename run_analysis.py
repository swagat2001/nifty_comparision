"""
Run Complete Investment Analysis
This script runs the complete enhanced analysis with all features:
- Individual investor tracking
- Monthly performance analysis  
- Investment value calculations
- Interactive TradingView-style charts
- Comprehensive reporting
"""

import sys
import warnings
warnings.filterwarnings('ignore')

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Import all modules
from config import INVESTMENT_DATE, OUTPUT_DIR, HOLDINGS_FILE, WEIGHTS_FILE
from data_loader import load_holdings_data, load_both_funds_from_sheet
from market_data import fetch_nifty_data
from ticker_resolver import resolve_all_tickers
from nse_data_loader import load_all_nse_data
from investment_calculator import (
    calculate_investment_values,
    calculate_investor_wise_investments,
    export_investment_report
)
from monthly_analyzer import (
    analyze_all_investors,
    compare_with_benchmarks,
    generate_monthly_report,
    create_monthly_heatmap_data
)
from enhanced_main import (
    calculate_investor_portfolios,
    calculate_fund_portfolio,
    calculate_monthly_returns
)
from enhanced_visualizer import (
    create_interactive_comparison_dashboard,
    create_investor_ranking_chart
)


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def main():
    """Run complete analysis"""
    
    print_header("COMPREHENSIVE INVESTMENT ANALYSIS SYSTEM")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Investment Start Date: {INVESTMENT_DATE}")
    
    try:
        # ============================================================
        # STEP 1: Load Data
        # ============================================================
        print_header("STEP 1: Loading Data Files")
        
        # Load holdings
        print("\n📁 Loading holdings data...")
        holdings_df = load_holdings_data()
        if holdings_df is None or len(holdings_df) == 0:
            print("❌ ERROR: No holdings data loaded")
            return 1
        
        # Check for multiple investors
        has_multiple_investors = 'NAME' in holdings_df.columns
        if has_multiple_investors:
            num_investors = holdings_df['NAME'].nunique()
            print(f"  ✓ Found {num_investors} individual investors")
            investor_names = holdings_df['NAME'].unique()[:5]
            print(f"  ✓ Sample investors: {', '.join([str(n) for n in investor_names if pd.notna(n)])}")
        else:
            print("  ✓ Processing as single portfolio")
        
        # Load fund weights
        print("\n📁 Loading mutual fund weights...")
        multi_cap_weights, mid_small_weights = load_both_funds_from_sheet(WEIGHTS_FILE)
        print(f"  ✓ GM Multi Cap: {len(multi_cap_weights)} securities")
        print(f"  ✓ GM Mid & Small Cap: {len(mid_small_weights)} securities")
        
        # ============================================================
        # STEP 2: Resolve Tickers
        # ============================================================
        print_header("STEP 2: Resolving Security Tickers")
        
        # Combine all securities
        all_securities = list(holdings_df['Security Name'].unique())
        all_securities.extend(multi_cap_weights.keys())
        all_securities.extend(mid_small_weights.keys())
        all_securities = list(set(all_securities))
        
        print(f"  Total unique securities: {len(all_securities)}")
        
        # Resolve tickers
        temp_df = pd.DataFrame({'Security Name': all_securities})
        success_map, failed_list = resolve_all_tickers(temp_df, INVESTMENT_DATE)
        
        success_rate = len(success_map) / len(all_securities) * 100
        print(f"\n  ✅ Successfully resolved: {len(success_map)}/{len(all_securities)} ({success_rate:.1f}%)")
        print(f"  ❌ Failed to resolve: {len(failed_list)}/{len(all_securities)}")
        
        if len(failed_list) > 0:
            print(f"  Failed securities (first 5): {failed_list[:5]}")
        
        # ============================================================
        # STEP 3: Load Stock Data
        # ============================================================
        print_header("STEP 3: Loading Stock Price Data")
        
        stock_data = load_all_nse_data(success_map, INVESTMENT_DATE)
        
        if len(stock_data) == 0:
            print("❌ ERROR: No stock data available")
            return 1
        
        print(f"  ✓ Loaded price data for {len(stock_data)} securities")
        
        # Check data quality
        data_points = sum(len(series) for series in stock_data.values())
        avg_points = data_points / len(stock_data)
        print(f"  ✓ Total data points: {data_points:,}")
        print(f"  ✓ Average points per security: {avg_points:.0f}")
        
        # ============================================================
        # STEP 4: Calculate Investment Values
        # ============================================================
        print_header("STEP 4: Calculating Investment Values (April 2024)")
        
        # Calculate investment values
        investment_df = calculate_investment_values(holdings_df, stock_data, INVESTMENT_DATE)
        
        # Get investor-wise summary
        investor_summary = calculate_investor_wise_investments(investment_df)
        
        print(f"\n📊 Investment Summary:")
        print(f"  Number of investors: {len(investor_summary)}")
        print(f"  Total investment: ₹{investor_summary['Investment_April_2024'].sum():,.0f}")
        print(f"  Current value: ₹{investor_summary['Current_Value'].sum():,.0f}")
        
        # Export investment report
        investment_report_file = export_investment_report(
            investment_df, investor_summary, 'reports'
        )
        
        # ============================================================
        # STEP 5: Calculate Portfolio Performance
        # ============================================================
        print_header("STEP 5: Calculating Portfolio Performance")
        
        # Calculate portfolio values over time
        investor_portfolios = calculate_investor_portfolios(
            holdings_df, stock_data, INVESTMENT_DATE
        )
        
        print(f"  ✓ Calculated {len(investor_portfolios)} portfolio(s)")
        
        # ============================================================
        # STEP 6: Monthly Performance Analysis
        # ============================================================
        print_header("STEP 6: Analyzing Monthly Performance")
        
        # Analyze monthly performance
        monthly_performance = analyze_all_investors(investor_portfolios, INVESTMENT_DATE)
        
        # Calculate monthly returns for visualization
        monthly_returns = {}
        for investor_name, portfolio_series in investor_portfolios.items():
            monthly_ret = calculate_monthly_returns(portfolio_series, INVESTMENT_DATE)
            if len(monthly_ret) > 0:
                monthly_returns[investor_name] = monthly_ret
        
        # ============================================================
        # STEP 7: Benchmark Comparison
        # ============================================================
        print_header("STEP 7: Loading Benchmark Data")
        
        # Fetch NIFTY data
        print("\n📈 Fetching NIFTY 50 data...")
        nifty_data_dict = fetch_nifty_data(INVESTMENT_DATE)
        
        nifty_monthly = pd.Series()
        if nifty_data_dict and 'NIFTY 50' in nifty_data_dict:
            nifty_series = nifty_data_dict['NIFTY 50']
            nifty_monthly = calculate_monthly_returns(nifty_series, INVESTMENT_DATE)
            print(f"  ✓ NIFTY 50 data loaded: {len(nifty_monthly)} months")
        
        # Calculate fund performance
        print("\n📈 Calculating fund portfolio performance...")
        
        # Use total investment for fund calculations
        total_investment = investor_summary['Investment_April_2024'].sum()
        
        # GM Multi Cap
        multi_cap_portfolio = calculate_fund_portfolio(
            stock_data, multi_cap_weights, total_investment, INVESTMENT_DATE
        )
        multi_cap_monthly = calculate_monthly_returns(multi_cap_portfolio, INVESTMENT_DATE)
        
        # GM Mid & Small Cap
        mid_small_portfolio = calculate_fund_portfolio(
            stock_data, mid_small_weights, total_investment, INVESTMENT_DATE
        )
        mid_small_monthly = calculate_monthly_returns(mid_small_portfolio, INVESTMENT_DATE)
        
        print(f"  ✓ GM Multi Cap: {len(multi_cap_monthly)} months")
        print(f"  ✓ GM Mid & Small Cap: {len(mid_small_monthly)} months")
        
        # Compare with benchmarks
        benchmark_performance = {
            'NIFTY 50': nifty_monthly,
            'GM Multi Cap': multi_cap_monthly,
            'GM Mid & Small Cap': mid_small_monthly
        }
        
        # Remove empty benchmarks
        benchmark_performance = {k: v for k, v in benchmark_performance.items() if len(v) > 0}
        
        comparison_df = compare_with_benchmarks(monthly_performance, benchmark_performance)
        
        # Generate monthly report
        monthly_report_file = generate_monthly_report(
            monthly_performance, comparison_df, 'reports'
        )
        
        # ============================================================
        # STEP 8: Create Visualizations
        # ============================================================
        print_header("STEP 8: Creating Interactive Visualizations")
        
        # Prepare visualization data
        viz_data = {
            'investors': monthly_returns,
            'nifty': nifty_monthly,
            'multi_cap': multi_cap_monthly,
            'mid_small': mid_small_monthly,
            'investments': {name: row['Investment_April_2024'] 
                          for _, row in investor_summary.iterrows()
                          for name in [row['Investor']]}
        }
        
        # Create main dashboard
        dashboard_file = create_interactive_comparison_dashboard(viz_data)
        
        # Create ranking chart
        all_returns = monthly_returns.copy()
        all_returns.update(benchmark_performance)
        ranking_file = create_investor_ranking_chart(monthly_returns, benchmark_performance)
        
        # ============================================================
        # STEP 9: Final Summary
        # ============================================================
        print_header("ANALYSIS COMPLETE - SUMMARY")
        
        if len(monthly_returns) > 0:
            # Performance statistics
            latest_month = max([ret.index[-1] for ret in monthly_returns.values()])
            
            print(f"\n📊 Performance as of {latest_month.strftime('%B %Y')}:")
            print("-" * 50)
            
            # Get final returns
            investor_final_returns = []
            for name, returns in monthly_returns.items():
                if len(returns) > 0:
                    final_return = returns.iloc[-1]
                    investor_final_returns.append((name, final_return))
            
            # Sort by performance
            investor_final_returns.sort(key=lambda x: x[1], reverse=True)
            
            # Show top performers
            print("\n🏆 Top 5 Performers:")
            for i, (name, ret) in enumerate(investor_final_returns[:5], 1):
                print(f"  {i}. {name[:30]:30s}: {ret:>8.2f}%")
            
            # Show bottom performers
            if len(investor_final_returns) > 5:
                print("\n📉 Bottom 5 Performers:")
                for i, (name, ret) in enumerate(investor_final_returns[-5:], 1):
                    print(f"  {i}. {name[:30]:30s}: {ret:>8.2f}%")
            
            # Statistics
            returns_values = [ret for _, ret in investor_final_returns]
            print(f"\n📊 Overall Statistics:")
            print(f"  Average Return: {np.mean(returns_values):.2f}%")
            print(f"  Median Return: {np.median(returns_values):.2f}%")
            print(f"  Best Return: {max(returns_values):.2f}%")
            print(f"  Worst Return: {min(returns_values):.2f}%")
            
            # Benchmark comparison
            if len(nifty_monthly) > 0:
                nifty_return = nifty_monthly.iloc[-1]
                print(f"\n📈 Benchmark Returns:")
                print(f"  NIFTY 50: {nifty_return:.2f}%")
                
                # Count outperformers
                outperformers = sum(1 for _, ret in investor_final_returns if ret > nifty_return)
                pct_outperform = outperformers / len(investor_final_returns) * 100
                print(f"\n  ✓ {outperformers}/{len(investor_final_returns)} investors beat NIFTY 50 ({pct_outperform:.1f}%)")
            
            if len(multi_cap_monthly) > 0:
                print(f"  GM Multi Cap: {multi_cap_monthly.iloc[-1]:.2f}%")
            
            if len(mid_small_monthly) > 0:
                print(f"  GM Mid & Small Cap: {mid_small_monthly.iloc[-1]:.2f}%")
        
        # Output files summary
        print_header("OUTPUT FILES GENERATED")
        
        print(f"\n📁 Reports Directory: reports/")
        print(f"  📄 Investment Report: {investment_report_file}")
        print(f"  📄 Monthly Report: {monthly_report_file}")
        
        print(f"\n📁 Visualizations Directory: {OUTPUT_DIR}/")
        print(f"  📊 Interactive Dashboard: {dashboard_file}")
        print(f"  📊 Performance Ranking: {ranking_file}")
        
        print("\n" + "=" * 80)
        print("  ✅ ANALYSIS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nOpen the interactive dashboard in your browser to explore the results.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
