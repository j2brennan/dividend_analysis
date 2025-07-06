import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import json
import random
from urllib.parse import urlencode

class YahooFinanceScraper:
    def __init__(self, delay_range=(1, 3)):
        self.session = requests.Session()
        self.delay_range = delay_range
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)
    
    def get_historical_data(self, ticker, start_date, end_date, include_dividends=False):
        """
        Fetch historical data for a given ticker
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL')
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
            include_dividends (bool): Whether to include dividend data as a column
        
        Returns:
            pandas.DataFrame: Historical stock data
        """
        try:
            # Convert dates to Unix timestamps
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            
            # Construct the URL
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                'period1': start_timestamp,
                'period2': end_timestamp,
                'interval': '1d',
                'events': 'history',
                'includeAdjustedClose': 'true'
            }
            
            # Make the request
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            if 'chart' not in data or not data['chart']['result']:
                print(f"No data found for {ticker}")
                return None
            
            # Extract data
            chart_data = data['chart']['result'][0]
            timestamps = chart_data['timestamp']
            quotes = chart_data['indicators']['quote'][0]
            
            # Create DataFrame
            df = pd.DataFrame({
                'Date': pd.to_datetime(timestamps, unit='s'),
                'Open': quotes['open'],
                'High': quotes['high'],
                'Low': quotes['low'],
                'Close': quotes['close'],
                'Volume': quotes['volume']
            })
            
            # Add adjusted close if available
            if 'adjclose' in chart_data['indicators']:
                df['Adj Close'] = chart_data['indicators']['adjclose'][0]['adjclose']
            
            # Add dividend data if requested
            if include_dividends:
                df['Dividend'] = 0.0  # Initialize dividend column
                
                # Get dividend data separately
                dividend_data = self.get_dividend_data(ticker, start_date, end_date)
                if dividend_data is not None and not dividend_data.empty:
                    # Merge dividend data with price data
                    df = df.merge(dividend_data[['Date', 'Dividend']], on='Date', how='left', suffixes=('', '_div'))
                    df['Dividend'] = df['Dividend_div'].fillna(0.0)
                    df = df.drop('Dividend_div', axis=1)
            
            # Clean data and sort by date
            df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])  # Don't drop rows with 0 dividends
            df = df.sort_values('Date')
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def get_dividend_data(self, ticker, start_date, end_date):
        """
        Fetch dividend data for a given ticker
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL')
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
        
        Returns:
            pandas.DataFrame: Dividend data with Date and Dividend columns
        """
        try:
            # Convert dates to Unix timestamps
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            
            # Construct the URL for dividend data
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                'period1': start_timestamp,
                'period2': end_timestamp,
                'interval': '1d',
                'events': 'div',  # Only get dividend events
                'includeAdjustedClose': 'false'
            }
            
            # Make the request
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            if 'chart' not in data or not data['chart']['result']:
                print(f"No dividend data found for {ticker}")
                return pd.DataFrame()
            
            chart_data = data['chart']['result'][0]
            
            # Check if dividend events exist
            if 'events' not in chart_data or 'dividends' not in chart_data['events']:
                print(f"No dividend events found for {ticker}")
                return pd.DataFrame()
            
            # Extract dividend data
            dividends = chart_data['events']['dividends']
            
            dividend_list = []
            for timestamp, div_info in dividends.items():
                dividend_list.append({
                    'Date': pd.to_datetime(int(timestamp), unit='s'),
                    'Dividend': div_info['amount']
                })
            
            if not dividend_list:
                return pd.DataFrame()
            
            # Create DataFrame
            df = pd.DataFrame(dividend_list)
            df = df.sort_values('Date')
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching dividend data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_splits(self, ticker, start_date, end_date):
        """
        Fetch stock split data for a given ticker
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL')
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
        
        Returns:
            pandas.DataFrame: Stock split data with Date and Split_Ratio columns
        """
        try:
            # Convert dates to Unix timestamps
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            
            # Construct the URL for stock split data
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                'period1': start_timestamp,
                'period2': end_timestamp,
                'interval': '1d',
                'events': 'split',  # Only get split events
                'includeAdjustedClose': 'false'
            }
            
            # Make the request
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            if 'chart' not in data or not data['chart']['result']:
                return pd.DataFrame()
            
            chart_data = data['chart']['result'][0]
            
            # Check if split events exist
            if 'events' not in chart_data or 'splits' not in chart_data['events']:
                return pd.DataFrame()
            
            # Extract split data
            splits = chart_data['events']['splits']
            
            split_list = []
            for timestamp, split_info in splits.items():
                split_list.append({
                    'Date': pd.to_datetime(int(timestamp), unit='s'),
                    'Split_Ratio': f"{split_info['numerator']}:{split_info['denominator']}",
                    'Split_Factor': split_info['splitRatio']
                })
            
            if not split_list:
                return pd.DataFrame()
            
            # Create DataFrame
            df = pd.DataFrame(split_list)
            df = df.sort_values('Date')
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching split data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def scrape_multiple_tickers(self, tickers, start_date, end_date, output_format='dict', include_dividends=False):
        """
        Scrape historical data for multiple tickers
        
        Args:
            tickers (list): List of ticker symbols
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
            output_format (str): 'dict' for dictionary or 'csv' to save as CSV files
            include_dividends (bool): Whether to include dividend data
        
        Returns:
            dict: Dictionary with ticker as key and DataFrame as value
        """
        results = {}
        
        for i, ticker in enumerate(tickers):
            print(f"Fetching data for {ticker} ({i+1}/{len(tickers)})")
            
            # Get data
            df = self.get_historical_data(ticker, start_date, end_date, include_dividends)
            
            if df is not None:
                results[ticker] = df
                
                # Save to CSV if requested
                if output_format == 'csv':
                    filename = f"{ticker}_historical_data.csv"
                    df.to_csv(filename, index=False)
                    print(f"Saved {ticker} data to {filename}")
            
            # Add delay between requests
            if i < len(tickers) - 1:  # Don't delay after last request
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)
        
        return results
    
    def get_ticker_info(self, ticker):
        """
        Get basic information about a ticker
        
        Args:
            ticker (str): Stock ticker symbol
        
        Returns:
            dict: Ticker information
        """
        try:
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
            params = {
                'modules': 'price,summaryDetail,defaultKeyStatistics'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'quoteSummary' not in data or not data['quoteSummary']['result']:
                return None
            
            result = data['quoteSummary']['result'][0]
            
            info = {
                'symbol': ticker,
                'longName': result.get('price', {}).get('longName', 'N/A'),
                'currency': result.get('price', {}).get('currency', 'N/A'),
                'exchange': result.get('price', {}).get('exchangeName', 'N/A'),
                'marketCap': result.get('price', {}).get('marketCap', {}).get('raw', 'N/A'),
                'sector': result.get('summaryDetail', {}).get('sector', 'N/A'),
                'industry': result.get('summaryDetail', {}).get('industry', 'N/A')
            }
            
            return info
            
        except Exception as e:
            print(f"Error fetching info for {ticker}: {str(e)}")
            return None
    
    def create_dividend_analysis(self, combined_data):
        """
        Create a comprehensive dividend analysis with price data
        
        Args:
            combined_data (pd.DataFrame): Combined data from multiple tickers
            
        Returns:
            pd.DataFrame: Detailed dividend analysis
        """
        # Filter for dividend payment days only
        dividend_days = combined_data[combined_data['Dividend'] > 0].copy()
        
        if dividend_days.empty:
            print("No dividend payments found in the data")
            return pd.DataFrame()
        
        # Calculate additional metrics
        dividend_days['Dividend_Yield_Daily'] = (dividend_days['Dividend'] / dividend_days['Close']) * 100
        dividend_days['Price_Drop_Pct'] = ((dividend_days['Open'] - dividend_days['Close']) / dividend_days['Open']) * 100
        dividend_days['Ex_Dividend_Impact'] = dividend_days['Open'] - dividend_days['Close']
        
        # Calculate price volatility on dividend day
        dividend_days['Day_Range_Pct'] = ((dividend_days['High'] - dividend_days['Low']) / dividend_days['Open']) * 100
        
        # Theoretical ex-dividend price (Open - Dividend)
        dividend_days['Theoretical_Ex_Price'] = dividend_days['Open'] - dividend_days['Dividend']
        dividend_days['Actual_vs_Theoretical'] = dividend_days['Close'] - dividend_days['Theoretical_Ex_Price']
        
        # Select relevant columns for the calendar
        calendar_columns = [
            'Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 
            'Dividend', 'Dividend_Yield_Daily', 'Price_Drop_Pct', 'Ex_Dividend_Impact',
            'Day_Range_Pct', 'Theoretical_Ex_Price', 'Actual_vs_Theoretical'
        ]
        
        # Only include columns that exist in the data
        available_columns = [col for col in calendar_columns if col in dividend_days.columns]
        dividend_calendar = dividend_days[available_columns].copy()
        
        dividend_calendar = dividend_calendar.sort_values(['Date', 'Ticker'])
        dividend_calendar = dividend_calendar.reset_index(drop=True)
        
        return dividend_calendar
    
    def get_dividend_summary_stats(self, dividend_calendar):
        """
        Generate summary statistics for dividend payments
        
        Args:
            dividend_calendar (pd.DataFrame): Dividend calendar data
            
        Returns:
            dict: Summary statistics
        """
        if dividend_calendar.empty:
            return {}
        
        stats = {}
        
        # Overall statistics
        stats['total_payments'] = len(dividend_calendar)
        stats['total_dividend_amount'] = dividend_calendar['Dividend'].sum()
        stats['avg_dividend_amount'] = dividend_calendar['Dividend'].mean()
        stats['median_dividend_amount'] = dividend_calendar['Dividend'].median()
        
        # Yield statistics
        if 'Dividend_Yield_Daily' in dividend_calendar.columns:
            stats['avg_daily_yield'] = dividend_calendar['Dividend_Yield_Daily'].mean()
            stats['max_daily_yield'] = dividend_calendar['Dividend_Yield_Daily'].max()
            stats['min_daily_yield'] = dividend_calendar['Dividend_Yield_Daily'].min()
        
        # Price impact statistics
        if 'Price_Drop_Pct' in dividend_calendar.columns:
            stats['avg_price_drop'] = dividend_calendar['Price_Drop_Pct'].mean()
            stats['max_price_drop'] = dividend_calendar['Price_Drop_Pct'].max()
            stats['min_price_drop'] = dividend_calendar['Price_Drop_Pct'].min()
        
        # By ticker statistics
        ticker_stats = dividend_calendar.groupby('Ticker').agg({
            'Dividend': ['count', 'sum', 'mean'],
            'Dividend_Yield_Daily': 'mean' if 'Dividend_Yield_Daily' in dividend_calendar.columns else lambda x: None
        }).round(4)
        
        stats['by_ticker'] = ticker_stats
        
        return stats

# Example usage
if __name__ == "__main__":
    # Initialize scraper
    scraper = YahooFinanceScraper(delay_range=(1, 2))
    
    # Define parameters
    tickers = ['SPY']
    start_date = '1930-01-01'
    end_date = '2025-7-03'
    
    print("Starting Yahoo Finance data scraping...")
    
    # Scrape data for multiple tickers with dividends
    data = scraper.scrape_multiple_tickers(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        output_format='dict',  # Change to 'csv' to save as CSV files
        include_dividends=True  # Include dividend data
    )
    
    # Display results
    for ticker, df in data.items():
        print(f"\n{ticker} - Data shape: {df.shape}")
        print(df.head())
        
        # Check for dividends
        if 'Dividend' in df.columns:
            dividend_dates = df[df['Dividend'] > 0]
            if not dividend_dates.empty:
                print(f"Found {len(dividend_dates)} dividend payments:")
                print(dividend_dates[['Date', 'Dividend']].head())
        
        # Get ticker info
        info = scraper.get_ticker_info(ticker)
        if info:
            print(f"Company: {info['longName']}")
            print(f"Exchange: {info['exchange']}")
    
    # Example: Get standalone dividend data
    print("\n--- Standalone Dividend Data ---")
    dividend_data = scraper.get_dividend_data('AAPL', '2020-01-01', '2023-12-31')
    if not dividend_data.empty:
        print(f"AAPL dividends - Shape: {dividend_data.shape}")
        print(dividend_data)
    
    # Example: Get stock split data
    print("\n--- Stock Split Data ---")
    split_data = scraper.get_stock_splits('AAPL', '2020-01-01', '2023-12-31')
    if not split_data.empty:
        print(f"AAPL splits - Shape: {split_data.shape}")
        print(split_data)
    
    # Example: Prepare data for backtesting
    print("\n--- Preparing data for backtesting ---")
    
    # Combine all data into a single DataFrame with multi-level columns
    combined_data = pd.DataFrame()
    
    for ticker, df in data.items():
        df_copy = df.copy()
        df_copy['Ticker'] = ticker
        combined_data = pd.concat([combined_data, df_copy], ignore_index=True)
    
    # Pivot to get ticker-based columns
    columns_to_pivot = ['Open', 'High', 'Low', 'Close', 'Volume']
    if 'Dividend' in combined_data.columns:
        columns_to_pivot.append('Dividend')
    if 'Adj Close' in combined_data.columns:
        columns_to_pivot.append('Adj Close')
    
    pivot_data = combined_data.pivot_table(
        index='Date', 
        columns='Ticker', 
        values=columns_to_pivot,
        aggfunc='first'
    )
    
    print(f"Combined data shape: {pivot_data.shape}")
    print(pivot_data.head())
    
    # Save combined data
    pivot_data.to_csv('combined_historical_data.csv')
    print("Combined data saved to 'combined_historical_data.csv'")
    
    # Example: Create a comprehensive dividend calendar
    print("\n--- Comprehensive Dividend Calendar ---")
    dividend_calendar = scraper.create_dividend_analysis(combined_data)
    
    if not dividend_calendar.empty:
        print(f"Found {len(dividend_calendar)} dividend payments")
        print("\nSample dividend calendar data:")
        print(dividend_calendar.head(10))
        
        # Save comprehensive dividend calendar
        dividend_calendar.to_csv('comprehensive_dividend_calendar.csv', index=False)
        print("\nComprehensive dividend calendar saved to 'comprehensive_dividend_calendar.csv'")
        
        # Generate and display summary statistics
        print("\n--- Dividend Summary Statistics ---")
        stats = scraper.get_dividend_summary_stats(dividend_calendar)
        
        print(f"Total dividend payments: {stats.get('total_payments', 0)}")
        print(f"Total dividend amount: ${stats.get('total_dividend_amount', 0):.2f}")
        print(f"Average dividend amount: ${stats.get('avg_dividend_amount', 0):.4f}")
        print(f"Average daily yield: {stats.get('avg_daily_yield', 0):.4f}%")
        print(f"Average price drop on ex-dividend day: {stats.get('avg_price_drop', 0):.4f}%")
        
        print("\nDividend payments by ticker:")
        if 'by_ticker' in stats:
            print(stats['by_ticker'])
        
        # Save statistics to file
        import json
        with open('dividend_statistics.json', 'w') as f:
            # Convert non-serializable objects to strings
            stats_serializable = {k: str(v) if not isinstance(v, (int, float, str, list, dict)) else v 
                                 for k, v in stats.items() if k != 'by_ticker'}
            json.dump(stats_serializable, f, indent=2)
        
        print("\nDividend statistics saved to 'dividend_statistics.json'")
    else:
        print("No dividend payments found in the selected date range")
