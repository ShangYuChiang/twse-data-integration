"""
資料取得器 - 整合 API 客戶端和快取機制
"""

import logging
from typing import List, Dict, Optional, Any
import pandas as pd
from datetime import datetime

from src.api_client import TWSSEAPIClient
from src.cache import get_cache, BaseCache
from src.models import Company, StockPrice, HistoricalData, FinancialStatement
from src.config import config

logger = logging.getLogger(__name__)


class TWDataFetcher:
    """TWSE 資料取得器"""
    
    def __init__(self, cache_enabled: bool = True, cache_type: str = "memory"):
        """
        初始化資料取得器
        
        Args:
            cache_enabled: 是否啟用快取
            cache_type: 快取類型 ("memory" 或 "redis")
        """
        self.api_client = TWSSEAPIClient()
        self.cache_enabled = cache_enabled
        
        if cache_enabled:
            self.cache = get_cache(cache_type, ttl=config.CACHE_TTL)
        else:
            self.cache = None
    
    def _get_from_cache_or_fetch(
        self,
        cache_key: str,
        fetch_func,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        從快取取得或取得新資料
        
        Args:
            cache_key: 快取鍵
            fetch_func: 取得資料的函數
            *args: 函數參數
            **kwargs: 函數關鍵字參數
            
        Returns:
            取得的資料或快取資料
        """
        # 嘗試從快取取得
        if self.cache_enabled and self.cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"Retrieved from cache: {cache_key}")
                return cached_data
        
        # 取得新資料
        try:
            data = fetch_func(*args, **kwargs)
            
            # 快取資料
            if self.cache_enabled and self.cache and data:
                self.cache.set(cache_key, data)
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise
    
    def get_listed_companies(self, force_refresh: bool = False) -> List[Dict]:
        """
        取得所有上市公司
        
        Args:
            force_refresh: 是否強制重新取得
            
        Returns:
            List[Dict]: 上市公司列表
        """
        cache_key = "listed_companies"
        
        if force_refresh and self.cache:
            self.cache.delete(cache_key)
        
        def _fetch():
            response = self.api_client.get_listed_companies()
            return self._parse_companies(response)
        
        return self._get_from_cache_or_fetch(cache_key, _fetch)
    
    def get_stock_price(self, stock_code: str, date: Optional[str] = None) -> Dict:
        """
        取得股票即時價格
        
        Args:
            stock_code: 股票代號
            date: 日期（YYYY-MM-DD 格式），預設為今日
            
        Returns:
            Dict: 股票價格資料
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        cache_key = f"stock_price:{stock_code}:{date}"
        
        def _fetch():
            response = self.api_client.get_stock_price(stock_code, date.replace("-", ""))
            return self._parse_stock_price(response)
        
        return self._get_from_cache_or_fetch(cache_key, _fetch)
    
    def get_historical_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        取得歷史行情資料
        
        Args:
            stock_code: 股票代號
            start_date: 起始日期（YYYY-MM-DD 格式）
            end_date: 結束日期（YYYY-MM-DD 格式）
            force_refresh: 是否強制重新取得
            
        Returns:
            pd.DataFrame: 歷史行情資料
        """
        cache_key = f"historical:{stock_code}:{start_date}:{end_date}"
        
        if force_refresh and self.cache:
            self.cache.delete(cache_key)
        
        def _fetch():
            response = self.api_client.get_historical_data(stock_code, start_date, end_date)
            return self._parse_historical_data(response)
        
        data = self._get_from_cache_or_fetch(cache_key, _fetch)
        
        if data:
            return pd.DataFrame(data)
        return pd.DataFrame()
    
    def get_financial_reports(
        self,
        stock_code: str,
        year: int,
        quarter: Optional[int] = None,
        force_refresh: bool = False
    ) -> Dict:
        """
        取得財務報表資料
        
        Args:
            stock_code: 股票代號
            year: 年份
            quarter: 季度（1-4），None 表示年報
            force_refresh: 是否強制重新取得
            
        Returns:
            Dict: 財務報表資料
        """
        report_type = f"Q{quarter}" if quarter else "ANNUAL"
        cache_key = f"financial:{stock_code}:{year}:{report_type}"
        
        if force_refresh and self.cache:
            self.cache.delete(cache_key)
        
        def _fetch():
            response = self.api_client.get_financial_reports(stock_code, year, quarter)
            return self._parse_financial_reports(response)
        
        return self._get_from_cache_or_fetch(cache_key, _fetch)
    
    def _parse_companies(self, response: Dict) -> List[Dict]:
        """解析上市公司資料"""
        try:
            if not response or "data" not in response:
                return []
            
            companies = []
            for item in response.get("data", []):
                try:
                    company = Company(
                        stock_code=item.get("code", ""),
                        company_name=item.get("name", ""),
                        isin_code=item.get("isin", ""),
                        market_type=item.get("market", ""),
                        industry_code=item.get("industryCode", ""),
                        industry_name=item.get("industryName", ""),
                        listing_date=item.get("listingDate", ""),
                    )
                    companies.append(company.dict())
                except Exception as e:
                    logger.warning(f"Error parsing company: {e}")
            
            return companies
        except Exception as e:
            logger.error(f"Error parsing companies: {e}")
            return []
    
    def _parse_stock_price(self, response: Dict) -> Dict:
        """解析股票價格資料"""
        try:
            if not response or "data" not in response or not response["data"]:
                return {}
            
            data = response["data"][0]
            
            return {
                "stock_code": data.get("code", ""),
                "trading_date": data.get("date", ""),
                "opening_price": float(data.get("open", 0)),
                "highest_price": float(data.get("high", 0)),
                "lowest_price": float(data.get("low", 0)),
                "closing_price": float(data.get("close", 0)),
                "price_change": float(data.get("change", 0)),
                "price_change_percent": float(data.get("changePercent", 0)),
                "trading_volume": int(data.get("volume", 0)),
                "trading_value": int(data.get("value", 0)),
                "transaction_count": int(data.get("transactions", 0)),
            }
        except Exception as e:
            logger.error(f"Error parsing stock price: {e}")
            return {}
    
    def _parse_historical_data(self, response: Dict) -> List[Dict]:
        """解析歷史行情資料"""
        try:
            if not response or "data" not in response:
                return []
            
            historical = []
            for item in response.get("data", []):
                try:
                    data = {
                        "stock_code": response.get("stock_code", ""),
                        "trading_date": item.get("date", ""),
                        "opening_price": float(item.get("open", 0)),
                        "highest_price": float(item.get("high", 0)),
                        "lowest_price": float(item.get("low", 0)),
                        "closing_price": float(item.get("close", 0)),
                        "price_change": float(item.get("change", 0)),
                        "price_change_percent": float(item.get("changePercent", 0)),
                        "trading_volume": int(item.get("volume", 0)),
                        "trading_value": int(item.get("value", 0)),
                        "transaction_count": int(item.get("transactions", 0)),
                    }
                    historical.append(data)
                except Exception as e:
                    logger.warning(f"Error parsing historical data: {e}")
            
            return historical
        except Exception as e:
            logger.error(f"Error parsing historical data: {e}")
            return []
    
    def _parse_financial_reports(self, response: Dict) -> Dict:
        """解析財務報表資料"""
        try:
            if not response or "data" not in response:
                return {}
            
            data = response.get("data", {})
            
            return {
                "stock_code": data.get("code", ""),
                "year": data.get("year", 0),
                "quarter": data.get("quarter"),
                "report_type": "季報" if "quarter" in data else "年報",
                "total_assets": float(data.get("totalAssets", 0)),
                "current_assets": float(data.get("currentAssets", 0)),
                "total_liabilities": float(data.get("totalLiabilities", 0)),
                "total_equity": float(data.get("totalEquity", 0)),
                "revenue": float(data.get("revenue", 0)),
                "net_income": float(data.get("netIncome", 0)),
                "eps": float(data.get("eps", 0)),
                "roe": float(data.get("roe", 0)),
                "roa": float(data.get("roa", 0)),
                "report_date": data.get("reportDate", ""),
            }
        except Exception as e:
            logger.error(f"Error parsing financial reports: {e}")
            return {}
    
    def clear_cache(self):
        """清空快取"""
        if self.cache:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def close(self):
        """關閉連線"""
        self.api_client.close()
    
    def __enter__(self):
        """Context manager 進入"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 退出"""
        self.close()
