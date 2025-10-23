"""
Visualizer - Creates 4-line comparison chart
1. Investor Portfolio
2. NIFTY 50
3. GM Multi Cap Fund
4. GM Mid & Small Cap Fund
"""
import plotly.graph_objects as go
from pathlib import Path


# Get OUTPUT_DIR from config dynamically
try:
    from config import OUTPUT_DIR
except:
    OUTPUT_DIR = Path(__file__).parent / 'output'
    OUTPUT_DIR.mkdir(exist_ok=True)


def create_fund_comparison_chart(investor_returns, nifty_returns, multi_cap_returns, 
                                  mid_small_returns, investor_name="Investor Portfolio"):
    """
    Create 4-line comparison chart:
    1. Investor Portfolio (actual)
    2. NIFTY 50 (benchmark)
    3. GM Multi Cap Fund
    4. GM Mid & Small Cap Fund
    """
    fig = go.Figure()
    
    # Define colors and styles for each line
    chart_config = {
        'NIFTY 50': {
            'data': nifty_returns,
            'color': '#FF6B6B',
            'width': 2,
            'dash': 'solid'
        },
        'GM Multi Cap Fund': {
            'data': multi_cap_returns,
            'color': '#4ECDC4',
            'width': 2.5,
            'dash': 'dash'
        },
        'GM Mid & Small Cap Fund': {
            'data': mid_small_returns,
            'color': '#95E1D3',
            'width': 2.5,
            'dash': 'dot'
        },
        investor_name: {
            'data': investor_returns,
            'color': '#FFD93D',
            'width': 3,
            'dash': 'solid'
        }
    }
    
    # Add all traces
    for name, config in chart_config.items():
        fig.add_trace(go.Scatter(
            x=config['data'].index,
            y=config['data'].values * 100,
            name=name,
            mode='lines',
            line=dict(
                width=config['width'],
                color=config['color'],
                dash=config['dash']
            ),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x|%b %Y}<br>' +
                         'Return: %{y:.2f}%<extra></extra>'
        ))
    
    # Calculate final returns for annotation
    final_returns = {
        name: config['data'].iloc[-1] * 100 
        for name, config in chart_config.items()
    }
    
    # Find best and worst performers
    best = max(final_returns.items(), key=lambda x: x[1])
    worst = min(final_returns.items(), key=lambda x: x[1])
    
    # Create annotations text
    returns_text = "<b>Final Returns:</b><br>"
    for name, ret in final_returns.items():
        emoji = "🏆" if name == best[0] else ("📉" if name == worst[0] else "📊")
        returns_text += f"{emoji} {name}: <b>{ret:.2f}%</b><br>"
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'<b>Investment Comparison Analysis</b><br>' +
                   f'<sub>Period: {investor_returns.index[0].strftime("%b %Y")} to ' +
                   f'{investor_returns.index[-1].strftime("%b %Y")}</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22}
        },
        xaxis_title='<b>Date</b>',
        yaxis_title='<b>Cumulative Returns (%)</b>',
        hovermode='x unified',
        template='plotly_white',
        height=700,
        font=dict(size=12),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="Black",
            borderwidth=2,
            font=dict(size=13)
        ),
        annotations=[
            dict(
                text=returns_text,
                xref="paper", yref="paper",
                x=0.98, y=0.02,
                xanchor="right", yanchor="bottom",
                showarrow=False,
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="black",
                borderwidth=2,
                font=dict(size=12)
            )
        ],
        plot_bgcolor='rgba(245,245,245,0.5)'
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig


def save_chart(fig, filename):
    """Save chart to HTML file"""
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    filepath = output_path / filename
    fig.write_html(str(filepath))
    
    print(f"  ✓ Saved: {filepath}")
    
    return filepath


if __name__ == "__main__":
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Exists: {Path(OUTPUT_DIR).exists()}")
