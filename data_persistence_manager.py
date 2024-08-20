import pandas as pd
import os

class DataPersistenceManager:
    def save_to_pkl(self, data, pkl_path):

        # 確保目錄存在
        dir_name = os.path.dirname(pkl_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # 保存數據到pkl
        if os.path.exists(pkl_path):
            existing_df = pd.read_pickle(pkl_path)
            updated_df = pd.concat([existing_df, data], ignore_index=True)
            updated_df = updated_df.drop_duplicates(subset=["日期時間"], keep="last")
            updated_df = updated_df.reset_index(drop=True)
        else:
            updated_df = data

        updated_df.to_pickle(pkl_path)
        return updated_df

    def load_from_pkl(self, pkl_path):
        if os.path.exists(pkl_path):
            return pd.read_pickle(pkl_path)
        else:
            return pd.DataFrame()
        
    def save_finlab_report(self, report, report_save_path):
        dir_name = os.path.dirname(report_save_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        report.display(save_report_path=report_save_path)
