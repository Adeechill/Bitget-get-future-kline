import requests
import json
import pandas as pd
from datetime import datetime, timezone
import time

def get_bitget_historical_klines(symbol, granularity, product_type, start_time=None, end_time=None, limit=200):
    """
    獲取 Bitget 交易所單批次的歷史 K 線數據。

    參數:
    symbol (str): 交易對，例如 "BTCUSDT"。
    granularity (str): K 線粒度。
        有效值: "1m", "3m", "5m", "15m", "30m", "1H", "4H", "6H", "12H", 
                 "1D", "3D", "1W", "1M", 以及 UTC 時區的對應值 (例如 "1Dutc")。
    product_type (str): 產品類型。
        有效值: "usdt-futures", "coin-futures", "usdc-futures" 等。
    start_time (int, optional): 查詢 K 線的開始時間（Unix 時間戳，毫秒）。
    end_time (int, optional): 查詢 K 線的結束時間（Unix 時間戳，毫秒）。
    limit (int, optional): 返回的最大數據條數，預設 200，最大也為 200。

    返回:
    pandas.DataFrame: 包含歷史 K 線數據的 DataFrame，如果請求失敗則返回 None。
    """
    base_url = "https://api.bitget.com/api/v2/mix/market/history-candles"
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "productType": product_type,
        "limit": limit
    }

    if start_time:
        params["startTime"] = start_time
    if end_time:
        params["endTime"] = end_time

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # 檢查 HTTP 請求是否成功

        data = response.json()

        if data["code"] == "00000" and data["data"]:
            df = pd.DataFrame(data["data"], columns=[
                "timestamp", "open", "high", "low", "close", "volume", "quote_volume"
            ])
            # 將時間戳轉換為可讀的日期時間格式
            df["timestamp"] = pd.to_datetime(pd.to_numeric(df["timestamp"]), unit='ms')
            # 將價格和成交量列轉換為數值類型
            numeric_cols = ["open", "high", "low", "close", "volume", "quote_volume"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col])
            
            # 按照時間戳升序排序
            df = df.sort_values(by="timestamp").reset_index(drop=True)
            return df
        else:
            # 如果 API 回傳無數據 (例如，查詢的時間範圍內沒有K線)，也算是正常情況
            if data.get('msg') == 'no data':
                return pd.DataFrame() # 返回空的 DataFrame
            print(f"API 請求失敗或無數據: {data.get('msg', '未知錯誤')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"請求發生錯誤: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 解析錯誤: {e}")
        return None

def get_all_historical_data(symbol, granularity, product_type, start_date_str=None, verbose=True):
    """
    獲取指定交易對從某個日期開始的所有歷史 K 線數據。

    參數:
    symbol (str): 交易對。
    granularity (str): K 線粒度。
    product_type (str): 產品類型。
    start_date_str (str, optional): 開始日期字串 "YYYY-MM-DD"。若為 None，則只獲取最近一批數據。
    verbose (bool, optional): 是否在控制台打印下載進度。預設為 True。

    返回:
    pandas.DataFrame: 包含所有歷史 K 線數據的 DataFrame。
    """
    all_klines_df = []
    
    # 將開始日期轉換為毫秒時間戳
    start_timestamp = None
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        start_timestamp = int(start_date.timestamp() * 1000)

    # 從當前時間開始，向前獲取數據
    end_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    
    if verbose:
        print("開始下載歷史數據...")
    
    while True:
        if verbose:
            print(f"正在獲取 {datetime.fromtimestamp(end_timestamp / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} 之前的數據...")
        
        df_batch = get_bitget_historical_klines(symbol, granularity, product_type, end_time=end_timestamp)
        
        # 檢查是否成功獲取數據或是否已無數據可取
        if df_batch is None or df_batch.empty:
            if verbose:
                print("已獲取所有可用數據，或 API 返回錯誤。")
            break
            
        all_klines_df.append(df_batch)
        
        # 更新下一次查詢的結束時間戳
        oldest_timestamp_in_batch = df_batch["timestamp"].iloc[0].timestamp() * 1000
        end_timestamp = int(oldest_timestamp_in_batch) - 1 # 減 1 毫秒避免重複

        # 如果指定了開始日期，檢查是否已達到
        if start_timestamp and oldest_timestamp_in_batch <= start_timestamp:
            if verbose:
                print("已達到指定的開始日期。")
            break
        
        # 尊重 API 的頻率限制
        time.sleep(0.2) 

    if not all_klines_df:
        return pd.DataFrame()

    # 合併所有數據幀並進行整理
    final_df = pd.concat(all_klines_df).drop_duplicates().sort_values(by="timestamp").reset_index(drop=True)
    
    # 如果有指定開始日期，過濾掉早於該日期的數據
    if start_timestamp:
        final_df = final_df[final_df['timestamp'] >= pd.to_datetime(start_timestamp, unit='ms', utc=True)]
        
    return final_df.reset_index(drop=True) 