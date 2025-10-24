# Investment Portfolio Comparison System

## 📊 Overview
A comprehensive investment analysis system that compares individual investor portfolios against NIFTY 50 and GM Mutual Funds. The system tracks performance since April 2024, providing monthly analysis and interactive TradingView-style visualizations.

## ✨ Key Features

### 1. **Individual Investor Tracking**
- Analyzes ~50 individual investors from the DETAILED_HOLDING sheet
- Calculates each investor's April 2024 investment value
- Tracks monthly performance for each investor separately

### 2. **Benchmark Comparisons**
- **NIFTY 50**: Direct comparison with market index
- **GM Multi Cap Fund**: Comparison with multi-cap mutual fund
- **GM Mid & Small Cap Fund**: Comparison with mid/small-cap fund

### 3. **Monthly Performance Analysis**
- Shows month-by-month rises and falls
- Calculates monthly returns and cumulative performance
- Identifies best and worst performing months

### 4. **Interactive Visualizations**
- TradingView-style dark theme charts
- Toggle individual investor lines on/off
- Hover for detailed information
- Monthly performance bar charts

### 5. **Comprehensive Reporting**
- Investment analysis Excel reports
- Monthly performance reports
- JSON data exports for programmatic access
- Performance ranking charts

## 📁 Project Structure

```
nifty_comparision/
│
├── run_analysis.py           # Main entry point - run this!
├── enhanced_main.py          # Enhanced analysis logic
├── enhanced_visualizer.py    # TradingView-style charts
├── investment_calculator.py  # April 2024 investment calculations
├── monthly_analyzer.py       # Monthly performance tracking
├── data_loader.py           # Excel data loading
├── market_data.py           # NIFTY data fetching
├── ticker_resolver.py       # Security ticker resolution
├── nse_data_loader.py       # NSE stock data loading
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
│
├── data/                   # Data directory
├── output/                 # Interactive dashboards
├── reports/                # Excel and JSON reports
│   ├── monthly_reports/    # Monthly performance reports
│   └── ticker_reports/     # Ticker resolution reports
│
└── stock_data_NSE/         # NSE stock price data
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Complete Analysis
```bash
python run_analysis.py
```

This will:
- Load holdings and fund data
- Calculate April 2024 investment values
- Fetch stock price data
- Calculate monthly performance
- Compare with NIFTY and GM funds
- Generate interactive dashboards
- Create comprehensive reports

## 📊 Data Requirements

### Input Files Required:
1. **Demat Holding_Nil_Trade_01.07.2025.xlsx**
   - Sheet: `DETAILED_HOLDING`
   - Columns: NAME, Security Name, Holding, Demat Holding Vlaue (Rs.)

2. **CURRENT_WEIGHATGE_(Aug 25).xlsx**
   - Sheet: `Sheet`
   - Contains two tables:
     - GM Multi Cap (As on 31-Aug-2025)
     - GM Mid & Small Cap (As on 31-Aug-2025)

## 📈 Output Files

### 1. Interactive Dashboards (output/)
- `interactive_dashboard_YYYYMMDD_HHMMSS.html` - Main comparison dashboard
- `ranking_chart_YYYYMMDD.html` - Performance ranking visualization

### 2. Reports (reports/)
- `investment_analysis_YYYYMMDD_HHMMSS.xlsx` - Investment value analysis
- `monthly_performance_YYYYMMDD_HHMMSS.xlsx` - Monthly performance details
- JSON files for programmatic access

## 🎯 Key Features Explained

### Individual Investor Analysis
- Each investor's holdings are tracked separately
- Investment values calculated based on April 2024 prices
- Monthly returns computed for each investor
- Can toggle individual lines in the interactive chart

### Monthly Rise/Fall Tracking
- Shows performance for each month since April 2024
- Identifies rising months (positive returns) vs falling months
- Calculates volatility and drawdown metrics
- Provides month-over-month comparison

### Interactive Legend
- Click on any investor name to show/hide their line
- Group toggles for categories (Investors, Benchmarks, Funds)
- "Show All" / "Hide Individuals" / "NIFTY Only" buttons
- Hover over any point for detailed information

### Investment Calculation
- Uses actual stock prices from April 2024
- Calculates initial investment for each investor
- Tracks gain/loss in both absolute and percentage terms
- Compares current value with initial investment

## 🔧 Configuration

Edit `config.py` to modify:
- Investment start date (default: April 1, 2024)
- File paths and sheet names
- Output directories

## 📝 Important Notes

1. **Data Coverage**: Not all securities may have price data available
2. **Performance**: Large number of investors may take time to process
3. **Browser**: Interactive charts work best in modern browsers (Chrome, Firefox, Edge)
4. **Excel Limits**: Sheet names are limited to 31 characters

## 🆘 Troubleshooting

### Common Issues:

1. **Missing Price Data**
   - Check stock_data_NSE/ folder for available data
   - Some securities may not have NSE data

2. **Excel Loading Errors**
   - Ensure column names match expected format
   - Check for empty rows or invalid data

3. **Visualization Issues**
   - Open HTML files in a modern browser
   - Clear browser cache if charts don't load

## 📊 Performance Metrics

The system calculates:
- **Cumulative Returns**: Total return since April 2024
- **Monthly Returns**: Month-over-month performance
- **Alpha**: Excess return over benchmarks
- **Volatility**: 3-month rolling standard deviation
- **Drawdown**: Maximum decline from peak

## 🎨 Chart Features

### TradingView-Style Interface
- Dark theme for better visibility
- Professional financial charting
- Multiple chart types (line, bar)
- Responsive and interactive

### Interactive Elements
- Zoom and pan capabilities
- Hover tooltips with detailed info
- Click legends to toggle series
- Export charts as images

## 📈 Success Metrics

The analysis shows:
- How many investors beat NIFTY 50
- Average investor performance
- Best and worst performers
- Comparison with mutual funds

## 🚦 Running Status

When you run `python run_analysis.py`, you'll see:
```
STEP 1: Loading Data Files
STEP 2: Resolving Security Tickers
STEP 3: Loading Stock Price Data
STEP 4: Calculating Investment Values
STEP 5: Calculating Portfolio Performance
STEP 6: Analyzing Monthly Performance
STEP 7: Loading Benchmark Data
STEP 8: Creating Interactive Visualizations
STEP 9: Final Summary
```

## 📧 Support

For issues or questions about the analysis, check:
1. The reports/ticker_reports/ folder for resolution issues
2. The console output for any error messages
3. The JSON files in reports/ for detailed data

---

**Last Updated**: October 2024
**Version**: 2.0 Enhanced
