"""
改进的数据取得器 - 使用打开源数据接口
"""

import logging
from typing import List, Dict, Optional, Any
import pandas as pd
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class AlternativeDataFetcher:
    """使用开源 API 的替代数据获取器"""
    
    def __init__(self):
        """初始化数据获取器"""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_stock_price_from_yahoo(self, stock_code: str) -> Dict:
        """
        从 Yahoo Finance 获取股票价格
        
        Args:
            stock_code: 股票代号
            
        Returns:
            Dict: 股票价格数据
        """
        try:
            # 台湾股票需要加 .TW 后缀
            ticker = f"{stock_code}.TW"
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
            params = {
                "modules": "price,summaryProfile"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            price_data = data.get('quoteSummary', {}).get('result', [{}])[0].get('price', {})
            
            return {
                'stock_code': stock_code,
                'trading_date': datetime.now().strftime('%Y-%m-%d'),
                'closing_price': price_data.get('regularMarketPrice', {}).get('raw', 0),
                'price_change': price_data.get('regularMarketChange', {}).get('raw', 0),
                'price_change_percent': price_data.get('regularMarketChangePercent', {}).get('raw', 0),
            }
        except Exception as e:
            logger.error(f"Failed to get price from Yahoo Finance: {e}")
            return {}
    
    def get_twse_mock_data(self, stock_code: str) -> Dict:
        """
        返回模拟数据用于演示
        
        Args:
            stock_code: 股票代号
            
        Returns:
            Dict: 模拟股票数据
        """
        # 常见股票的示例数据
        mock_data = {
            '2330': {
                'stock_code': '2330',
                'company_name': '台积电',
                'closing_price': 950.0,
                'opening_price': 948.0,
                'highest_price': 955.0,
                'lowest_price': 947.0,
                'price_change': 2.0,
                'price_change_percent': 0.21,
                'trading_volume': 50000000,
                'trading_value': 47600000000,
                'industry_name': '半导体业',
            },
            '2454': {
                'stock_code': '2454',
                'company_name': '联发科',
                'closing_price': 1120.0,
                'opening_price': 1115.0,
                'highest_price': 1125.0,
                'lowest_price': 1110.0,
                'price_change': 5.0,
                'price_change_percent': 0.45,
                'trading_volume': 40000000,
                'trading_value': 45000000000,
                'industry_name': '半导体业',
            },
            '0050': {
                'stock_code': '0050',
                'company_name': '元大台湾50',
                'closing_price': 140.0,
                'opening_price': 139.5,
                'highest_price': 141.0,
                'lowest_price': 139.0,
                'price_change': 0.5,
                'price_change_percent': 0.36,
                'trading_volume': 100000000,
                'trading_value': 14000000000,
                'industry_name': '基金',
            },
        }
        
        return mock_data.get(stock_code, {})
    
    def get_listed_companies_mock(self) -> List[Dict]:
        """
        返回常见上市公司的模拟数据
        
        Returns:
            List[Dict]: 上市公司列表
        """
        return [
            {
                'stock_code': '2330',
                'company_name': '台积电',
                'industry_name': '半导体业',
                'listing_date': '1994-06-30',
                'market_type': '上市',
            },
            {
                'stock_code': '2454',
                'company_name': '联发科',
                'industry_name': '半导体业',
                'listing_date': '2002-06-24',
                'market_type': '上市',
            },
            {
                'stock_code': '2412',
                'company_name': '中华电',
                'industry_name': '电信业',
                'listing_date': '1999-12-30',
                'market_type': '上市',
            },
            {
                'stock_code': '0050',
                'company_name': '元大台湾50',
                'industry_name': '基金',
                'listing_date': '2003-06-30',
                'market_type': '上市',
            },
            {
                'stock_code': '0056',
                'company_name': '元大高股息',
                'industry_name': '基金',
                'listing_date': '2007-12-27',
                'market_type': '上市',
            },
        ]
    
    def close(self):
        """关闭连接"""
        self.session.close()
