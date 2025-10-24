"""
Monthly Performance Analyzer
Tracks monthly rises and falls for each investor
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import json


def calculate_monthly_performance(portfolio_series, start_date='2024-04-01'):
    """
    Calculate month-by-month performance metrics
    
    Args:
        portfolio_series: Time series of portfolio values
        start_date: Investment start date
        
    Returns:
        DataFrame with monthly performance metrics
    """
    # Ensure datetime index
    if not isinstance(portfolio_series.index, pd.DatetimeIndex):
        portfolio_series.index = pd.to_datetime(portfolio_series.index)
    
    # Filter from start date
    start_dt = pd.to_datetime(start_date)
    portfolio_series = portfolio_series[portfolio_series.index >= start_dt]
    
    if len(portfolio_series) == 0:
        return pd.DataFrame()
    
    # Resample to monthly (last business day)
    monthly = portfolio_series.resample('M').last()
    
    # Calculate metrics
    metrics = pd.DataFrame(index=monthly.index)
    
    # Portfolio value
    metrics['Portfolio_Value'] = monthly.values
    
    # Monthly returns (percentage)
    metrics['Monthly_Return'] = monthly.pct_change() * 100
    
    # Cumulative returns from start
    initial_value = portfolio_series.iloc[0]
    if initial_value != 0:
        metrics['Cumulative_Return'] = ((monthly / initial_value) - 1) * 100
    else:
        metrics['Cumulative_Return'] = 0
    
    # Month-over-month change in value
    metrics['Value_Change'] = monthly.diff()
    
    # Identify rise or fall
    metrics['Direction'] = metrics['Monthly_Return'].apply(
        lambda x: 'Rise' if x > 0 else ('Fall' if x < 0 else 'Flat')
    )
    
    # Calculate volatility (rolling 3-month)
    metrics['Volatility_3M'] = metrics['Monthly_Return'].rolling(window=3).std()
    
    # Calculate drawdown from peak
    cumulative_max = monthly.cummax()
    drawdown = (monthly - cumulative_max) / cumulative_max * 100
    metrics['Drawdown'] = drawdown
    
    # Add month name for readability
    metrics['Month_Name'] = metrics.index.strftime('%B %Y')
    
    return metrics


def analyze_all_investors(investor_portfolios, start_date='2024-04-01'):
    """
    Analyze monthly performance for all investors
    
    Args:
        investor_portfolios: Dict of investor_name -> portfolio series
        start_date: Investment start date
        
    Returns:
        Dict of investor_name -> monthly performance DataFrame
    """
    print("\n📊 Analyzing Monthly Performance:")
    print("-" * 50)
    
    monthly_performance = {}
    
    for investor_name, portfolio in investor_portfolios.items():
        metrics = calculate_monthly_performance(portfolio, start_date)
        
        if len(metrics) > 0:
            monthly_performance[investor_name] = metrics
            
            # Print summary
            total_months = len(metrics)
            rise_months = (metrics['Direction'] == 'Rise').sum()
            fall_months = (metrics['Direction'] == 'Fall').sum()
            avg_monthly_return = metrics['Monthly_Return'].mean()
            max_return = metrics['Monthly_Return'].max()
            min_return = metrics['Monthly_Return'].min()
            current_return = metrics['Cumulative_Return'].iloc[-1]
            
            print(f"\n{investor_name}:")
            print(f"  Months analyzed: {total_months}")
            print(f"  Rising months: {rise_months} ({rise_months/total_months*100:.1f}%)")
            print(f"  Falling months: {fall_months} ({fall_months/total_months*100:.1f}%)")
            print(f"  Avg monthly return: {avg_monthly_return:.2f}%")
            print(f"  Best month: {max_return:.2f}%")
            print(f"  Worst month: {min_return:.2f}%")
            print(f"  Current return: {current_return:.2f}%")
    
    return monthly_performance


def compare_with_benchmarks(investor_performance, benchmark_performance):
    """
    Compare investor performance with benchmarks
    
    Args:
        investor_performance: Dict of investor monthly performance
        benchmark_performance: Dict of benchmark monthly performance
        
    Returns:
        DataFrame with comparison metrics
    """
    comparison_data = []
    
    # Get common months
    all_months = set()
    for perf in investor_performance.values():
        all_months.update(perf.index)
    for perf in benchmark_performance.values():
        all_months.update(perf.index)
    
    if not all_months:
        return pd.DataFrame()
    
    common_months = sorted(all_months)
    
    # Calculate comparison metrics
    for investor_name, investor_metrics in investor_performance.items():
        for benchmark_name, benchmark_metrics in benchmark_performance.items():
            # Align data to common months
            investor_returns = investor_metrics.reindex(common_months)['Cumulative_Return'].fillna(0)
            benchmark_returns = benchmark_metrics.reindex(common_months)['Cumulative_Return'].fillna(0)
            
            # Calculate alpha (excess return)
            alpha = investor_returns - benchmark_returns
            
            # Count outperformance months
            outperform_months = (alpha > 0).sum()
            total_months = len(common_months)
            
            comparison_data.append({
                'Investor': investor_name,
                'Benchmark': benchmark_name,
                'Final_Investor_Return': investor_returns.iloc[-1] if len(investor_returns) > 0 else 0,
                'Final_Benchmark_Return': benchmark_returns.iloc[-1] if len(benchmark_returns) > 0 else 0,
                'Alpha': alpha.iloc[-1] if len(alpha) > 0 else 0,
                'Outperform_Months': outperform_months,
                'Total_Months': total_months,
                'Outperform_Rate': outperform_months / total_months * 100 if total_months > 0 else 0,
                'Avg_Monthly_Alpha': alpha.mean() if len(alpha) > 0 else 0
            })
    
    return pd.DataFrame(comparison_data)


def generate_monthly_report(monthly_performance, comparison_df, output_dir='reports'):
    """
    Generate comprehensive monthly performance report
    
    Args:
        monthly_performance: Dict of monthly performance data
        comparison_df: Comparison with benchmarks
        output_dir: Output directory
    """
    output_path = Path(output_dir) / 'monthly_reports'
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = output_path / f'monthly_performance_{timestamp}.xlsx'
    
    # Create Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Write comparison summary first
        if not comparison_df.empty:
            comparison_df.to_excel(writer, sheet_name='Benchmark Comparison', index=False)
        
        # Write individual investor monthly data
        for investor_name, metrics in monthly_performance.items():
            # Sanitize sheet name (Excel has 31 char limit)
            sheet_name = investor_name[:31] if len(investor_name) > 31 else investor_name
            metrics.to_excel(writer, sheet_name=sheet_name)
        
        # Create summary sheet
        summary_data = []
        for investor_name, metrics in monthly_performance.items():
            if len(metrics) > 0:
                summary_data.append({
                    'Investor': investor_name,
                    'Total_Months': len(metrics),
                    'Rising_Months': (metrics['Direction'] == 'Rise').sum(),
                    'Falling_Months': (metrics['Direction'] == 'Fall').sum(),
                    'Flat_Months': (metrics['Direction'] == 'Flat').sum(),
                    'Avg_Monthly_Return': metrics['Monthly_Return'].mean(),
                    'Best_Month': metrics['Monthly_Return'].max(),
                    'Worst_Month': metrics['Monthly_Return'].min(),
                    'Current_Return': metrics['Cumulative_Return'].iloc[-1],
                    'Max_Drawdown': metrics['Drawdown'].min(),
                    'Avg_Volatility': metrics['Volatility_3M'].mean()
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\n📄 Monthly performance report saved: {filename}")
    
    # Also save key metrics as JSON
    json_filename = output_path / f'monthly_metrics_{timestamp}.json'
    
    json_data = {
        'timestamp': timestamp,
        'num_investors': len(monthly_performance),
        'analysis_period': {
            'start': 'April 2024',
            'end': datetime.now().strftime('%B %Y')
        },
        'summary': summary_df.to_dict('records') if not summary_df.empty else [],
        'benchmark_comparison': comparison_df.to_dict('records') if not comparison_df.empty else []
    }
    
    # Add best/worst performing months across all investors
    all_monthly_returns = []
    for metrics in monthly_performance.values():
        if 'Monthly_Return' in metrics.columns:
            for month, ret in metrics['Monthly_Return'].items():
                if not pd.isna(ret):
                    all_monthly_returns.append({
                        'month': month.strftime('%B %Y'),
                        'return': float(ret)
                    })
    
    if all_monthly_returns:
        all_monthly_returns.sort(key=lambda x: x['return'], reverse=True)
        json_data['best_months'] = all_monthly_returns[:5]
        json_data['worst_months'] = all_monthly_returns[-5:]
    
    with open(json_filename, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)
    
    print(f"📄 Monthly metrics JSON saved: {json_filename}")
    
    return filename


def create_monthly_heatmap_data(monthly_performance):
    """
    Create data structure for monthly performance heatmap
    
    Args:
        monthly_performance: Dict of monthly performance data
        
    Returns:
        DataFrame suitable for heatmap visualization
    """
    # Create a matrix: investors x months
    all_months = set()
    for metrics in monthly_performance.values():
        all_months.update(metrics.index)
    
    if not all_months:
        return pd.DataFrame()
    
    months = sorted(all_months)
    
    # Create matrix
    heatmap_data = pd.DataFrame(index=list(monthly_performance.keys()), 
                                columns=[m.strftime('%b %Y') for m in months])
    
    for investor_name, metrics in monthly_performance.items():
        for month in months:
            if month in metrics.index:
                # Use monthly return for heatmap
                heatmap_data.loc[investor_name, month.strftime('%b %Y')] = \
                    metrics.loc[month, 'Monthly_Return']
    
    # Convert to float
    heatmap_data = heatmap_data.astype(float)
    
    return heatmap_data


if __name__ == "__main__":
    print("Monthly Performance Analyzer Module")
    print("Tracks monthly rises and falls for each investor")
