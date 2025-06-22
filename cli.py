import argparse
import os
from bitget_fetcher import get_all_historical_data, get_bitget_historical_klines

def main():
    parser = argparse.ArgumentParser(description="下載 Bitget U本位合約的歷史 K 線數據。")
    parser.add_argument("symbol", type=str, help="交易對，例如：BTCUSDT")
    parser.add_argument("granularity", type=str, help="K 線粒度，例如：5m, 1H, 1D")
    parser.add_argument("--product_type", type=str, default="usdt-futures", help="產品類型，預設為 'usdt-futures'")
    parser.add_argument("--start_date", type=str, default=None, help="獲取數據的開始日期，格式：YYYY-MM-DD。若不指定，則獲取最近的 200 條數據。")
    parser.add_argument("--output", type=str, help="儲存數據的 CSV 檔案路徑。若不指定，則預設以 'symbol_granularity.csv' 格式命名。")

    args = parser.parse_args()

    # 決定輸出檔案名稱
    if args.output:
        output_file = args.output
    else:
        output_file = f"{args.symbol}_{args.granularity}_{args.product_type}.csv"
    
    print(f"--- 任務設定 ---")
    print(f"交易對: {args.symbol}")
    print(f"K線粒度: {args.granularity}")
    print(f"產品類型: {args.product_type}")
    print(f"開始日期: {'從最早的可用數據開始' if args.start_date else '僅獲取最新一批'}")
    print(f"輸出檔案: {output_file}")
    print(f"------------------\n")

    if args.start_date:
        # 獲取從指定日期開始的所有歷史數據
        df_klines = get_all_historical_data(args.symbol, args.granularity, args.product_type, args.start_date)
    else:
        # 僅獲取最新一批數據
        print("正在獲取最新一批 K 線數據...")
        df_klines = get_bitget_historical_klines(args.symbol, args.granularity, args.product_type)

    if df_klines is not None and not df_klines.empty:
        # 建立目錄 (如果不存在)
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 儲存到 CSV
        df_klines.to_csv(output_file, index=False)
        
        print(f"\n成功獲取 {len(df_klines)} 條數據，並已儲存至 {output_file}")
        print("\n--- 數據預覽 (前 5 條) ---")
        print(df_klines.head())
        print("\n--- 數據預覽 (後 5 條) ---")
        print(df_klines.tail())
    else:
        print("未能獲取 K 線數據，或指定範圍內無數據。")


if __name__ == "__main__":
    main() 