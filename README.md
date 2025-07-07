# Dividend Analysis Project

A comprehensive Python toolkit for analyzing dividend payments and their impact on stock prices using Yahoo Finance data. This project provides tools for scraping historical stock data, tracking dividend payments, and calculating tax implications.

## Features

- **Historical Data Scraping**: Fetch historical stock prices, dividends, and stock splits from Yahoo Finance
- **Dividend Calendar**: Track dividend payment dates and amounts across multiple securities
- **Price Impact Analysis**: Analyze how dividend payments affect stock prices on ex-dividend dates
- **Tax Calculation**: Calculate federal tax obligations on dividend income
- **Comprehensive Analytics**: Generate detailed statistics and visualizations for dividend analysis

## Project Structure

```
dividend_analysis/
├── README.md                          # This file
├── dividend_calendar.csv              # Historical dividend payment data
├── diviendchart.py                   # Main Yahoo Finance scraper class
├── federal_tax_calculator.py         # Federal tax calculation utilities
└── generated_files/                  # Output directory for analysis results
    ├── combined_historical_data.csv
    ├── comprehensive_dividend_calendar.csv
    └── dividend_statistics.json
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Required Dependencies

Install the required packages using pip:

```bash
pip install pandas numpy matplotlib requests
```

Or create a `requirements.txt` file with the following content:

```txt
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.3.0
requests>=2.25.0
```

Then install with:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Basic Usage - Scraping Dividend Data

```python
from diviendchart import YahooFinanceScraper

# Initialize the scraper
scraper = YahooFinanceScraper(delay_range=(1, 2))

# Scrape data for SPY ETF
data = scraper.scrape_multiple_tickers(
    tickers=['SPY'],
    start_date='2020-01-01',
    end_date='2023-12-31',
    include_dividends=True
)

# Display results
for ticker, df in data.items():
    print(f"{ticker} - Data shape: {df.shape}")
    dividend_payments = df[df['Dividend'] > 0]
    print(f"Found {len(dividend_payments)} dividend payments")
```

### 2. Generate Dividend Calendar

```python
# Create comprehensive dividend analysis
dividend_calendar = scraper.create_dividend_analysis(combined_data)

# Save to CSV
dividend_calendar.to_csv('dividend_calendar.csv', index=False)

# Generate summary statistics
stats = scraper.get_dividend_summary_stats(dividend_calendar)
print(f"Total dividend payments: {stats['total_payments']}")
print(f"Average dividend yield: {stats['avg_daily_yield']:.2f}%")
```

### 3. Calculate Tax Obligations

```python
from federal_tax_calculator import federal_tax_calculator

# Calculate federal taxes on dividend income
annual_dividend_income = 5000
federal_tax_calculator(annual_dividend_income)
```

## Core Classes and Methods

### YahooFinanceScraper

The main class for scraping financial data from Yahoo Finance.

#### Key Methods:

- **`get_historical_data(ticker, start_date, end_date, include_dividends=False)`**
  - Fetch historical price and volume data
  - Optionally include dividend payments
  - Returns pandas DataFrame with OHLCV data

- **`get_dividend_data(ticker, start_date, end_date)`**
  - Fetch only dividend payment data
  - Returns DataFrame with dates and dividend amounts

- **`get_stock_splits(ticker, start_date, end_date)`**
  - Fetch stock split information
  - Returns DataFrame with split dates and ratios

- **`scrape_multiple_tickers(tickers, start_date, end_date, output_format='dict', include_dividends=False)`**
  - Scrape data for multiple securities
  - Built-in rate limiting to respect API limits
  - Option to save directly to CSV files

- **`create_dividend_analysis(combined_data)`**
  - Generate comprehensive dividend calendar
  - Calculate price impact metrics
  - Analyze ex-dividend date effects

- **`get_dividend_summary_stats(dividend_calendar)`**
  - Generate summary statistics
  - Calculate yield metrics
  - Analyze price drop patterns

### Federal Tax Calculator

Simple utility for calculating federal income taxes.

- **`federal_tax_calculator(taxable_income)`**
  - Calculate federal taxes based on 2024 tax brackets
  - Includes standard deduction
  - Supports all tax brackets from 10% to 37%

## Data Schema

### Dividend Calendar CSV Format

| Column | Description |
|--------|-------------|
| Date | Dividend payment date |
| Ticker | Stock ticker symbol |
| Open | Opening price on ex-dividend date |
| High | Highest price on ex-dividend date |
| Low | Lowest price on ex-dividend date |
| Close | Closing price on ex-dividend date |
| Volume | Trading volume |
| Dividend | Dividend amount per share |
| Dividend_Yield_Daily | Daily dividend yield percentage |
| Price_Drop_Pct | Price drop percentage on ex-dividend date |
| Ex_Dividend_Impact | Actual price drop amount |

## Configuration

### Scraper Settings

You can customize the scraper behavior:

```python
# Adjust delay between requests (seconds)
scraper = YahooFinanceScraper(delay_range=(1, 3))

