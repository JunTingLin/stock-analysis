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

✅ **完成!** 現在可以訪問 Dashboard:
- **主頁**: http://localhost:5000
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
30 20 * * * cd /app && python -m jobs.fetch_account --user_name=junting --broker_name=shioaji

# 2. 每天 20:00 - 執行回測
0 20 * * * cd /app && python -m jobs.backtest --strategy_class_name=RAndDManagementStrategy

# 3. 每天 08:00 - 早盤下單
0 8 * * * cd /app && python -m jobs.order_executor --user_name=junting --broker_name=shioaji

# 4. 每天 13:00 - 尾盤下單 (加價 1%)
0 13 * * * cd /app && python -m jobs.order_executor --user_name=junting --broker_name=shioaji --extra_bid_pct=0.01
```

### 排程參數說明

#### `jobs.fetch_account` - 抓取帳務資料

| 參數 | 必需 | 預設值 | 說明 |
|------|------|--------|------|
| `--user_name` | ✅ | 無 | 使用者名稱 (需與 `config.yaml` 一致) |
| `--broker_name` | ✅ | 無 | 券商名稱 (`shioaji`) |

**範例:**
```bash
python -m jobs.fetch_account --user_name=alan --broker_name=shioaji
```

#### `jobs.backtest` - 執行回測

| 參數 | 必需 | 預設值 | 說明 |
|------|------|--------|------|
| `--strategy_class_name` | ✅ | 無 | 策略類別名稱 (見 [附錄 A](#附錄-a-可用的策略類別)) |

**範例:**
```bash
python -m jobs.backtest --strategy_class_name=PrisonRabbitStrategy
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
docker exec -it stock-analysis-app python -m jobs.backtest \
  --strategy_class_name=RAndDManagementStrategy

# 手動抓取帳務資料
docker exec -it stock-analysis-app python -m jobs.fetch_account \
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

## 疑難排解

### 問題 1: 容器啟動失敗

**現象:**
```bash
$ docker-compose ps
NAME                 STATUS
stock-analysis-app   Exited (1)
```

**排查步驟:**

```bash
# 1. 查看詳細錯誤
docker-compose logs stock-analysis

# 2. 常見原因及解決方法:
```

