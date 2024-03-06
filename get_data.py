import pickle
import os
from finlab import data

def get_data_from_finlab(dataset_name, use_cache=False, cache_dir='cache_data', market=None, category=None):
    """
    根據條件從finlab獲取數據或從本地緩存讀取數據。
    
    Args:
        dataset_name (str): 從finlab獲取的數據集名稱。
        use_cache (bool): 是否使用本地緩存的數據。False表示從finlab獲取最新數據。
        cache_dir (str): 本地緩存數據的目錄路徑。
        market (str): 股票市場，例如 'TSE', 'OTC'。
        category (str or list): 股票類別，例如 ['水泥工業', '金融業']。
        
    Returns:
        pd.DataFrame: 獲取的數據。
    """
    cache_path = os.path.join(cache_dir, f'{dataset_name}.pkl')
    
    # 檢查是否使用本地緩存
    if use_cache and os.path.exists(cache_path):
        # 從本地文件反序列化讀取數據
        with open(cache_path, 'rb') as file:
            return pickle.load(file)
    else:
        # 根據市場和類別設置股票宇宙
        if market is not None or category is not None:
            with data.universe(market=market, category=category if category is not None else 'ALL'):
                df = data.get(dataset_name)
        else:
            # 從finlab獲取最新數據
            df = data.get(dataset_name)
        
        # 將數據序列化存儲到本地
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        try:
            with open(cache_path, 'wb') as file:
                pickle.dump(df, file)
        except Exception as e:
            print(f"Error saving data to {cache_path}: {e}")
            
        return df



if __name__ == "__main__":
    # 測試函數
    close = get_data_from_finlab("price:收盤價", use_cache=True)
    market_value = get_data_from_finlab("etl:market_value", use_cache=True)
    print(close.head())
    print(market_value.head())

