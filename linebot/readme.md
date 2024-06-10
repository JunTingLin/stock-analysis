# Line Bot Notification Service

此資料夾包含一個 Flask 伺服器，用於接收來自 `stock-analysis` 專案的交易結果並通過 Line Bot 發送給用戶。除了推送通知外，該服務還處理用戶事件，例如新用戶加入 Line Bot。

## 功能
- 接收並處理來自 `stock-analysis` 的交易結果
- 渲染模板並通過 Line Bot 發送通知給用戶
- 處理用戶事件，如用戶加入 Line Bot 後自動將其加入訂閱清單

## 依賴
- `line-bot-sdk`：Line Bot SDK，用於與 Line Messaging API 交互
- `flask`：輕量級的 web 框架，用於構建 API 伺服器
- `gunicorn`：WSGI HTTP 伺服器，用於生產環境
