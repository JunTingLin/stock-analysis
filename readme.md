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

## 手冊
[Stock Analysis - Docker 部署指南 (客戶版)](https://hackmd.io/@RPTu-Li-R66a9lr4Fb9qEg/SkQDaPzyWg)