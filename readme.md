# Stock Analysis

此專案旨在使用 [finlab](https://ai.finlab.tw/) 提供的即時財金資料，進行股票策略的製作和歷史回測，並實現全自動的股票交易。透過自動化流程，每天定期執行回測和交易，並將結果發送至 Flask 伺服器，該伺服器會將信息渲染成模板，發送給訂閱了該 Line Bot 的用戶。

## 功能
- 使用 finlab 即時財金資料進行股票策略開發
- 每日自動回測和交易執行
- 將交易結果（如目前持倉、明日調整的持倉、當前帳戶餘額、持倉市值和總市值等）發送至 Flask 伺服器
- 渲染模板並通過 Line Bot 發送通知給用戶
- 處理用戶事件，如用戶加入 Line Bot 後自動將其加入訂閱清單

## 依賴
- `finlab`：用於獲取財金資料
- `openpyxl`：用於處理 Excel 文件
- `fugle-trade`：玉山 Fugle 交易 API
- `keyring`：用於管理敏感信息

- `line-bot-sdk`：Line Bot SDK，用於與 Line Messaging API 交互
- `flask`：輕量級的 web 框架，用於構建 API 伺服器
- `gunicorn`：WSGI HTTP 伺服器，用於生產環境

## 布署
[股票自動交易手冊](https://hackmd.io/@RPTu-Li-R66a9lr4Fb9qEg/BJpNu1QSC/%2FSy7PQ0BB0)