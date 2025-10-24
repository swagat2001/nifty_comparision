"""
Enhanced Visualizer with TradingView-style Interactive Charts
- Individual investor lines with toggle
- Monthly data visualization
- Professional financial charting
- Interactive legend for filtering
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import json

# Import config
try:
    from config import OUTPUT_DIR
except:
    OUTPUT_DIR = Path(__file__).parent / 'output'
    OUTPUT_DIR.mkdir(exist_ok=True)


def create_interactive_comparison_dashboard(viz_data):
    """
    Create TradingView-style interactive dashboard with:
    - Individual investor performance lines
    - NIFTY benchmark
    - GM Fund comparisons
    - Monthly performance bars
    - Interactive legend for toggling
    """
    
    investors = viz_data['investors']
    nifty = viz_data['nifty']
    multi_cap = viz_data['multi_cap']
    mid_small = viz_data['mid_small']
    investments = viz_data['investments']
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.12,
        subplot_titles=('Cumulative Returns (%)', 'Monthly Performance (%)'),
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    # Color palette for investors (TradingView style)
    colors = [
        '#2962FF', '#00BCD4', '#00E676', '#FFD600', '#FF6D00',
        '#FF1744', '#D500F9', '#651FFF', '#00E5FF', '#76FF03',
        '#FFEA00', '#FF3D00', '#F50057', '#AA00FF', '#00B8D4',
        '#64DD17', '#FFD740', '#FF6E40', '#FF4081', '#7C4DFF',
        '#18FFFF', '#69F0AE', '#FFE57F', '#FF8A65', '#FF80AB',
        '#82B1FF', '#84FFFF', '#B2FF59', '#FFE082', '#FFAB91'
    ]
    
    # Extend colors if needed
    while len(colors) < len(investors):
        colors.extend(colors)
    
    # Add NIFTY 50 as the main benchmark (thick line)
    if len(nifty) > 0:
        fig.add_trace(
            go.Scatter(
                x=nifty.index,
                y=nifty.values,
                name='NIFTY 50',
                mode='lines',
                line=dict(color='#FF0000', width=3, dash='solid'),
                legendgroup='benchmark',
                legendgrouptitle_text='Benchmarks',
                hovertemplate='<b>NIFTY 50</b><br>Date: %{x|%b %Y}<br>Return: %{y:.2f}%<extra></extra>',
                visible=True
            ),
            row=1, col=1
        )
        
        # Add NIFTY monthly bars
        monthly_changes = nifty.diff()
        colors_bars = ['#26A69A' if x >= 0 else '#EF5350' for x in monthly_changes.values]
        
        fig.add_trace(
            go.Bar(
                x=nifty.index,
                y=monthly_changes.values,
                name='NIFTY 50 Monthly',
                marker_color=colors_bars,
                legendgroup='benchmark',
                showlegend=False,
                hovertemplate='<b>NIFTY 50</b><br>%{x|%b %Y}<br>Change: %{y:.2f}%<extra></extra>'
            ),
            row=2, col=1
        )
    
    # Add GM Multi Cap Fund
    if len(multi_cap) > 0:
        fig.add_trace(
            go.Scatter(
                x=multi_cap.index,
                y=multi_cap.values,
                name='GM Multi Cap',
                mode='lines',
                line=dict(color='#4CAF50', width=2.5, dash='dash'),
                legendgroup='funds',
                legendgrouptitle_text='Mutual Funds',
                hovertemplate='<b>GM Multi Cap</b><br>Date: %{x|%b %Y}<br>Return: %{y:.2f}%<extra></extra>',
                visible=True
            ),
            row=1, col=1
        )
    
    # Add GM Mid & Small Cap Fund
    if len(mid_small) > 0:
        fig.add_trace(
            go.Scatter(
                x=mid_small.index,
                y=mid_small.values,
                name='GM Mid & Small Cap',
                mode='lines',
                line=dict(color='#FF9800', width=2.5, dash='dot'),
                legendgroup='funds',
                hovertemplate='<b>GM Mid & Small Cap</b><br>Date: %{x|%b %Y}<br>Return: %{y:.2f}%<extra></extra>',
                visible=True
            ),
            row=1, col=1
        )
    
    # Add individual investor lines
    color_idx = 0
    for investor_name, returns in investors.items():
        if len(returns) > 0:
            # Calculate investment amount
            inv_amount = investments.get(investor_name, 0)
            
            # Add line trace
            fig.add_trace(
                go.Scatter(
                    x=returns.index,
                    y=returns.values,
                    name=f"{investor_name[:25]}",
                    mode='lines',
                    line=dict(color=colors[color_idx], width=1.5),
                    legendgroup='investors',
                    legendgrouptitle_text='Individual Investors',
                    hovertemplate=f'<b>{investor_name}</b><br>' +
                                 f'Investment: ₹{inv_amount:,.0f}<br>' +
                                 'Date: %{x|%b %Y}<br>' +
                                 'Return: %{y:.2f}%<extra></extra>',
                    visible='legendonly'  # Hidden by default to avoid clutter
                ),
                row=1, col=1
            )
            
            color_idx += 1
    
    # Calculate and add average investor line
    if len(investors) > 1:
        # Calculate average returns
        all_dates = set()
        for ret in investors.values():
            all_dates.update(ret.index)
        all_dates = sorted(all_dates)
        
        avg_returns = pd.Series(index=all_dates, dtype=float)
        for date in all_dates:
            values = []
            for ret in investors.values():
                if date in ret.index:
                    values.append(ret[date])
            if values:
                avg_returns[date] = np.mean(values)
        
        fig.add_trace(
            go.Scatter(
                x=avg_returns.index,
                y=avg_returns.values,
                name='Average Investor',
                mode='lines',
                line=dict(color='#9C27B0', width=2.5, dash='dashdot'),
                legendgroup='aggregate',
                legendgrouptitle_text='Aggregate',
                hovertemplate='<b>Average Investor</b><br>Date: %{x|%b %Y}<br>Return: %{y:.2f}%<extra></extra>',
                visible=True
            ),
            row=1, col=1
        )
    
    # Update layout with TradingView styling
        # Update layout with TradingView styling
    fig.update_layout(
        title={
            'text': '<b>Investment Portfolio Comparison Dashboard</b><br>' +
                   '<sub>Individual Investors vs NIFTY 50 vs GM Funds (Since July 2025)</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'family': 'Trebuchet MS, sans-serif'}
        },
        hovermode='x unified',
        height=900,
        template='plotly_dark',  # Dark theme like TradingView
        paper_bgcolor='#131722',
        plot_bgcolor='#131722',
        font=dict(
            family="Trebuchet MS, sans-serif",
            size=12,
            color='#787B86'
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(19, 23, 34, 0.95)",
            bordercolor="#2A2E39",
            borderwidth=1,
            font=dict(size=10, color='#D1D4DC'),
            groupclick="toggleitem",  # Enable group clicking
            tracegroupgap=10
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#2A2E39',
            showline=True,
            linewidth=1,
            linecolor='#2A2E39',
            rangeslider=dict(
                visible=False
            )
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#2A2E39',
            showline=True,
            linewidth=1,
            linecolor='#2A2E39',
            title={
                'text': '<b>Cumulative Return (%)</b>',
                'font': {'color': '#787B86'}
            }
        ),
        xaxis2=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#2A2E39'
        ),
        yaxis2=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#2A2E39',
            title={
                'text': '<b>Monthly Change (%)</b>',
                'font': {'color': '#787B86'}
            }
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(
                        args=[{"visible": [True] * len(fig.data)}],
                        label="Show All",
                        method="restyle"
                    ),
                    dict(
                        args=[{"visible": [trace.legendgroup in ['benchmark', 'funds', 'aggregate'] 
                                         for trace in fig.data]}],
                        label="Hide Individuals",
                        method="restyle"
                    ),
                    dict(
                        args=[{"visible": [trace.legendgroup == 'benchmark' 
                                         for trace in fig.data]}],
                        label="NIFTY Only",
                        method="restyle"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.01,
                xanchor="left",
                y=1.12,
                yanchor="top",
                bgcolor='#131722',
                bordercolor='#2A2E39',
                font=dict(color='#D1D4DC')
            ),
        ]
    )

    
    # Add annotations for key statistics
    if len(investors) > 0:
        # Calculate statistics
        latest_returns = {name: ret.iloc[-1] for name, ret in investors.items() if len(ret) > 0}
        
        if latest_returns:
            best_performer = max(latest_returns.items(), key=lambda x: x[1])
            worst_performer = min(latest_returns.items(), key=lambda x: x[1])
            avg_return = np.mean(list(latest_returns.values()))
            
            # Add annotation box
            annotation_text = (
                f"<b>📊 Performance Statistics</b><br>"
                f"Best: {best_performer[0][:20]} ({best_performer[1]:.1f}%)<br>"
                f"Worst: {worst_performer[0][:20]} ({worst_performer[1]:.1f}%)<br>"
                f"Average: {avg_return:.1f}%"
            )
            
            if len(nifty) > 0:
                nifty_return = nifty.iloc[-1]
                outperformers = sum(1 for ret in latest_returns.values() if ret > nifty_return)
                annotation_text += f"<br>Beat NIFTY: {outperformers}/{len(latest_returns)}"
            
            fig.add_annotation(
                text=annotation_text,
                xref="paper",
                yref="paper",
                x=0.01,
                y=0.55,
                xanchor="left",
                yanchor="top",
                showarrow=False,
                bgcolor="rgba(19, 23, 34, 0.95)",
                bordercolor="#2A2E39",
                borderwidth=1,
                font=dict(size=11, color='#D1D4DC'),
                align="left"
            )
    
    # Save the dashboard
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"interactive_dashboard_{timestamp}.html"
    filepath = OUTPUT_DIR / filename
    
    # Write HTML with custom CSS for TradingView styling
    html_string = fig.to_html(include_plotlyjs='cdn')
    
    # Add custom CSS
    custom_css = """
    <style>
        body {
            background-color: #131722;
            font-family: 'Trebuchet MS', sans-serif;
        }
        .modebar {
            background-color: rgba(19, 23, 34, 0.8) !important;
        }
        .modebar-btn path {
            fill: #787B86 !important;
        }
        .modebar-btn:hover path {
            fill: #D1D4DC !important;
        }
    </style>
    """
    
    html_string = html_string.replace('</head>', custom_css + '</head>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_string)
    
    print(f"  ✓ Dashboard saved: {filepath}")
    
    # Also save data as JSON for future reference
    json_data = {
        'timestamp': timestamp,
        'num_investors': len(investors),
        'date_range': {
            'start': 'July 2025',
            'end': datetime.now().strftime('%B %Y')
        },
        'summary': {}
    }
    
    if len(investors) > 0:
        latest_returns = {name: float(ret.iloc[-1]) for name, ret in investors.items() if len(ret) > 0}
        json_data['summary']['investor_returns'] = latest_returns
        json_data['summary']['average_return'] = float(np.mean(list(latest_returns.values())))
        
        if len(nifty) > 0:
            json_data['summary']['nifty_return'] = float(nifty.iloc[-1])
        if len(multi_cap) > 0:
            json_data['summary']['multi_cap_return'] = float(multi_cap.iloc[-1])
        if len(mid_small) > 0:
            json_data['summary']['mid_small_return'] = float(mid_small.iloc[-1])
    
    json_filepath = OUTPUT_DIR / f"dashboard_data_{timestamp}.json"
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    
    return filepath


def create_investor_ranking_chart(investors, benchmarks):
    """
    Create a bar chart showing investor performance ranking
    """
    # Prepare data
    performance_data = []
    
    for name, returns in investors.items():
        if len(returns) > 0:
            final_return = returns.iloc[-1]
            performance_data.append({
                'name': name[:30],
                'return': final_return,
                'type': 'Investor'
            })
    
    # Add benchmarks
    for bench_name, bench_returns in benchmarks.items():
        if len(bench_returns) > 0:
            performance_data.append({
                'name': bench_name,
                'return': bench_returns.iloc[-1],
                'type': 'Benchmark'
            })
    
    # Sort by return
    performance_data.sort(key=lambda x: x['return'], reverse=True)
    
    # Create bar chart
    fig = go.Figure()
    
    # Separate colors for investors and benchmarks
    colors = ['#26A69A' if d['type'] == 'Investor' else '#FF0000' 
              for d in performance_data]
    
    fig.add_trace(go.Bar(
        x=[d['return'] for d in performance_data],
        y=[d['name'] for d in performance_data],
        orientation='h',
        marker_color=colors,
        text=[f"{d['return']:.1f}%" for d in performance_data],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Return: %{x:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title='<b>Performance Ranking</b>',
        xaxis_title='Return (%)',
        yaxis_title='',
        template='plotly_dark',
        height=max(600, len(performance_data) * 25),
        paper_bgcolor='#131722',
        plot_bgcolor='#131722',
        font=dict(color='#D1D4DC'),
        xaxis=dict(gridcolor='#2A2E39'),
        yaxis=dict(gridcolor='#2A2E39')
    )
    
    # Save
    filepath = OUTPUT_DIR / f"ranking_chart_{datetime.now().strftime('%Y%m%d')}.html"
    fig.write_html(str(filepath))
    
    return filepath


if __name__ == "__main__":
    print("Enhanced Visualizer Module")
    print(f"Output directory: {OUTPUT_DIR}")
