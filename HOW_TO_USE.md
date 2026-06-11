# 🚀 TWSE 資料整合系統 - 完整使用教程

本文件提供詳細的使用指南，幫助你快速上手 TWSE 資料整合系統。

## 📋 目錄

1. [環境安裝](#環境安裝)
2. [快速開始](#快速開始)
3. [基本使用](#基本使用)
4. [執行範例](#執行範例)
5. [API 參考](#api-參考)
6. [常見用途](#常見用途)
7. [進階功能](#進階功能)
8. [故障排除](#故障排除)

---

## 環境安裝

### 前置需求

- Python 3.8 或更高版本
- pip 套件管理器
- Git（用於複製倉庫）

### 安裝步驟

#### 步驟 1：複製倉庫

```bash
git clone https://github.com/ShangYuChiang/twse-data-integration.git
cd twse-data-integration
```

#### 步驟 2：建立虛擬環境

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 步驟 3：安裝依賴套件

```bash
pip install -r requirements.txt
```

#### 步驟 4：設定環境變數（可選）

```bash
cp .env.example .env
# 編輯 .env 檔案，如需要修改設定
```

### 驗證安裝

```bash
# 進入 Python 互動模式
python

# 執行以下程式碼
from src.data_fetcher import TWDataFetcher
fetcher = TWDataFetcher()
print("安裝成功！")
fetcher.close()
```

---

## 快速開始

### 最簡單的範例

建立 `demo.py`：

```python
from src.data_fetcher import TWDataFetcher

# 初始化
fetcher = TWDataFetcher(cache_enabled=True)

try:
    # 取得 TSMC 的股票價格
    price = fetcher.get_stock_price('2330')
    print(f"TSMC 收盤價: {price['closing_price']}")
    print(f"漲跌: {price['price_change']} ({price['price_change_percent']}%)")
    
finally:
    fetcher.close()
```

執行：
```bash
python demo.py
```

---

## 基本使用

### 1. 初始化資料取得器

```python
from src.data_fetcher import TWDataFetcher

# 啟用快取（推薦）
fetcher = TWDataFetcher(cache_enabled=True, cache_type="memory")

# 或不使用快取
fetcher = TWDataFetcher(cache_enabled=False)
```

### 2. 取得上市公司資料

```python
# 取得所有上市公司
companies = fetcher.get_listed_companies()

print(f"總共 {len(companies)} 家上市公司\n")

# 顯示前 5 家
for company in companies[:5]:
    print(f"代號: {company['stock_code']}")
    print(f"名稱: {company['company_name']}")
    print(f"產業: {company['industry_name']}\n")
```

**返回資料結構:**
```python
{
    'stock_code': '2330',           # 股票代號
    'company_name': '台積電',       # 公司名稱
    'industry_name': '半導體業',    # 產業別
    'listing_date': '1994-06-30',  # 上市日期
    'market_type': '上市',          # 上市別
    'isin_code': 'TW0002330008'    # ISIN代碼
}
```

### 3. 取得股票即時價格

```python
# 取得 TSMC 今日的股票價格
stock_price = fetcher.get_stock_price('2330')

print(f"股票代號: {stock_price['stock_code']}")
print(f"交易日期: {stock_price['trading_date']}")
print(f"開盤價: {stock_price['opening_price']}")
print(f"最高價: {stock_price['highest_price']}")
print(f"最低價: {stock_price['lowest_price']}")
print(f"收盤價: {stock_price['closing_price']}")
print(f"漲跌: {stock_price['price_change']} ({stock_price['price_change_percent']}%)")
print(f"成交量: {stock_price['trading_volume']:,} 股")
print(f"成交值: {stock_price['trading_value']:,} (百元)")
```

**返回資料結構:**
```python
{
    'stock_code': '2330',
    'trading_date': '2024-06-11',
    'opening_price': 950.0,         # 開盤價
    'highest_price': 955.0,         # 最高價
    'lowest_price': 948.0,          # 最低價
    'closing_price': 952.0,         # 收盤價
    'price_change': 2.0,            # 漲跌價格
    'price_change_percent': 0.21,   # 漲跌百分比
    'trading_volume': 50000,        # 成交量（股）
    'trading_value': 4760000,       # 成交值（百元）
    'transaction_count': 25000      # 成交筆數
}
```

### 4. 取得歷史行情資料

```python
import pandas as pd

# 取得 2024 年 1 月至 6 月的行情
historical = fetcher.get_historical_data(
    stock_code='2330',
    start_date='2024-01-01',
    end_date='2024-06-30'
)

print(f"取得 {len(historical)} 筆資料")
print(f"\n前 5 筆:")
print(historical.head())

# 簡單統計
print(f"\n統計資訊:")
print(f"平均收盤價: {historical['closing_price'].mean():.2f}")
print(f"最高價: {historical['highest_price'].max():.2f}")
print(f"最低價: {historical['lowest_price'].min():.2f}")
print(f"總成交量: {historical['trading_volume'].sum():,} 股")
```

### 5. 取得財務報表資料

```python
# 取得 2023 年年報
financial = fetcher.get_financial_reports(
    stock_code='2330',
    year=2023,
    quarter=None  # None=年報，1-4=季報
)

print(f"【{financial['stock_code']} {financial['year']} 年財務報表】\n")
print("資產負債表:")
print(f"  總資產: {financial['total_assets']:,.0f}")
print(f"  總負債: {financial['total_liabilities']:,.0f}")
print(f"  股東權益: {financial['total_equity']:,.0f}\n")

print("損益表:")
print(f"  營業收入: {financial['revenue']:,.0f}")
print(f"  淨利: {financial['net_income']:,.0f}\n")

print("關鍵指標:")
print(f"  EPS: {financial['eps']:.2f}")
print(f"  ROE: {financial['roe']*100:.2f}%")
print(f"  ROA: {financial['roa']*100:.2f}%")
```

**返回資料結構:**
```python
{
    'stock_code': '2330',
    'year': 2023,
    'quarter': None,                  # None=年報，1-4=季報
    'report_type': '年報',
    'total_assets': 676000000000,     # 總資產
    'total_liabilities': 90000000000, # 總負債
    'total_equity': 586000000000,     # 股東權益
    'revenue': 675900000000,          # 營業收入
    'net_income': 205000000000,       # 淨利
    'eps': 78.9,                      # 每股盈餘
    'roe': 0.35,                      # 股東權益報酬率
    'roa': 0.28                       # 資產報酬率
}
```

### 6. 關閉連線

```python
# 完成後記得關閉
fetcher.close()
```

---

## 執行範例

### 範例 1：基本用法

```bash
python examples/basic_usage.py
```

**功能:**
- 取得上市公司列表
- 取得即時股價
- 取得歷史行情
- 取得財務報表
- 測試快取機制

### 範例 2：歷史資料分析

```bash
python examples/historical_data.py
```

**功能:**
- 分析股票績效
- 計算波動率
- 計算報酬率
- 比較多支股票
- 移動平均線分析

### 範例 3：財務報表分析

```bash
python examples/financial_reports.py
```

**功能:**
- 分析公司財務健康
- 比較多家公司的財務指標
- 分析季度績效
- 評估獲利能力

---

## API 參考

### TWDataFetcher 類

#### 初始化

```python
fetcher = TWDataFetcher(
    cache_enabled: bool = True,      # 是否啟用快取
    cache_type: str = "memory"       # 快取類型："memory" 或 "redis"
)
```

#### 方法

##### `get_listed_companies(force_refresh=False)`

取得所有上市公司

```python
companies = fetcher.get_listed_companies()
# 返回: List[Dict]

# 強制重新取得（跳過快取）
companies = fetcher.get_listed_companies(force_refresh=True)
```

**參數:**
- `force_refresh` (bool): 是否強制重新取得，跳過快取

**返回:** List[Dict] - 上市公司列表

---

##### `get_stock_price(stock_code, date=None)`

取得股票即時價格

```python
# 取得今日價格
price = fetcher.get_stock_price('2330')

# 取得特定日期價格
price = fetcher.get_stock_price('2330', date='2024-06-11')
```

**參數:**
- `stock_code` (str): 股票代號（必要）
- `date` (str): 日期，格式 YYYY-MM-DD（可選，預設為今日）

**返回:** Dict - 股票價格資料

---

##### `get_historical_data(stock_code, start_date, end_date, force_refresh=False)`

取得歷史行情資料

```python
# 取得一個月的行情
historical = fetcher.get_historical_data(
    stock_code='2330',
    start_date='2024-05-01',
    end_date='2024-06-30'
)

# 返回 pandas DataFrame，可直接進行分析
print(historical.head())
print(historical['closing_price'].mean())
```

**參數:**
- `stock_code` (str): 股票代號
- `start_date` (str): 起始日期，格式 YYYY-MM-DD
- `end_date` (str): 結束日期，格式 YYYY-MM-DD
- `force_refresh` (bool): 是否強制重新取得

**返回:** pd.DataFrame - 歷史行情資料

---

##### `get_financial_reports(stock_code, year, quarter=None, force_refresh=False)`

取得財務報表

```python
# 取得 2023 年年報
financial = fetcher.get_financial_reports(
    stock_code='2330',
    year=2023
)

# 取得 2024 年第一季報
financial = fetcher.get_financial_reports(
    stock_code='2330',
    year=2024,
    quarter=1
)
```

**參數:**
- `stock_code` (str): 股票代號
- `year` (int): 年份
- `quarter` (int): 季度（1-4），None 表示年報
- `force_refresh` (bool): 是否強制重新取得

**返回:** Dict - 財務報表資料

---

##### `clear_cache()`

清空快取

```python
fetcher.clear_cache()
```

---

##### `close()`

關閉連線

```python
fetcher.close()
```

---

## 常見用途

### 用途 1：監控多支股票

```python
from src.data_fetcher import TWDataFetcher

fetcher = TWDataFetcher()

# 要監控的股票代號
watchlist = ['2330', '2454', '3105', '2412']  # TSMC, 聯發科, 群創, 中華電

print("股票代號\t公司名稱\t\t收盤價\t漲跌\t漲跌%")
print("-" * 60)

for stock_code in watchlist:
    try:
        price = fetcher.get_stock_price(stock_code)
        # 這裡需要公司名稱，可從 get_listed_companies 取得
        print(f"{stock_code}\t{price['closing_price']:.2f}\t{price['price_change']:.2f}\t{price['price_change_percent']:.2f}%")
    except Exception as e:
        print(f"{stock_code}\t取得失敗")

fetcher.close()
```

### 用途 2：計算股票報酬率

```python
import pandas as pd
from src.data_fetcher import TWDataFetcher

fetcher = TWDataFetcher()

# 計算過去 6 個月的報酬率
history = fetcher.get_historical_data('2330', '2024-01-01', '2024-06-30')

first_price = history.iloc[0]['closing_price']
last_price = history.iloc[-1]['closing_price']
return_pct = ((last_price - first_price) / first_price) * 100

print(f"期初價格: {first_price:.2f}")
print(f"期末價格: {last_price:.2f}")
print(f"報酬率: {return_pct:.2f}%")

fetcher.close()
```

### 用途 3：找出高 EPS 的公司

```python
from src.data_fetcher import TWDataFetcher

fetcher = TWDataFetcher()

companies = fetcher.get_listed_companies()
high_eps = []

for company in companies[:100]:  # 檢查前 100 家
    try:
        fin = fetcher.get_financial_reports(company['stock_code'], year=2023)
        if fin.get('eps', 0) > 5:  # EPS > 5
            high_eps.append({
                'code': company['stock_code'],
                'name': company['company_name'],
                'eps': fin['eps']
            })
    except:
        pass

# 按 EPS 排序
high_eps.sort(key=lambda x: x['eps'], reverse=True)

print("代號\t公司名稱\t\tEPS")
for item in high_eps[:10]:
    print(f"{item['code']}\t{item['name']}\t{item['eps']:.2f}")

fetcher.close()
```

### 用途 4：比較公司財務指標

```python
from src.data_fetcher import TWDataFetcher

fetcher = TWDataFetcher()

# 比較科技大廠
companies = ['2330', '2454', '3105']  # TSMC, 聯發科, 群創

print("公司\tEPS\tROE\tROA\t淨利率")
print("-" * 50)

for code in companies:
    try:
        fin = fetcher.get_financial_reports(code, year=2023)
        revenue = fin.get('revenue', 0)
        net_income = fin.get('net_income', 0)
        profit_margin = (net_income / revenue * 100) if revenue > 0 else 0
        
        print(f"{code}\t{fin['eps']:.2f}\t{fin['roe']*100:.2f}%\t{fin['roa']*100:.2f}%\t{profit_margin:.2f}%")
    except Exception as e:
        print(f"{code}\t錯誤: {e}")

fetcher.close()
```

### 用途 5：尋找股價低估的股票

```python
from src.data_fetcher import TWDataFetcher

fetcher = TWDataFetcher()

# 計算本益比（簡化版）
stock_code = '2330'
price = fetcher.get_stock_price(stock_code)
fin = fetcher.get_financial_reports(stock_code, year=2023)

if fin['eps'] > 0:
    # 假設 1 股 = 1 單位（實際需要考慮股票面額）
    pe_ratio = price['closing_price'] / fin['eps']
    print(f"本益比: {pe_ratio:.2f}x")
    
    if pe_ratio < 15:
        print("✓ 股票可能被低估")
    elif pe_ratio > 25:
        print("✗ 股票可能被高估")
    else:
        print("= 股票價格合理")

fetcher.close()
```

---

## 進階功能

### 快取管理

#### 啟用快取

```python
# 使用記憶體快取（推薦用於開發）
fetcher = TWDataFetcher(cache_enabled=True, cache_type="memory")

# 使用 Redis 快取（生產環境）
fetcher = TWDataFetcher(cache_enabled=True, cache_type="redis")
```

#### 快取設定

編輯 `.env`：
```env
CACHE_ENABLED=true
CACHE_TTL=3600           # 快取時間（秒）
CACHE_TYPE=memory        # memory 或 redis
REDIS_URL=redis://localhost:6379
```

#### 強制重新取得

```python
# 跳過快取，重新取得資料
companies = fetcher.get_listed_companies(force_refresh=True)
history = fetcher.get_historical_data('2330', '2024-01-01', '2024-06-30', force_refresh=True)
```

#### 清空快取

```python
# 清空所有快取
fetcher.clear_cache()
```

### 錯誤處理

```python
from src.data_fetcher import TWDataFetcher

fetcher = TWDataFetcher()

try:
    # 嘗試取得不存在的股票
    price = fetcher.get_stock_price('9999')
    
except ValueError as e:
    print(f"輸入錯誤: {e}")
    
except ConnectionError as e:
    print(f"連線錯誤: {e}")
    
except Exception as e:
    print(f"未知錯誤: {e}")
    
finally:
    fetcher.close()
```

### Context Manager（推薦）

```python
# 自動管理資源
with TWDataFetcher() as fetcher:
    price = fetcher.get_stock_price('2330')
    print(f"TSMC: {price['closing_price']}")
# 自動關閉連線
```

---

## 故障排除

### 問題 1：ModuleNotFoundError: No module named 'src'

**原因:** 虛擬環境未啟動或依賴未安裝

**解決方案:**
```bash
# 確認虛擬環境已啟動
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 重新安裝依賴
pip install -r requirements.txt
```

### 問題 2：requests.exceptions.ConnectionError

**原因:** 無法連接到 TWSE 伺服器

**解決方案:**
```bash
# 檢查網路連線
ping www.twse.com.tw

# 檢查防火牆設定
# 確保可以訪問 TWSE 網站
```

### 問題 3：返回空資料

**原因:** 股票代號錯誤或資料不存在

**解決方案:**
```python
# 先確認股票代號
companies = fetcher.get_listed_companies()
valid_codes = [c['stock_code'] for c in companies]

if '2330' in valid_codes:
    # 代號有效
    price = fetcher.get_stock_price('2330')
else:
    # 代號無效
    print("無效的股票代號")
```

### 問題 4：快取問題

**清空快取:**
```python
fetcher.clear_cache()

# 或強制重新取得
companies = fetcher.get_listed_companies(force_refresh=True)
```

---

## 常見問題 (FAQ)

**Q: 資料更新頻率是多少？**

A: TWSE 資料一般在交易日下午 15:30 更新。如需即時資料，建議不使用快取或設定較短的 TTL。

**Q: 可以取得即時報價嗎？**

A: 目前 API 提供的是日終資料，不提供盤中即時報價。

**Q: 支援多線程嗎？**

A: 支援。每個線程應使用獨立的 `TWDataFetcher` 實例。

**Q: 可以離線使用嗎？**

A: 不行，需要持續的網路連接才能取得資料。

**Q: 有 API 頻率限制嗎？**

A: TWSE 有頻率限制。建議使用快取以減少 API 呼叫。

---

## 進一步幫助

- 查看 [README.md](./README.md) 了解專案概況
- 查看 [examples/](./examples/) 獲得更多範例
- 查看 [USAGE.md](./USAGE.md) 獲得更詳細的文檔
- 提交 [Issue](https://github.com/ShangYuChiang/twse-data-integration/issues) 報告問題

---

**祝你使用愉快！** 🎉
