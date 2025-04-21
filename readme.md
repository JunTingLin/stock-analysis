# Stock Analysis

此專案利用 FinLab 提供的即時財經資料，設計股票交易策略並進行歷史回測。透過自動化流程，每日定時執行回測與下單，並將結果以表格與圖表形式展示於 Dashboard 上。Dashboard 內容包含詳細下單資訊、帳戶資金水位變化圖及每月實際回報率圖表。

## 功能
+ 策略開發與回測
    + 利用 FinLab 的即時資料進行股票策略設計與歷史回測。
+ 多用戶與多券商支援
    + 支援多使用者，並可根據需求設定不同券商（如玉山、永豐），相關參數可於 config.yaml 中調整。
+ 自動化下單
    + crontab排程自動執行交易，透過玉山富果 API、Shioaji永豐API 進行下單。
+ 批次任務與 Dashboard
    + Cronjob 1 - 下單流程: FinLab 資料 → 策略回測 → 下單（調整持倉） → 紀錄 → 資料庫
    + Cronjob 2 - 帳務資料抓取: 獲取成交明細、庫存明細、銀行餘額、交割款 → 紀錄 → 資料庫
    + Web Dashboard: 展示下單資訊、帳戶資金水位變化圖、每月實際回報率圖以及 FinLab 回測報告。

![image](https://github.com/user-attachments/assets/b640a032-bd2f-4278-8429-b617804cf4f9)

## 依賴

+ 資料與交易相關
    + finlab：取得即時財經資料與回測分析（僅能用 pip 安裝）
    + shioaji[speed]：永豐證券下單（僅能用 pip 安裝）
    + fugle-trade：玉山證券下單（僅能用 pip 安裝）
    + keyring：管理與儲存敏感資訊

    + openpyxl：處理 Excel 文件
    + ta-lib：技術分析庫，提供多種股票技術指標
    + lxml：HTML 解析工具（用於 FinLab 中 order_executer.show_alerting_stocks() 依賴 pd.read_html(res.text)）
    + pandas：資料處理與分析

+ Web 與 Dashboard
    + dash：建立交互式 Web 應用
    + dash-bootstrap-components：搭配 Bootstrap 的 UI 組件
    + Flask-AutoIndex：自動生成目錄列表（僅能用 pip 安裝）
    + gunicorn：WSGI HTTP 伺服器（僅適用於 Unix 系統）

+ 其他
    + IPython：互動式 Python 介面
    + pyyaml：讀取配置文件


## 安裝

建議使用 conda 環境（推薦方式）
1. 建立並啟用環境
```bash
conda create -n stock-analysis python=3.10.16
conda activate stock-analysis
```

2. 更新環境
已有提供的 conda 環境 YAML 檔([environment_linux.yml](./environment_linux.yml), [environment_window.yml](./environment_window.yml))，可使用下列指令更新環境：
```bash
conda env update --file environment_linux.yml --name stock-analysis
```

或者逐一安裝

```
# 安裝僅提供 pip 的套件
pip install finlab shioaji[speed] fugle-trade

# 使用 conda 安裝其他依賴（部分從 conda-forge channel）
conda install -c conda-forge openpyxl keyring ta-lib lxml ipython dash dash-bootstrap-components pyyaml pandas

# Unix 系統專用：安裝 gunicorn
conda install gunicorn

```

## 注意事項

+ FinLab 套件原碼修改
目前 finlab 安裝版本為 1.2.23，請手動修改其原始碼：
到 finlab 套件中 online/order_executor.py 檔案內，找到 execute_orders 函數，將第 679 行的 print 語句改為 logger.info，以便 jobs/order_executor.py 能夠正確抓取下單資訊供後續處理。

+ 多券商配置
在根目錄新增 config.yaml ，並正確設定finlab API、使用者、各券商（如玉山、永豐）的連線與交易參數。


## 部署
[股票自動交易手冊](https://hackmd.io/@RPTu-Li-R66a9lr4Fb9qEg/BJpNu1QSC/%2FSy7PQ0BB0)
