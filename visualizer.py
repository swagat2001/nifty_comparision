"""
Module for creating interactive visualizations using Plotly
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os
from config import OUTPUT_DIR, GRAPH_FILE


def create_comparison_chart(investor_name, initial_investment, monthly_data):
    """
    Create an interactive comparison chart for a single investor
    
    Args:
        investor_name: Name of the investor
        initial_investment: Initial investment amount
        monthly_data: Dictionary with monthly portfolio values for different strategies
        
    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    # Define colors for different strategies
    colors = {
        'Actual Portfolio': '#1f77b4',
        'NIFTY 50': '#ff7f0e',
        'NIFTY Small Cap 250': '#2ca02c',
        'NIFTY Mid Cap 150': '#d62728',
        'NIFTY Large Cap': '#9467bd',
        'GM Multi Cap': '#8c564b',
        'GM Mid & Small Cap': '#e377c2'
    }
    
    # Add traces for each investment strategy
    for strategy_name, values in monthly_data.items():
        if isinstance(values, pd.Series) and len(values) > 0:
            fig.add_trace(go.Scatter(
                x=values.index,
                y=values.values,
                mode='lines+markers',
                name=strategy_name,
                line=dict(width=2, color=colors.get(strategy_name, '#000000')),
                marker=dict(size=6),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Date: %{x|%b %Y}<br>' +
                             'Value: ₹%{y:,.2f}<br>' +
                             '<extra></extra>',
                visible=True
            ))
    
    # Update layout with TradingView-style theme
    fig.update_layout(
        title={
            'text': f'Investment Comparison - {investor_name}<br>' +
                   f'<sub>Initial Investment: ₹{initial_investment:,.2f} (April 2024)</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial, sans-serif'}
        },
        xaxis=dict(
            title='Date',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128, 128, 128, 0.5)',
            mirror=True,
            tickformat='%b %Y'
        ),
        yaxis=dict(
            title='Portfolio Value (₹)',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128, 128, 128, 0.5)',
            mirror=True,
            tickformat=',.0f'
        ),
        hovermode='x unified',
        plot_bgcolor='#ffffff',
        paper_bgcolor='#f5f5f5',
        font=dict(family='Arial, sans-serif', size=12),
        legend=dict(
            orientation='v',
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(128, 128, 128, 0.5)',
            borderwidth=1,
            font=dict(size=11)
        ),
        height=600,
        margin=dict(l=80, r=40, t=100, b=80)
    )
    
    return fig


def create_multi_investor_dashboard(investors_data):
    """
    Create a dashboard with multiple investor comparisons
    
    Args:
        investors_data: Dictionary with investor names as keys and their data as values
        
    Returns:
        plotly.graph_objects.Figure
    """
    # Calculate number of rows needed (2 charts per row)
    num_investors = len(investors_data)
    num_rows = (num_investors + 1) // 2
    
    # Adjust spacing based on number of rows
    if num_rows > 10:
        vertical_spacing = 0.02  # Tighter spacing for many investors
    else:
        vertical_spacing = 0.12
    
    # Create subplot titles
    subplot_titles = list(investors_data.keys())
    
    fig = make_subplots(
        rows=num_rows,
        cols=2,
        subplot_titles=subplot_titles,
        vertical_spacing=vertical_spacing,
        horizontal_spacing=0.1,
        specs=[[{'type': 'scatter'}] * 2] * num_rows
    )
    
    colors = {
        'Actual Portfolio': '#1f77b4',
        'NIFTY 50': '#ff7f0e',
        'NIFTY Small Cap 250': '#2ca02c',
        'NIFTY Mid Cap 150': '#d62728',
        'NIFTY Large Cap': '#9467bd',
        'GM Multi Cap': '#8c564b',
        'GM Mid & Small Cap': '#e377c2'
    }
    
    for idx, (investor_name, data) in enumerate(investors_data.items()):
        row = (idx // 2) + 1
        col = (idx % 2) + 1
        
        monthly_data = data.get('monthly_data', {})
        
        for strategy_name, values in monthly_data.items():
            if isinstance(values, pd.Series) and len(values) > 0:
                showlegend = (idx == 0)  # Only show legend for first subplot
                
                fig.add_trace(
                    go.Scatter(
                        x=values.index,
                        y=values.values,
                        mode='lines+markers',
                        name=strategy_name,
                        line=dict(width=2, color=colors.get(strategy_name, '#000000')),
                        marker=dict(size=4),
                        showlegend=showlegend,
                        legendgroup=strategy_name,
                        hovertemplate='%{fullData.name}<br>₹%{y:,.2f}<extra></extra>'
                    ),
                    row=row, col=col
                )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Investment Comparison Dashboard - All Investors',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        height=300 * num_rows,  # Reduced height per row for many investors
        showlegend=True,
        plot_bgcolor='#ffffff',
        paper_bgcolor='#f5f5f5',
        hovermode='closest',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )
    
    # Update axes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128, 128, 128, 0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128, 128, 128, 0.2)', 
                     tickformat=',.0f')
    
    return fig


def save_chart(fig, filename=None):
    """
    Save chart to HTML file
    
    Args:
        fig: Plotly figure object
        filename: Output filename (optional)
    """
    if filename is None:
        filename = GRAPH_FILE
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    # Save as HTML with full interactivity
    fig.write_html(
        output_path,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': filename.replace('.html', ''),
                'height': 800,
                'width': 1400,
                'scale': 2
            }
        }
    )
    
    print(f"Chart saved to: {output_path}")
    return output_path