| 錯誤訊息 | 原因 | 解決方法 |
|---------|------|---------|
| `FileNotFoundError: config.yaml` | 配置檔不存在 | 確認 `config/config.yaml` 存在 |
| `yaml.scanner.ScannerError` | YAML 格式錯誤 | 檢查縮排和語法 (用 [YAML Lint](http://www.yamllint.com/) 驗證) |
| `No such file: cert.pfx` | 憑證檔案路徑錯誤 | 確認憑證檔案在 `config/` 目錄下 |
| `Invalid API Token` | API Token 錯誤或過期 | 檢查 `FINLAB_API_TOKEN` 是否正確 |

---

### 問題 2: Dashboard 無法訪問

**現象:** 訪問 http://localhost:5000 沒有回應

**排查步驟:**

```bash
# 1. 確認容器狀態
docker-compose ps
# 應顯示: Up (healthy)

# 2. 確認端口是否被佔用
# Windows
netstat -ano | findstr 5000

# Linux/Mac
lsof -i :5000

# 3. 檢查防火牆設定
# 確保端口 5000 允許連線

# 4. 如果端口被佔用,修改 docker-compose.yml
ports:
  - "8080:5000"  # 改用 8080 端口
```

---

### 問題 3: Healthcheck 顯示 unhealthy

**現象:**
```bash
$ docker-compose ps
NAME                 STATUS
stock-analysis-app   Up (unhealthy)
```

**排查步驟:**

```bash
# 1. 查看容器日誌
docker-compose logs stock-analysis

# 2. 檢查 Gunicorn 是否啟動成功
docker exec -it stock-analysis-app curl http://localhost:5000

# 3. 如果是啟動慢導致,等待 40 秒後自動恢復
# (healthcheck 有 start_period: 40s)

# 4. 手動重啟
docker-compose restart stock-analysis
```

---

### 問題 4: 排程沒有執行

**現象:** 到了排程時間,但沒有看到日誌或下單

**排查步驟:**

```bash
# 1. 進入 scheduler 容器檢查
docker exec -it stock-scheduler bash

# 2. 查看 cron 是否運行
ps aux | grep cron
# 應該看到: cron -f

# 3. 查看 crontab 列表
crontab -l

# 4. 檢查 crontab 檔案格式 (CRLF 問題)
cat -A /etc/cron.d/stock-cron
# 行尾應該是 $ 而不是 ^M$

# 5. 手動執行排程指令測試
cd /app
python -m jobs.order_executor --user_name=junting --broker_name=shioaji --view_only

# 6. 查看排程執行日誌
tail -f /app/logs/order.log
```

---

### 問題 5: 憑證檔案找不到

**錯誤訊息:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/app/config/cert.pfx'
```

**解決方法:**

```bash
# 1. 確認憑證檔案確實存在
ls -la config/

# 2. 確認檔名完全一致 (包含大小寫)
# config.yaml 中:
SHIOAJI_CERT_PATH: "/app/config/junting_Sinopac.pfx"
# 實際檔案:
config/junting_Sinopac.pfx  # ✅ 正確
config/Junting_Sinopac.pfx  # ❌ 大小寫不符

# 3. 確認路徑是容器內路徑 (開頭是 /app/config/)
# ✅ 正確: "/app/config/cert.pfx"
# ❌ 錯誤: "D:/config/cert.pfx"
# ❌ 錯誤: "./config/cert.pfx"
```

---

### 問題 6: 資料庫鎖定錯誤

**錯誤訊息:**
```
sqlite3.OperationalError: database is locked
```

**原因:** 多個程序同時存取 SQLite 資料庫

**解決方法:**

```bash
# 1. 檢查是否有多個程序在運行
docker exec -it stock-analysis-app ps aux | grep python

# 2. 停止所有服務後重啟
docker-compose down
docker-compose up -d --build

# 3. 如果問題持續,備份並重建資料庫
cp data_prod.db data_prod.db.backup
rm data_prod.db
docker-compose restart
```

---

## 附錄

### 附錄 A: 可用的策略類別

在 `config.yaml` 的 `strategy_class_name` 欄位可使用以下策略:

| 策略類別名稱 | 檔案位置 | 說明 | 來源 |
|-------------|---------|------|------|
| `AlanTWStrategyC` | [alan_tw_strategy_C.py](strategy_class/alan_tw_strategy_C.py) | Alan 策略 C | 自訂 |
| `AlanTWStrategyE` | [alan_tw_strategy_E.py](strategy_class/alan_tw_strategy_E.py) | Alan 策略 E | 自訂 |
| `PeterWuStrategy` | [peterwu_tw_strategy.py](strategy_class/peterwu_tw_strategy.py) | Peter Wu 策略 | 自訂 |
| `RAndDManagementStrategy` | [r_and_d_management_strategy.py](strategy_class/r_and_d_management_strategy.py) | **研發管理大亂鬥** | FinLab 官方 |
| `RevenuePriceStrategy` | [tibetanmastiff_tw_strategy.py](strategy_class/tibetanmastiff_tw_strategy.py) | **藏敖策略** | FinLab 官方 |

**範例配置:**

```yaml
users:
  junting:
    shioaji:
      constant:
        strategy_class_name: "RAndDManagementStrategy"  # 使用研發管理大亂鬥策略
```

---

### 附錄 B: 從傳統 Linux 部署遷移

如果你之前使用傳統的 Linux Cron 部署,遷移步驟:

#### 1. 停止舊服務

```bash
# 停止 Cron Jobs
crontab -e
# 註解掉或刪除所有 stock-analysis 相關排程

# 停止 Dashboard systemd 服務
sudo systemctl stop flask_stock
sudo systemctl disable flask_stock
```

#### 2. 備份資料

```bash
# 備份資料庫
cp /home/<user>/stock-analysis/data_prod.db ~/backup/

# 備份配置
cp /home/<user>/stock-analysis/config.yaml ~/backup/

# 備份日誌 (可選)
cp -r /home/<user>/stock-analysis/logs ~/backup/
```

#### 3. 啟動 Docker 版本

```bash
# 下載專案 (如果還沒有)
cd ~
git clone https://github.com/your-repo/stock-analysis.git
cd stock-analysis

# 複製舊配置
cp ~/backup/config.yaml config/
cp ~/backup/data_prod.db .

# 啟動
docker-compose up -d --build
```

#### 4. 驗證遷移

```bash
# 檢查服務狀態
docker-compose ps

# 檢查 Dashboard
curl http://localhost:5000

# 檢查日誌
docker-compose logs -f
```

---

### 附錄 C: 效能調校

#### Dashboard 工作程序數調整

如果 Dashboard 訪問量大,可調整 Gunicorn 工作程序數:

```yaml
# docker-compose.yml
services:
  stock-analysis:
    command: ["gunicorn", "-w", "8", "-b", "0.0.0.0:5000", "dashboard:server"]
    #                            ↑ 改成 8 個工作程序
```

**建議值:**
- CPU 核心數 × 2 + 1
- 例如: 4 核心 CPU → 4 × 2 + 1 = 9

#### 記憶體限制

```yaml
# docker-compose.yml
services:
  stock-analysis:
    deploy:
      resources:
        limits:
          memory: 2G  # 限制 2GB RAM
        reservations:
          memory: 1G  # 保證 1GB RAM
```

---

### 附錄 D: 安全注意事項

⚠️ **重要提醒:**

1. **配置檔安全**
   - `config.yaml` 包含敏感資訊,不要上傳到 GitHub
   - 已在 `.gitignore` 中排除
   - 如果不小心上傳,立即刪除並更換 API Token

2. **憑證保管**
   - `.pfx` 憑證檔案妥善保管
   - 定期更換憑證密碼
   - 不要分享給他人

3. **API Token**
   - 定期檢查 API Token 有效期
   - 不要在日誌中記錄 Token
   - 發現外洩立即重新生成

4. **容器安全**
   - 定期更新 Docker image: `docker-compose build --pull`
   - 不要以 root 身分運行容器
   - 定期檢查安全更新

---

### 附錄 E: 支援與回饋

#### 取得協助

- **GitHub Issues**: [專案 Issues 頁面](https://github.com/your-repo/stock-analysis/issues)
- **文件**: [完整開發文件](readme.md)
- **Email**: your-email@example.com

#### 回報問題

回報問題時,請提供:

1. 錯誤訊息截圖或完整日誌
2. `docker-compose ps` 輸出
3. `docker-compose logs` 輸出 (遮蔽敏感資訊)
4. 作業系統和 Docker 版本

```bash
# 收集診斷資訊
echo "=== Docker 版本 ===" > debug.log
docker --version >> debug.log
docker-compose --version >> debug.log

echo "\n=== 容器狀態 ===" >> debug.log
docker-compose ps >> debug.log

echo "\n=== 容器日誌 ===" >> debug.log
docker-compose logs --tail=100 >> debug.log
```

---

### 附錄 F: 與傳統部署的比較

| 項目 | 傳統 Linux 部署 | Docker 部署 |
|------|----------------|-------------|
| **環境準備** | ⭐⭐⭐⭐ (困難)<br>安裝 Miniconda、建立環境 | ⭐⭐ (簡單)<br>只需安裝 Docker |
| **修改套件** | ~~手動改 finlab 原始碼~~<br>(現已用 patcher 解決) | 自動 patch,無需手動 |
| **配置複雜度** | 高 (systemd + crontab) | 低 (docker-compose.yml) |
| **排程設定** | crontab + .sh 腳本 | docker/crontab |
| **Dashboard** | systemd service + Gunicorn | docker-compose |
| **更新流程** | git pull + 手動重啟 | `git pull && docker-compose up -d --build` |
| **跨平台** | 只支援 Linux | Windows/Linux/Mac |
| **資源隔離** | 無 | 完整隔離 |
| **客戶難度** | ⭐⭐⭐⭐ | ⭐⭐ |

---

## 總結

使用 Docker 部署的優勢:

✅ **簡單** - 3 個步驟即可完成部署
✅ **一致** - 環境完全一致,無版本衝突
✅ **隔離** - 不影響系統其他套件
✅ **快速** - 啟動和更新都很快
✅ **跨平台** - Windows/Linux/Mac 都能用

如有任何問題,請參考 [疑難排解](#疑難排解) 章節或聯繫技術支援。

---

**祝交易順利! 📈**
