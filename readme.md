# Stock Analysis

此專案旨在利用 FinLab 提供的即時財經資料，設計股票交易策略並進行歷史回測。透過自動化流程，每天定期執行回測與自動下單，並將結果推送至用戶。報告中包含詳細的交易資訊、帳戶水位變化圖表以及每月帳戶實際回報率的圖表，所有資訊會彙整至 HTML 報表中，並透過 LINE Notify 推送報告連結。

## 功能
+ 使用 FinLab 即時財經資料進行股票策略開發與歷史回測
+ 自動執行每日交易，透過玉山富果 API 進行實時下單
+ 儲存交易資訊至資料庫，包含：
    + 當前持倉狀況
    + 調整後的持倉
    + 委託下單細節
    + 異常警示股信息
    + 帳戶餘額（扣除交割款）、持倉市值、總資產等
+ 生成的 HTML 報表內嵌有：
    + 交易資訊表格
    + 帳戶資金水位變化圖表
    + 每月實際回報率圖表
    + FinLab 每日回測報告
+ 通過 LINE Notify 推送報表連結，使用者可隨時點擊檢視最新的交易報告

## 依賴
以下是專案中使用的主要套件：

- `finlab`：獲取即時財經資料並進行回測分析
- `openpyxl`：用於處理 Excel 文件
- `fugle-trade`：玉山 Fugle 交易 API，用於股票下單
- `keyring`：管理和儲存敏感信息

- `ta-lib`：技術分析庫，用於股票策略分析
- `lxml`：處理 HTML 解析，FinLab 的 `order_executer.show_alerting_stocks()` 函數的`pd.read_html(res.text)`依賴此套件
- `IPython`：互動式 Python 介面
- `plotly`：用於生成圖表
- `pyyaml`：用於讀取與解析 YAML 格式的配置檔

- `flask`：輕量級 Web 框架，Flask-AutoIndex 依賴此套件
- `Flask-AutoIndex`：自動索引與公開資料夾報告
- `gunicorn`：WSGI HTTP 伺服器，用於生產環境下的 Web 服務

⚠️ **提醒**：
請確保 `numpy` 的版本低於 2.0 (`<2`)。`finlab` 依賴較舊版本的 `numpy`，若 `numpy` 被手動升級到 2.0 以上，可能會導致 `finlab` 無法正常運行。

## 部署
[股票自動交易手冊](https://hackmd.io/@RPTu-Li-R66a9lr4Fb9qEg/BJpNu1QSC/%2FSy7PQ0BB0)