# Stock Analysis

此專案旨在利用 FinLab 提供的即時財經資料，設計股票交易策略並進行歷史回測。透過自動化流程，每天定期執行回測與自動下單，並將結果以表格或是圖表呈現在dashboard上。dashboard包含詳細的下單資訊、帳戶水位變化圖表以及每月帳戶實際回報率的圖表。

## 功能
+ 使用 FinLab 即時財經資料進行股票策略開發與歷史回測
+ 支援多使用者多券商(玉山、永豐)，可在config.yaml中設定
+ 自動執行每日交易，透過玉山富果 API 進行實時下單
+ 包含兩個批次任務(cronjob)和 web儀表版(dashboard)
    + cronjob1-下單: finlab資料 --> 策略回測 --> 下單(調整持倉) --> 紀錄 --> database
    + cronjob2-獲取帳務資料: 獲取成交明細、庫存明細、銀行餘額、交割款 --> 紀錄 --> database
    + dashboard-網頁: 顯示下單資訊、帳戶資金水位變化圖表、每月實際回報率圖表、FinLab 每日回測報告

## 依賴
以下是專案中使用的主要套件：

- `finlab`：獲取即時財經資料並進行回測分析(僅能用pip安裝)
- `openpyxl`：用於處理 Excel 文件
- `shioaji[speed]`: 永豐證券下單(僅能用pip安裝)
- `fugle-trade`：玉山證券下單(僅能用pip安裝)
- `keyring`：管理和儲存敏感信息

- `ta-lib`：技術分析庫，用於股票策略分析
- `lxml`：處理 HTML 解析，FinLab 的 `order_executer.show_alerting_stocks()` 函數的`pd.read_html(res.text)`依賴此套件
- `IPython`：互動式 Python 介面

- `gunicorn`：WSGI HTTP 伺服器，用於生產環境下的 Web 服務(only for Unix subsystem)

- `dash`：用於生成交互式 Web 應用
- `dash-bootstrap-components`：用於生成 Bootstrap 組件

- `pyyaml`：用於讀取配置文件

⚠️ **提醒**：
目前finlab安裝的版本是1.2.21，需要去finlab的套件原始碼內的online\order_executor.py內的execute_orders函數內，將679行的print打印改為logger.info，這樣我這邊jobs\order_executor.py才能抓取到實際下單資訊以利後續。

## 部署
[股票自動交易手冊](https://hackmd.io/@RPTu-Li-R66a9lr4Fb9qEg/BJpNu1QSC/%2FSy7PQ0BB0)