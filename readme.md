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
# 程式專案設定檔配置&自動排程v3.1

## 程式下載
1. 進入ubuntu，切換到使用者根目錄下`/home/<user>`，此篇範例為`home/junting/`
2. `git clone https://github.com/JunTingLin/stock-analysis.git`


## python 環境建置
:::warning
這裡使用miniconda建置環境，假如想使用.venv建置可自行參考repo的套件依賴安裝
:::

1. 更新包管理器並安裝所需工具
```
sudo apt update
sudo apt install wget bzip2 -y
```

2. 下載並運行 Miniconda 安裝腳本
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```
+ 這邊會請您閱讀條款，一直按Enter之後選擇Yes
+ 它會詢問miniconda 安裝位置，預設是`/home/<user>/miniconda3`
+ 它詢問您是否希望自動初始化 conda，這將在啟動時自動激活 conda 基本環境並改變命令提示符，這裡我是選擇No，自己配置會比較清楚

3. 初始化 Conda
+ 先手動激活 conda。`source ~/miniconda3/etc/profile.d/conda.sh`
+ 這指令會修改您的 shell 配置文件（如 ~/.bashrc ），以便在每次打開終端時自動加載 conda。`conda init`

4. 創建並配置 Conda 環境
```
conda create -n stock-analysis python=3.10.16
conda activate stock-analysis
cd stock-analysis
conda env update --file environment_linux.yml --name stock-analysis
```

5. 驗證環境配置
```
conda activate stock-analysis
conda list
```

## 前置設定要求
1. 憑證檔案準備
根據使用的券商，準備對應的憑證檔案：
Shioaji（永豐金證券）：
+ 憑證檔案：.pfx 格式
+ 建議路徑：/home/<user>/stock-analysis/config/<user>_Sinopac.pfx
+ 取得方式：從永豐金證券-[金鑰與憑證申請](https://sinotrade.github.io/zh/tutor/prepare/token/)

2. config.yaml 配置
在專案根目錄建立 config.yaml，包含以下設定：
必要欄位說明:
```
# 全域環境變數
env:
  FINLAB_API_TOKEN: "your_finlab_token"  # FinLab API Token

# 使用者配置
users:
  <user_name>:  # 例如：junting, alan
    <broker_name>:  # 例如：fugle, shioaji
      env:
        # 券商 API 認證資訊（依券商不同）
        # Fugle 範例：
        FUGLE_MARKET_API_KEY: "your_api_key"
        FUGLE_ACCOUNT: "your_account"
        FUGLE_ACCOUNT_PASSWORD: "your_password"
        FUGLE_CERT_PASSWORD: "your_cert_password"
        FUGLE_CONFIG_PATH: "/path/to/config.ini"
        PYTHON_KEYRING_BACKEND: "keyrings.cryptfile.cryptfile.CryptFileKeyring"

        # Shioaji 範例：
        SHIOAJI_API_KEY: "your_api_key"
        SHIOAJI_SECRET_KEY: "your_secret_key"
        SHIOAJI_CERT_PERSON_ID: "your_id"
        SHIOAJI_CERT_PATH: "/path/to/cert.pfx"
        SHIOAJI_CERT_PASSWORD: "your_cert_password"

      constant:
        rebalance_safety_weight: 0.1  # 再平衡安全權重（0.0-1.0）
        strategy_class_name: "YourStrategyClassName"  # 策略類別名稱
```
config.yaml 範例：
```
env:
  FINLAB_API_TOKEN: "PG323UEltzZHHyhR4wg+OIGmrII..."

users:
  junting:
    shioaji:
      env:
        SHIOAJI_API_KEY: "4rJhFzsocEFDtCBb75Mku2..."
        SHIOAJI_SECRET_KEY: "425iBxJdmR1rEsn47kee66..."
        SHIOAJI_CERT_PERSON_ID: "A123456789"
        SHIOAJI_CERT_PATH: "/home/junting/stock-analysis/config/junting_Sinopac.pfx"
        SHIOAJI_CERT_PASSWORD: "A123456789"
      constant:
        rebalance_safety_weight: 0.3
        strategy_class_name: "RAndDManagementStrategy"
```
    

## 啟動Dashboard (linux systemd)
1. 創建一個新的 systemd 服務單元文件。`sudo vim /etc/systemd/system/flask_stock.service`

2. 在文件中添加以下內容:
```
[Unit]
Description=Flask Server Stock Analysis
After=network.target

