# Stock Analysis - Docker 部署指南 (客戶版)

> 🚀 這是最簡單的部署方式,無需安裝 Python 環境,只需 Docker!

---

## 📋 目錄
- [前置需求](#前置需求)
- [快速開始](#快速開始)
- [配置說明](#配置說明)
- [排程設定](#排程設定)
- [常用指令](#常用指令)
- [疑難排解](#疑難排解)
- [附錄](#附錄)

---

## 前置需求

### 1. 安裝 Docker Desktop

| 作業系統 | 下載連結 |
|---------|---------|
| **Windows/Mac** | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **Linux** | 執行以下指令: |

```bash
# Linux 安裝 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 驗證安裝

```bash
docker --version
# 應顯示: Docker version 24.x.x

docker-compose --version
# 應顯示: Docker Compose version v2.x.x
```

### 3. 準備憑證檔案

準備永豐金證券的憑證檔案:

| 券商 | 憑證格式 | 取得方式 |
|------|---------|---------|
| **永豐金證券 (Shioaji)** | `.pfx` | [金鑰與憑證申請](https://sinotrade.github.io/zh/tutor/prepare/token/) |

---

## 快速開始 (3 步驟)

### 步驟 1: 下載專案

```bash
# 使用 Git 下載
git clone https://github.com/JunTingLin/stock-analysis.git
cd stock-analysis

```

---

### 步驟 2: 準備配置檔

#### 2.1 編輯 `config/config.yaml`

```yaml
# 全域環境變數
env:
  FINLAB_API_TOKEN: "你的_FinLab_API_Token"  # 從 FinLab 取得

# 使用者配置
users:
  你的名字:  # 例如: junting, alan
    shioaji:  # 券商名稱: shioaji
      env:
        # 永豐金證券 (Shioaji) 設定
        SHIOAJI_API_KEY: "你的_API_Key"
        SHIOAJI_SECRET_KEY: "你的_Secret_Key"
        SHIOAJI_CERT_PERSON_ID: "身分證字號"
        SHIOAJI_CERT_PATH: "/app/config/你的憑證.pfx"  # 容器內路徑
        SHIOAJI_CERT_PASSWORD: "憑證密碼"

      constant:
        rebalance_safety_weight: 0.3  # 再平衡安全權重 (0.0-1.0)
        strategy_class_name: "RAndDManagementStrategy"  # 策略類別名稱 (見附錄)
```

**參數說明:**

| 參數 | 必填 | 說明 | 範例 |
|------|------|------|------|
| `FINLAB_API_TOKEN` | ✅ | FinLab API Token | `"PG323UEltzZ..."` |
| `SHIOAJI_API_KEY` | ✅ | 永豐 API Key | `"4rJhFzsocE..."` |
| `SHIOAJI_SECRET_KEY` | ✅ | 永豐 Secret Key | `"425iBxJdmR..."` |
| `SHIOAJI_CERT_PERSON_ID` | ✅ | 身分證字號 | `"A123456789"` |
| `SHIOAJI_CERT_PATH` | ✅ | 憑證路徑 (容器內) | `"/app/config/junting_Sinopac.pfx"` |
| `SHIOAJI_CERT_PASSWORD` | ✅ | 憑證密碼 | `"A123456789"` |
| `rebalance_safety_weight` | ✅ | 安全權重 (0-1) | `0.3` (30%) |
| `strategy_class_name` | ✅ | 策略類別 | 見 [附錄 A](#附錄-a-可用的策略類別) |

#### 2.2 放入憑證檔案

```bash
# 將憑證檔案複製到 config 目錄
# Windows
copy C:\path\to\your_cert.pfx config\

# Linux/Mac
cp /path/to/your_cert.pfx config/
```

**⚠️ 注意:**
- 憑證檔名必須與 `config.yaml` 中的 `CERT_PATH` 一致
- 例如: `SHIOAJI_CERT_PATH: "/app/config/junting_Sinopac.pfx"` → 檔名為 `junting_Sinopac.pfx`

#### 2.3 調整排程設定 (可選)

如果要自訂排程時間,編輯 `docker/crontab`:

```bash
# 預設排程:
# 20:30 - 抓取帳務資料
# 20:00 - 執行回測
# 08:00 - 早盤下單
# 13:00 - 尾盤下單 (加價 1%)

# 可修改為:
# 0 9 * * * ...  # 改成早上 9:00 下單
```

**Crontab 格式說明:**
```
分 時 日 月 週 指令
│ │ │ │ │
│ │ │ │ └─── 星期幾 (0-7, 0和7都是星期日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小時 (0-23)
└─────────── 分鐘 (0-59)

範例:
0 8 * * *     # 每天 08:00
30 13 * * 1-5 # 週一到週五 13:30
0 */2 * * *   # 每 2 小時
```

---

### 步驟 3: 啟動服務

```bash
# 啟動所有服務 (Dashboard + 排程)
docker-compose up -d --build

# 查看啟動狀態
docker-compose ps
```

**預期輸出:**
```
NAME                 IMAGE                  STATUS        PORTS
stock-analysis-app   stock-analysis:latest  Up (healthy)  0.0.0.0:5000->5000/tcp
stock-scheduler      stock-analysis:latest  Up
```

- **Dashboard主頁**: http://localhost:5000
- **回測報告瀏覽**: http://localhost:5000/assets/

---

## 配置說明

### 目錄結構

```
stock-analysis/
├── config/
│   ├── config.yaml          ← 📝 你需要編輯這個
│   └── your_cert.pfx        ← 🔐 你的憑證放這裡
├── logs/                    ← 📊 日誌輸出位置
│   ├── order.log           # 下單日誌
│   ├── fetch.log           # 抓取日誌
│   └── backtest.log        # 回測日誌
├── data_prod.db             ← 💾 資料庫 (自動建立)
├── assets/                  ← 📈 回測報告 HTML
├── docker-compose.yml       ← ⚙️ Docker 配置
└── Dockerfile
```

### 服務說明

| 服務名稱 | 用途 | 端口 |
|---------|------|------|
| `stock-analysis-app` | Dashboard 網頁介面 | 5000 |
| `stock-scheduler` | 定時排程執行器 | - |

### Volume 掛載說明

| 本地路徑 | 容器路徑 | 用途 | 模式 |
|---------|---------|------|------|
| `./config/` | `/app/config/` | 配置檔和憑證 | 只讀 `:ro` |
| `./logs/` | `/app/logs/` | 日誌輸出 | 讀寫 |
| `./data_prod.db` | `/app/data_prod.db` | SQLite 資料庫 | 讀寫 |

---

## 排程設定

預設排程內容 (`docker/crontab`):

```bash
# 1. 每天 20:30 - 抓取當日持股和帳戶資訊
30 20 * * * cd /app && python -m jobs.scheduler --user_name=junting --broker_name=shioaji

# 2. 每天 20:00 - 執行回測
0 20 * * * cd /app && python -m jobs.backtest_executor --strategy_class_name=RAndDManagementStrategy

# 3. 每天 08:00 - 早盤下單
0 8 * * * cd /app && python -m jobs.order_executor --user_name=junting --broker_name=shioaji

# 4. 每天 13:00 - 尾盤下單 (加價 1%)
0 13 * * * cd /app && python -m jobs.order_executor --user_name=junting --broker_name=shioaji --extra_bid_pct=0.01
```

### 排程參數說明

#### `jobs.scheduler` - 抓取帳務資料

| 參數 | 必需 | 預設值 | 說明 |
|------|------|--------|------|
| `--user_name` | ✅ | 無 | 使用者名稱 (需與 `config.yaml` 一致) |
| `--broker_name` | ✅ | 無 | 券商名稱 (`shioaji`) |

**範例:**
```bash
python -m jobs.scheduler --user_name=alan --broker_name=shioaji
```

#### `jobs.backtest_executor` - 執行回測

| 參數 | 必需 | 預設值 | 說明 |
|------|------|--------|------|
| `--strategy_class_name` | ✅ | 無 | 策略類別名稱 (見 [附錄 A](#附錄-a-可用的策略類別)) |

**範例:**
```bash
python -m jobs.backtest_executor --strategy_class_name=PrisonRabbitStrategy
```

#### `jobs.order_executor` - 執行下單

| 參數 | 必需 | 預設值 | 說明 |
|------|------|--------|------|
| `--user_name` | ✅ | 無 | 使用者名稱 (需與 `config.yaml` 一致) |
| `--broker_name` | ✅ | 無 | 券商名稱 (`shioaji`) |
| `--extra_bid_pct` | ❌ | `0` | 額外加價百分比 (例如 `0.01` = 加價 1%) |
| `--view_only` | ❌ | `false` | 僅查看模式,不實際下單 |

**範例:**
```bash
# 一般下單
python -m jobs.order_executor --user_name=junting --broker_name=shioaji

# 加價 1% 下單 (尾盤)
python -m jobs.order_executor --user_name=junting --broker_name=shioaji --extra_bid_pct=0.01

# 只看不下單 (測試模式)
python -m jobs.order_executor --user_name=junting --broker_name=shioaji --view_only
```

---

## 常用指令

### 服務管理

```bash
# 啟動服務
docker-compose up -d --build

# 停止服務
docker-compose down

# 重新啟動服務
docker-compose restart

# 查看服務狀態
docker-compose ps

# 查看資源使用
docker stats stock-analysis-app stock-scheduler
```

### 日誌查看

```bash
# 查看所有日誌 (即時)
docker-compose logs -f

# 只看 Dashboard 日誌
docker-compose logs -f stock-analysis

# 只看排程日誌
docker-compose logs -f stock-scheduler

# 查看最近 100 行
docker-compose logs --tail=100

# 查看本地日誌檔案
tail -f logs/order.log
tail -f logs/fetch.log
tail -f logs/backtest.log
```

### 手動執行指令

```bash
# 進入容器
docker exec -it stock-analysis-app bash

# 手動執行下單 (測試模式)
docker exec -it stock-analysis-app python -m jobs.order_executor \
  --user_name=junting \
  --broker_name=shioaji \
  --view_only

# 手動執行回測
docker exec -it stock-analysis-app python -m jobs.backtest_executor \
  --strategy_class_name=RAndDManagementStrategy

# 手動抓取帳務資料
docker exec -it stock-analysis-app python -m jobs.scheduler \
  --user_name=junting \
  --broker_name=shioaji
```

### 更新程式

```bash
# 1. 拉取最新程式碼
git pull

# 2. 重新建立並啟動
docker-compose up -d --build

# 3. 確認更新成功
docker-compose ps
docker-compose logs --tail=50
```

### 清理資源

```bash
# 停止並移除容器
docker-compose down

# 移除容器 + 未使用的映像
docker-compose down --rmi local

# 清理所有未使用的 Docker 資源 (謹慎使用!)
docker system prune -a
```

---


## 附錄

### 附錄 A: 可用的策略類別

在 `config.yaml` 的 `strategy_class_name` 欄位可使用以下策略:

| 策略類別名稱 | 檔案位置 | 說明 | 來源 |
|-------------|---------|------|------|
| `AlanTWStrategyACE` | [alan_tw_strategy_ACE.py](strategy_class/alan_tw_strategy_ACE.py) | Alan 策略 (A\|C\|E) | 自訂 |
| `PeterWuStrategy` | [peterwu_tw_strategy.py](strategy_class/peterwu_tw_strategy.py) | Peter Wu 策略 | 自訂 |
| `RAndDManagementStrategy` | [r_and_d_management_strategy.py](strategy_class/r_and_d_management_strategy.py) | 研發管理大亂鬥 | FinLab 官方 |
| `RevenuePriceStrategy` | [tibetanmastiff_tw_strategy.py](strategy_class/tibetanmastiff_tw_strategy.py) | 藏敖策略 | FinLab 官方 |

**範例配置:**

```yaml
users:
  junting:
    shioaji:
      constant:
        strategy_class_name: "AlanTWStrategyACE"  # 使用 Alan 策略 ACE 組合
```

---