# Custom headers for different user agents
scraper.headers['User-Agent'] = 'Your Custom User Agent'
```

### Date Formats

All date inputs should be in 'YYYY-MM-DD' format:

```python
start_date = '2020-01-01'
end_date = '2023-12-31'
```

## Example Analysis Workflows

### 1. Dividend Growth Analysis

```python
# Analyze dividend growth over time
spy_dividends = scraper.get_dividend_data('SPY', '2010-01-01', '2023-12-31')
spy_dividends['Year'] = spy_dividends['Date'].dt.year
annual_dividends = spy_dividends.groupby('Year')['Dividend'].sum()
print("Annual dividend growth:")
print(annual_dividends.pct_change().dropna())
```

### 2. Multi-Stock Dividend Comparison

```python
# Compare dividend patterns across multiple ETFs
etfs = ['SPY', 'QQQ', 'IWM', 'EFA']
data = scraper.scrape_multiple_tickers(
    tickers=etfs,
    start_date='2020-01-01',
    end_date='2023-12-31',
    include_dividends=True
)

# Analyze dividend frequency and amounts
for ticker, df in data.items():
    div_payments = df[df['Dividend'] > 0]
    print(f"{ticker}: {len(div_payments)} payments, avg ${div_payments['Dividend'].mean():.3f}")
```

### 3. Ex-Dividend Date Price Impact

```python
# Analyze price behavior on ex-dividend dates
dividend_calendar = scraper.create_dividend_analysis(combined_data)
avg_price_drop = dividend_calendar['Price_Drop_Pct'].mean()
print(f"Average price drop on ex-dividend date: {avg_price_drop:.2f}%")

# Compare actual vs theoretical price drops
actual_vs_theoretical = dividend_calendar['Actual_vs_Theoretical'].mean()
print(f"Average difference from theoretical price: ${actual_vs_theoretical:.3f}")
```

## Rate Limiting and Best Practices

### Respectful API Usage

- Built-in delays between requests (1-3 seconds by default)
- Randomized delay intervals to appear more human-like
- Proper error handling for API failures
- Session management for efficient connection reuse

### Error Handling

The scraper includes comprehensive error handling:

```python
try:
    data = scraper.get_historical_data('INVALID_TICKER', '2020-01-01', '2023-12-31')
except Exception as e:
    print(f"Error occurred: {e}")
    # Graceful fallback or retry logic
```

## Troubleshooting

### Common Issues

1. **No data returned**: Check that the ticker symbol is valid and the date range includes trading days
2. **Rate limiting**: Increase delay between requests if you encounter HTTP 429 errors
3. **Missing dividends**: Some stocks may not pay dividends; check with a financial data provider
4. **Date format errors**: Ensure dates are in 'YYYY-MM-DD' format

### Debug Mode

Enable verbose output for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Write unit tests for new functionality

## License

This project is provided as-is for educational and research purposes. Please respect Yahoo Finance's terms of service when using their data.

## Disclaimer

This tool is for educational and research purposes only. It should not be used as the sole basis for investment decisions. Always consult with qualified financial advisors before making investment choices.

The dividend and price data is sourced from Yahoo Finance and may not be completely accurate or up-to-date. Users should verify important information through official sources.

## Support

For questions or issues:

1. Check the troubleshooting section above
2. Review the example code in the main script
3. Create an issue in the project repository with detailed error messages and steps to reproduce

## Future Enhancements

- [ ] Add support for international markets
- [ ] Implement dividend yield forecasting
- [ ] Add portfolio-level dividend analysis
- [ ] Include state tax calculations
- [ ] Add data visualization capabilities
- [ ] Implement backtesting framework for dividend strategies
- [ ] Add support for REITs and special dividend handling