[Service]
User=junting
WorkingDirectory=/home/junting/stock-analysis
Environment="PATH=/home/junting/miniconda3/envs/stock-analysis/bin"
ExecStart=/home/junting/miniconda3/envs/stock-analysis/bin/gunicorn -w 4 -b 0.0.0.0:5000 dashboard:server
Restart=always

[Install]
WantedBy=multi-user.target
```
:::warning
注意: 這裡User和路徑內的<user>請自行替換
:::

3. 啟動並啟用服務
```
sudo systemctl start flask_stock # 啟動
sudo systemctl enable flask_stock # 開機自動啟動
```
    
4. 檢查 systemd 服務的狀態。`sudo systemctl status flask_stock`

-- 補充--
    
5. 重新啟動服務
```
sudo systemctl daemon-reload
sudo systemctl restart flask_stock
```
6. 停止服務
```
sudo systemctl stop flask_stock
sudo systemctl disable flask_stock
```
    



    
## 啟動自動排程 (linux cronjob)

1. 在終端中，執行以下命令來編輯 crontab 配置。`crontab -e`
    
2. 添加定時任務
`0 20 * * * /path/to/your/order.sh`
+ `0 20 `表示每天的 20:00（晚上八點）。
+ `* * * `表示每天的每個月的每個月份。
+ `/path/to/your/order.sh` 是您腳本的完整路徑。
    
3. Example
    
CronJob 1 - fetch.sh
```
30 20 * * * /home/junting/stock-analysis/fetch.sh --user_name=junting --broker_name=shioaji >> /home/junting/stock-analysis/fetch.log 2>&1
```
參數說明：
| 參數 | 必需 | 預設值 | 說明 |
|------|------|--------|------|
| `--user_name` | 是 | 無 | 使用者名稱，需與 `config.yaml` 一致 |
| `--broker_name` | 是 | 無 | 券商名稱（`fugle` 或 `shioaji`） |
    
CronJob 2 - backtest.sh 
```
00 20 * * * /home/junting/stock-analysis/backtest.sh --strategy_class_name=RAndDManagementStrategy >> /home/junting/stock-analysis/backtest.log 2>&1
```
**參數說明：**

| 參數 | 必需 | 預設值 | 說明 |
|------|------|--------|------|
| `--strategy_class_name` | 是 | 無 | 策略類別名稱（例如：`RAndDManagementStrategy`） |

    
CronJob 3 - order.sh
```
00 08 * * * /home/junting/stock-analysis/order.sh --user_name=junting --broker_name=shioaji >> /home/junting/stock-analysis/order.log 2>&1
        
00 13 * * * /home/junting/stock-analysis/order.sh --user_name=junting --broker_name=shioaji --extra_bid_pct=0.01 >> /home/junting/stock-analysis/order.log 2>&1
```
 **參數說明：**

| 參數 | 必需 | 預設值 | 說明 |
|------|------|--------|------|
| `--user_name` | 是 | 無 | 使用者名稱，需與 `config.yaml` 一致 |
| `--broker_name` | 是 | 無 | 券商名稱（`fugle` 或 `shioaji`） |
| `--extra_bid_pct` | 否 | 0 | 額外加價百分比（例如：0.01 代表加價 1%） |
| `--view_only` | 否 | false | 僅查看模式，不實際下單 |


4. 檢查 Crontab 列表。`crontab -l`
        

## 可用策略類別名稱列表
| 策略類別名稱 | 檔案位置 | 說明 |
|-------------|---------|------|
| `AlanTWStrategyC` | [alan_tw_strategy_C.py](strategy_class/alan_tw_strategy_C.py) | Alan 策略 C |
| `AlanTWStrategyE` | [alan_tw_strategy_E.py](strategy_class/alan_tw_strategy_E.py) | Alan 策略 E |
| `PeterWuStrategy` | [peterwu_tw_strategy.py](strategy_class/peterwu_tw_strategy.py) | Peter Wu 策略 |
| `RAndDManagementStrategy` | [r_and_d_management_strategy.py](strategy_class/r_and_d_management_strategy.py) | Finlab官方-研發管理策略 |
| `TibetanMastiffTWStrategy` | [tibetanmastiff_tw_strategy.py](strategy_class/tibetanmastiff_tw_strategy.py) | Finlab-藏敖策略 |