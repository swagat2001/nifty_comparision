"""
Configuration file for Investment Comparison Analysis
"""

# File Paths
HOLDINGS_FILE = r"C:\\Users\swaga\\OneDrive\\Desktop\\nifty_comparision\\Demat Holding_Nil_Trade_01.07.2025.xlsx"
PORTFOLIO_FILE = r"C:\\Users\\swaga\\OneDrive\\Desktop\\nifty_comparision\\CURRENT_WEIGHATGE_(Aug 25).xlsx"

# Sheet Names
HOLDINGS_SHEET = "DETAILED_HOLDING"
PORTFOLIO_SHEET = "Sheet"

# Column Names
NAME_COL = "NAME"
SECURITY_NAME_COL = "Security Name"
HOLDING_COL = "Holding"
CURRENT_VALUE_COL = "Demat Holding Vlaue (Rs.)"

# Investment Date
INVESTMENT_DATE = "2024-04-01"  # April 2024

# NIFTY Indices Symbols
NIFTY_INDICES = {
    "NIFTY 50": "^NSEI",
    "NIFTY Small Cap 100": "^CNXSC",
    "NIFTY Midcap 100": "^NSEMDCP50",
    "NIFTY 100": "^CNX100"
}

# Portfolio Names
MULTI_CAP_PORTFOLIO = "GM Multi Cap (As on 31-Aug-2025)"
MID_SMALL_CAP_PORTFOLIO = "GM Mid & Small Cap (As on 31-Aug-2025)"

# Output Settings
OUTPUT_DIR = r"C:\\Users\\Admin\\Desktop\\nifty_comparision\\output"
GRAPH_FILE = "investment_comparison.html"
