"""
TWSE API 客戶端 - 使用正確的公開 API 端點
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import requests
import time
import json
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import config

logger = logging.getLogger(__name__)


class TWSSEAPIClient:
    """TWSE API 客戶端"""
    
    def __init__(self):
        """初始化客戶端"""
        self.base_url = "https://www.twse.com.tw"
        self.timeout = config.TWSE_API_TIMEOUT
        self.max_retries = config.TWSE_MAX_RETRIES
        self.session = self._create_session()
        self.last_request_time = 0
    
    def _create_session(self) -> requests.Session:
        """
        建立帶有重試機制的 requests session
        """
        session = requests.Session()
        
        # 設定請求頭 - TWSE 需要特定的 User-Agent
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.twse.com.tw/",
            "Origin": "https://www.twse.com.tw",
        })
        
        return session
    
    def _rate_limit(self):
        """實現速率限制"""
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.5:  # 至少間隔 0.5 秒
            time.sleep(0.5 - elapsed)
        self.last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5)
    )
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        """
        發送 GET 請求
        """
        self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"Fetching: {url} with params: {params}")
        
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                verify=True
            )
            
            logger.debug(f"Status Code: {response.status_code}")
            logger.debug(f"Response Content: {response.text[:500]}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                    logger.debug(f"Response text: {response.text}")
                    return {"data": []}
            else:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                response.raise_for_status()
        
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get_listed_companies(self) -> List[Dict]:
        """
        取得上市公司列表
        使用 TWSE 正式 API
        """
        endpoint = "/api/corp/corpsearchInfo"
        params = {
            "query.cond": "and",
            "query.type": "AND",
            "query.pageNumber": "1",
            "query.pageSize": "9999",
            "firstin": "true",
            "step": "1"
        }
        
        try:
            logger.info("Fetching listed companies from TWSE API")
            result = self.get(endpoint, params)
            
            if result and "data" in result:
                companies = []
                for item in result.get("data", []):
                    companies.append({
                        "stock_code": item.get("code", ""),
                        "company_name": item.get("name", ""),
                        "isin_code": item.get("isin", ""),
                        "industry_name": item.get("industryName", ""),
                        "market_type": item.get("marketType", ""),
                        "listing_date": item.get("listingDate", ""),
                    })
                logger.info(f"Retrieved {len(companies)} companies")
                return companies
            return []
        except Exception as e:
            logger.error(f"Failed to get listed companies: {e}")
            return []
    
    def get_stock_price(self, stock_code: str, date: Optional[str] = None) -> Dict:
        """
        取得股票即時價格
        使用 TWSE 正式 API
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        else:
            # 即使接收到 YYYY-MM-DD 格式，轉換為 YYYYMMDD
            date = date.replace("-", "")
        
        endpoint = "/api/data/dailystock"
        params = {
            "date": date,
            "stockCode": stock_code
        }
        
        try:
            logger.info(f"Fetching stock price for {stock_code} on {date}")
            result = self.get(endpoint, params)
            
            if result and result.get("data"):
                data = result["data"][0] if isinstance(result["data"], list) else result["data"]
                
                return {
                    "stock_code": stock_code,
                    "trading_date": date,
                    "opening_price": float(data.get("open", 0)),
                    "highest_price": float(data.get("high", 0)),
                    "lowest_price": float(data.get("low", 0)),
                    "closing_price": float(data.get("close", 0)),
                    "price_change": float(data.get("change", 0)),
                    "price_change_percent": float(data.get("changePercent", 0)),
                    "trading_volume": int(float(data.get("volume", 0))),
                    "trading_value": int(float(data.get("value", 0))),
                }
            return {}
        except Exception as e:
            logger.error(f"Failed to get stock price for {stock_code}: {e}")
            return {}
    
    def get_historical_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        取得歷史行情資料
        使用 TWSE 正式 API
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        all_data = []
        current = start
        
        logger.info(f"Fetching historical data for {stock_code} from {start_date} to {end_date}")
        
        while current <= end:
            # 跳過魯半日天（星期天）
            if current.weekday() == 6:
                current += timedelta(days=1)
                continue
            
            date_str = current.strftime("%Y%m%d")
            
            try:
                data = self.get_stock_price(stock_code, date_str)
                if data:
                    all_data.append(data)
            except Exception as e:
                logger.debug(f"No data for {stock_code} on {date_str}: {e}")
            
            current += timedelta(days=1)
        
        logger.info(f"Retrieved {len(all_data)} records")
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
        取得財务報表
        使用 TWSE 正式 API
        """
        endpoint = "/api/data/financialreport"
        
        if quarter is None:
            params = {
                "stockCode": stock_code,
                "year": year,
                "reportType": "annual"
            }
        else:
            params = {
                "stockCode": stock_code,
                "year": year,
                "quarter": quarter,
                "reportType": "quarter"
            }
        
        try:
            logger.info(f"Fetching financial reports for {stock_code}")
            result = self.get(endpoint, params)
            
            if result and result.get("data"):
                data = result["data"]
                return {
                    "stock_code": stock_code,
                    "year": year,
                    "quarter": quarter,
                    "report_type": "季報" if quarter else "年報",
                    "data": data
                }
            return {}
        except Exception as e:
            logger.error(f"Failed to get financial reports: {e}")
            return {}
    
    def close(self):
        """關閉連線"""
        self.session.close()
    
    def __enter__(self):
        """Context manager 進入"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 退出"""
        self.close()
