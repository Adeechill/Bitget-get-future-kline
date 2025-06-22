# Bitget K-Line Data Fetcher

這是一個 Python 套件，能讓您輕鬆地從 Bitget 交易所下載指定交易對的合約產品歷史 K 線（Candlestick）數據。

您可以將其作為一個命令列工具直接使用，也可以在您自己的 Python 專案中匯入並使用其功能。此工具透過 Bitget 官方 V2 API 獲取數據，支援下載完整的歷史記錄。

## 功能特性

- **雙重使用模式**：既可作為獨立的 **命令列工具**，也可作為 **Python 函式庫** 整合至您的專案中。
- **完整的歷史數據**：可指定一個開始日期，將自動分頁下載從該日期至今的所有 K 線數據。
- **高度自訂化**：支援自訂交易對、K 線時間粒度及產品類型。
- **CSV 輸出**：將下載的數據儲存為通用的 CSV 格式，方便後續分析。
- **穩健的錯誤處理**：包含 API 請求錯誤、網路問題及頻率限制的處理。

## 安裝指南

1.  複製此專案至您的本地環境：
    ```bash
    git clone https://github.com/Adeechill/Bitget-get-future-kline.git
    cd Bitget-get-future-kline
    ```

2.  建議建立並啟用一個 Python 虛擬環境。

3.  使用 pip 進行安裝。此指令將會把 `bitget-fetcher` 套件安裝到您的環境中，並自動處理 `requests` 和 `pandas` 的相依性：
    ```bash
    pip install .
    ```

## 使用方法

### 方案一：作為 Python 函式庫使用

安裝完成後，您可以在自己的 Python 腳本中匯入並使用 `bitget-fetcher`。

```python
import pandas as pd
from bitget_fetcher import get_all_historical_data

# --- 範例 1: 獲取 BTCUSDT 從 2023-01-01 至今的日線數據 ---
print("正在下載 BTCUSDT 日線數據...")
btc_daily_data = get_all_historical_data(
    symbol="BTCUSDT",
    granularity="1D",
    product_type="usdt-futures",
    start_date_str="2023-01-01"
)

if not btc_daily_data.empty:
    print("下載成功！")
    print(btc_daily_data.head())
    # 將數據儲存為 CSV
    btc_daily_data.to_csv("btc_daily_from_2023.csv", index=False)


# --- 範例 2: 獲取 ETHUSDT 最新的 5 分鐘線數據 (不指定開始日期) ---
print("\n正在下載 ETHUSDT 5分鐘線數據...")
eth_5m_data = get_all_historical_data(
    symbol="ETHUSDT",
    granularity="5m",
    product_type="usdt-futures"
)

if not eth_5m_data.empty:
    print("下載成功！")
    print(eth_5m_data.tail())

```

### 方案二：作為命令列工具使用

安裝後，`bitget-fetcher` 指令將變為可用。

- `symbol` (必須): 交易對，例如 `BTCUSDT`。
- `granularity` (必須): K 線的時間粒度。支援的值包括 `1m`, `5m`, `1H`, `4H`, `1D`, `1W` 等。
- `--start_date` (可選): 獲取數據的開始日期 (YYYY-MM-DD)。若省略，則只會下載最新的一批數據。
- `--output` (可選): 輸出 CSV 檔案的路徑。若省略，則儲存在當前目錄，檔名為 `SYMBOL_GRANULARITY_PRODUCTTYPE.csv`。

**命令列範例:**

```bash
# 下載 ETHUSDT 從 2023-01-01 至今的全部日線 (1D) 數據
bitget-fetcher ETHUSDT 1D --start_date 2023-01-01

# 下載 XRPUSDT 的 5 分鐘線數據，並儲存至 data/xrp_data.csv
bitget-fetcher XRPUSDT 5m --start_date 2024-01-01 --output data/xrp_data.csv
```

## API 參考

本工具使用 Bitget V2 API 的 `history-candles` 端點。更多關於 API 的詳細資訊，請參閱 [Bitget 官方 API 文件](https://www.bitget.com/api-doc/contract/market/Get-History-Candle-Data)。

## 免責聲明

- 本軟體非 Bitget 官方提供。
- 所有下載的數據均直接來自 Bitget API，其準確性與即時性由交易所保證。
- 請遵守 Bitget 的 API 使用條款。
- 使用本工具所產生的任何風險，作者概不負責。 