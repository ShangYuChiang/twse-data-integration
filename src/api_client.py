"""
TWSE API 客戶端 - 處理 HTTP 請求和回應
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from src.config import config

logger = logging.getLogger(__name__)


class TWSSEAPIClient:
    """TWSE API 客戶端"""
    
    def __init__(self):
        """初始化客戶端"""
        self.base_url = config.TWSE_BASE_URL
        self.timeout = config.TWSE_API_TIMEOUT
        self.max_retries = config.TWSE_MAX_RETRIES
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        建立帶有重試機制的 requests session
        
        Returns:
            requests.Session: 設定好的 session 物件
        """
        session = requests.Session()
        
        # 設定重試策略
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 設定請求頭
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        return session
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        """
        發送 GET 請求
        
        Args:
            endpoint: API 端點
            params: 查詢參數
            
        Returns:
            Dict: 回應資料
            
        Raises:
            requests.RequestException: 請求失敗
        """
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"Fetching: {url}")
        
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get_listed_companies(self) -> Dict:
        """
        取得上市公司列表
        
        Returns:
            Dict: 上市公司資料
        """
        endpoint = "exchangeReport/CORS/STOCKINFO"
        params = {
            "query.name": "",
            "firstin": "true",
            "step": "0"
        }
        
        return self.get(endpoint, params)
    
    def get_stock_price(self, stock_code: str, date: Optional[str] = None) -> Dict:
        """
        取得股票即時價格
        
        Args:
            stock_code: 股票代號
            date: 日期（YYYYMMDD 格式），預設為今日
            
        Returns:
            Dict: 股票價格資料
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        endpoint = "exchangeReport/CORS/OHLCMONTH"
        params = {
            "query.stockInfoItem.stockCode": stock_code,
            "query.date": date,
            "response.currentPageIndex": "1"
        }
        
        return self.get(endpoint, params)
    
    def get_historical_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        取得歷史行情資料
        
        Args:
            stock_code: 股票代號
            start_date: 起始日期（YYYY-MM-DD 格式）
            end_date: 結束日期（YYYY-MM-DD 格式）
            
        Returns:
            Dict: 歷史行情資料
        """
        # 轉換日期格式
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        all_data = []
        current = start
        
        while current <= end:
            date_str = current.strftime("%Y%m%d")
            
            try:
                data = self.get_stock_price(stock_code, date_str)
                if data and "data" in data:
                    all_data.extend(data["data"])
            except Exception as e:
                logger.warning(f"Failed to fetch data for {stock_code} on {date_str}: {e}")
            
            current += timedelta(days=1)
        
        return {
            "stock_code": stock_code,
            "start_date": start_date,
            "end_date": end_date,
            "data": all_data
        }
    
    def get_financial_reports(
        self,
        stock_code: str,
        year: int,
        quarter: Optional[int] = None
    ) -> Dict:
        """
        取得財務報表資料
        
        Args:
            stock_code: 股票代號
            year: 年份
            quarter: 季度（1-4），None 表示年報
            
        Returns:
            Dict: 財務報表資料
        """
        if quarter is None:
            endpoint = "exchangeReport/CORS/FINSTATEMENTS"
            params = {
                "query.stockCode": stock_code,
                "query.year": year
            }
        else:
            endpoint = "exchangeReport/CORS/QFINSTATEMENTS"
            params = {
                "query.stockCode": stock_code,
                "query.year": year,
                "query.quarter": quarter
            }
        
        return self.get(endpoint, params)
    
    def close(self):
        """關閉連線"""
        self.session.close()
    
    def __enter__(self):
        """Context manager 進入"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 退出"""
        self.close()
