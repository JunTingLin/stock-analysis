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
    + Cronjob 1 - fetech.sh 帳務資料抓取: 獲取成交明細、庫存明細、銀行餘額、交割款 → 紀錄 → 資料庫
    + Cronjob 2 - backtest.sh 回測獨立報表: FinLab 資料 → 策略回測 → 產生html報告 → File Browser(root/assets/)
    + Cronjob 3 - order.sh 下單流程: FinLab 資料 → 策略回測 → 下單（調整持倉） → 紀錄 → 資料庫
    + Web Dashboard: 展示下單資訊、帳戶資金水位變化圖、每月實際回報率圖以及 FinLab 回測報告。

<img width="1917" height="1075" alt="image" src="https://github.com/user-attachments/assets/b5adbb8c-740b-4269-bd68-f93cf3c5a873" />



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

# 保留最新版 Flask 與 Dash 的相容性
pip install flask-autoindex

# Unix 系統專用：安裝 gunicorn
conda install gunicorn

```

## 注意事項

+ FinLab 套件原碼修改
目前 finlab 安裝版本為 1.3.0，請手動修改其原始碼：
    1. **下單日誌修改**：到 finlab 套件中 `online/order_executor.py`（例如：`C:\Users\junting\anaconda3\envs\stock-analysis\lib\site-packages\finlab\online\order_executor.py`）檔案內，找到 `execute_orders` 函數，將第 690 行的 `print(f'{action_str:<11} {o["stock_id"]:10} X {round(abs(o["quantity"]), 3):<10} @ {price_string:<11} {extra_bid_text} {order_condition_str}')` 語句改為 `logger.info`，以便 `jobs/order_executor.py` 能夠正確抓取下單資訊供後續處理。

    2. **警示股日誌修改**：在同一個檔案 `online/order_executor.py` 中，找到 `show_alerting_stocks` 函數（約第 538-568 行），將第 563、567 行的 `print` 語句改為 `logger.info`：
        - 第 563 行：將 `print(f"買入 {sid} {quantity[sid]:>5} 張 - 總價約 {total_amount:>15.2f}")` 改為 `logger.info(f"買入 {sid} {quantity[sid]:>5} 張 - 總價約 {total_amount:>15.2f}")`
        - 第 567 行：將 `print(f"賣出 {sid} {quantity[sid]:>5} 張 - 總價約 {total_amount:>15.2f}")` 改為 `logger.info(f"賣出 {sid} {quantity[sid]:>5} 張 - 總價約 {total_amount:>15.2f}")`

        這樣可以讓警示股資訊寫入 log，方便後續進行圈存處理。

+ 警示股自動圈存功能
    + 系統會自動檢測下單部位中的警示股、處置股、全額交割股
    + 針對永豐券商（shioaji）自動執行圈存：
        + 買入：使用 `reserve_earmarking` 進行預收款項
        + 賣出：使用 `reserve_stock` 進行預收股票
    + 採用策略模式設計（`utils/reservation_handler.py`），未來可擴展支援其他券商
    + Fugle 券商目前不支援圈存 API，會記錄警告訊息提醒手動處理

+ 多券商配置
在根目錄新增 config.yaml ，並正確設定finlab API、使用者、各券商（如玉山、永豐）的連線與交易參數。


## 部署
[股票自動交易手冊](https://hackmd.io/@RPTu-Li-R66a9lr4Fb9qEg/BJpNu1QSC/%2FSy7PQ0BB0)
