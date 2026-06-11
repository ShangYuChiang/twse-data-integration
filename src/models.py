"""
資料模型 - 定義資料結構
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 上市公司資料 ====================

class Company(BaseModel):
    """上市公司資料"""
    stock_code: str = Field(..., description="股票代號")
    company_name: str = Field(..., description="公司名稱")
    isin_code: str = Field(..., description="ISIN代碼")
    market_type: str = Field(..., description="上市別 (上市/上櫃)")
    industry_code: str = Field(..., description="產業代碼")
    industry_name: str = Field(..., description="產業名稱")
    listing_date: str = Field(..., description="上市日期")
    cfi_code: Optional[str] = Field(None, description="CFI代碼")
    background: Optional[str] = Field(None, description="公司簡介")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stock_code": "2330",
                "company_name": "台積電",
                "isin_code": "TW0002330008",
                "market_type": "上市",
                "industry_code": "2401",
                "industry_name": "半導體業",
                "listing_date": "1994-06-30",
            }
        }


# ==================== 股價行情資料 ====================

class StockPrice(BaseModel):
    """即時股價資料"""
    stock_code: str = Field(..., description="股票代號")
    trading_date: str = Field(..., description="交易日期")
    opening_price: float = Field(..., description="開盤價")
    highest_price: float = Field(..., description="最高價")
    lowest_price: float = Field(..., description="最低價")
    closing_price: float = Field(..., description="收盤價")
    price_change: float = Field(..., description="漲跌價格")
    price_change_percent: float = Field(..., description="漲跌百分比")
    trading_volume: int = Field(..., description="成交量（股）")
    trading_value: int = Field(..., description="成交值（新台幣百元）")
    transaction_count: int = Field(..., description="成交筆數")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stock_code": "2330",
                "trading_date": "2024-06-11",
                "opening_price": 950.0,
                "highest_price": 955.0,
                "lowest_price": 948.0,
                "closing_price": 952.0,
                "price_change": 2.0,
                "price_change_percent": 0.21,
                "trading_volume": 50000,
                "trading_value": 4760000,
                "transaction_count": 25000,
            }
        }


class HistoricalData(BaseModel):
    """歷史行情資料"""
    stock_code: str = Field(..., description="股票代號")
    data: List[StockPrice] = Field(..., description="歷史資料列表")
    start_date: str = Field(..., description="起始日期")
    end_date: str = Field(..., description="結束日期")


# ==================== 財務報表資料 ====================

class FinancialStatement(BaseModel):
    """財務報表資料"""
    stock_code: str = Field(..., description="股票代號")
    year: int = Field(..., description="年份")
    quarter: Optional[int] = Field(None, description="季度（1-4）")
    report_type: str = Field(..., description="報表類型（年報/季報）")
    
    # 資產負債表
    total_assets: Optional[float] = Field(None, description="總資產")
    current_assets: Optional[float] = Field(None, description="流動資產")
    fixed_assets: Optional[float] = Field(None, description="固定資產")
    total_liabilities: Optional[float] = Field(None, description="總負債")
    current_liabilities: Optional[float] = Field(None, description="流動負債")
    total_equity: Optional[float] = Field(None, description="股東權益")
    
    # 損益表
    revenue: Optional[float] = Field(None, description="營業收入")
    cost_of_revenue: Optional[float] = Field(None, description="營業成本")
    gross_profit: Optional[float] = Field(None, description="毛利")
    operating_expenses: Optional[float] = Field(None, description="營業費用")
    operating_income: Optional[float] = Field(None, description="營業淨利")
    net_income: Optional[float] = Field(None, description="淨利")
    
    # 關鍵指標
    eps: Optional[float] = Field(None, description="每股盈餘（EPS）")
    roe: Optional[float] = Field(None, description="股東權益報酬率（ROE）")
    roa: Optional[float] = Field(None, description="資產報酬率（ROA）")
    debt_ratio: Optional[float] = Field(None, description="負債比率")
    
    # 報告日期
    report_date: Optional[str] = Field(None, description="報告日期")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stock_code": "2330",
                "year": 2023,
                "quarter": None,
                "report_type": "年報",
                "revenue": 675900000000,
                "net_income": 205000000000,
                "eps": 78.9,
                "roe": 0.35,
            }
        }


# ==================== API 回應模型 ====================

class APIResponse(BaseModel):
    """API 統一回應格式"""
    success: bool = Field(..., description="是否成功")
    code: int = Field(..., description="狀態碼")
    message: str = Field(..., description="訊息")
    data: Optional[dict] = Field(None, description="資料")
    timestamp: datetime = Field(default_factory=datetime.now, description="時間戳記")


class ErrorResponse(BaseModel):
    """錯誤回應"""
    success: bool = Field(False)
    code: int = Field(..., description="錯誤代碼")
    message: str = Field(..., description="錯誤訊息")
    details: Optional[dict] = Field(None, description="詳細資訊")
    timestamp: datetime = Field(default_factory=datetime.now)
