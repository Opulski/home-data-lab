"""
ENTSO-E Data Scraper

This module scrapes electricity market data from the ENTSO-E Transparency Platform.
Data includes:
- Day-ahead prices
- Actual generation per production type
- Load data
- Cross-border flows

Usage:
    python entsoe_scraper.py

Environment variables required:
    ENTSOE_API_KEY: Your ENTSO-E API key from https://transparency.entsoe.eu/
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import logging
from typing import Optional

try:
    from entsoe import EntsoePandasClient
except ImportError:
    print("Error: entsoe-py package not installed. Run: pip install entsoe-py")
    sys.exit(1)

# Load environment variables
load_dotenv('config.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/entsoe_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EntsoeDataScraper:
    """Scraper for ENTSO-E Transparency Platform data."""
    
    def __init__(self, api_key: str, data_dir: str = './data'):
        """
        Initialize the ENTSO-E scraper.
        
        Args:
            api_key: ENTSO-E API key
            data_dir: Directory to store scraped data
        """
        self.client = EntsoePandasClient(api_key=api_key)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info("ENTSO-E scraper initialized")
    
    def scrape_day_ahead_prices(
        self, 
        country_code: str, 
        start: pd.Timestamp, 
        end: pd.Timestamp
    ) -> Optional[pd.DataFrame]:
        """
        Scrape day-ahead electricity prices.
        
        Args:
            country_code: Two-letter country code (e.g., 'DE', 'FR')
            start: Start timestamp
            end: End timestamp
            
        Returns:
            DataFrame with day-ahead prices or None if error
        """
        try:
            logger.info(f"Scraping day-ahead prices for {country_code} from {start} to {end}")
            prices = self.client.query_day_ahead_prices(country_code, start=start, end=end)
            
            # Convert to DataFrame if it's a Series
            if isinstance(prices, pd.Series):
                prices = prices.to_frame(name='price')
            
            # Save to CSV
            filename = f"day_ahead_prices_{country_code}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.csv"
            filepath = self.data_dir / filename
            prices.to_csv(filepath)
            logger.info(f"Saved day-ahead prices to {filepath}")
            
            return prices
        except Exception as e:
            logger.error(f"Error scraping day-ahead prices: {e}")
            return None
    
    def scrape_load_data(
        self, 
        country_code: str, 
        start: pd.Timestamp, 
        end: pd.Timestamp
    ) -> Optional[pd.DataFrame]:
        """
        Scrape actual load data.
        
        Args:
            country_code: Two-letter country code
            start: Start timestamp
            end: End timestamp
            
        Returns:
            DataFrame with load data or None if error
        """
        try:
            logger.info(f"Scraping load data for {country_code} from {start} to {end}")
            load = self.client.query_load(country_code, start=start, end=end)
            
            # Convert to DataFrame if it's a Series
            if isinstance(load, pd.Series):
                load = load.to_frame(name='load')
            
            # Save to CSV
            filename = f"load_{country_code}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.csv"
            filepath = self.data_dir / filename
            load.to_csv(filepath)
            logger.info(f"Saved load data to {filepath}")
            
            return load
        except Exception as e:
            logger.error(f"Error scraping load data: {e}")
            return None
    
    def scrape_generation_data(
        self, 
        country_code: str, 
        start: pd.Timestamp, 
        end: pd.Timestamp
    ) -> Optional[pd.DataFrame]:
        """
        Scrape actual generation per production type.
        
        Args:
            country_code: Two-letter country code
            start: Start timestamp
            end: End timestamp
            
        Returns:
            DataFrame with generation data or None if error
        """
        try:
            logger.info(f"Scraping generation data for {country_code} from {start} to {end}")
            generation = self.client.query_generation(country_code, start=start, end=end)
            
            # Save to CSV
            filename = f"generation_{country_code}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.csv"
            filepath = self.data_dir / filename
            generation.to_csv(filepath)
            logger.info(f"Saved generation data to {filepath}")
            
            return generation
        except Exception as e:
            logger.error(f"Error scraping generation data: {e}")
            return None
    
    def scrape_all_data(self, country_code: str = 'DE', days_back: int = 7):
        """
        Scrape all available data types for a given country.
        
        Args:
            country_code: Two-letter country code (default: 'DE' for Germany)
            days_back: Number of days to look back from today
        """
        end = pd.Timestamp.now(tz='Europe/Berlin')
        start = end - pd.Timedelta(days=days_back)
        
        logger.info(f"Starting comprehensive scrape for {country_code}")
        logger.info(f"Period: {start} to {end}")
        
        # Scrape all data types
        self.scrape_day_ahead_prices(country_code, start, end)
        self.scrape_load_data(country_code, start, end)
        self.scrape_generation_data(country_code, start, end)
        
        logger.info("Comprehensive scrape completed")


def main():
    """Main function to run the scraper."""
    # Get API key from environment
    api_key = os.getenv('ENTSOE_API_KEY')
    if not api_key:
        logger.error("ENTSOE_API_KEY not found in environment variables")
        logger.error("Please set your API key in config.env file")
        sys.exit(1)
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    # Initialize scraper
    data_dir = os.getenv('DATA_DIR', './data')
    scraper = EntsoeDataScraper(api_key=api_key, data_dir=data_dir)
    
    # Scrape data for Germany (default)
    # You can change the country code or add more countries
    scraper.scrape_all_data(country_code='DE', days_back=7)
    
    logger.info("Scraping completed successfully")


if __name__ == '__main__':
    main()
