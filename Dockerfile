# Multi-stage build for stock-analysis
FROM continuumio/miniconda3:latest AS builder

# 設定工作目錄
WORKDIR /app

# 複製環境配置檔
COPY environment_linux.yml .

# 建立 conda 環境
RUN conda env create -f environment_linux.yml && \
    conda clean -afy

# 最終 runtime image
FROM continuumio/miniconda3:latest

# 安裝必要的系統套件
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    curl \
    cron \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 從 builder 複製 conda 環境
COPY --from=builder /opt/conda/envs/stock-analysis /opt/conda/envs/stock-analysis

# 複製應用程式碼
COPY . .

# 複製並設定 crontab (處理 CRLF 和權限)
COPY docker/crontab /etc/cron.d/stock-cron
RUN dos2unix /etc/cron.d/stock-cron && \
    chmod 0644 /etc/cron.d/stock-cron && \
    crontab /etc/cron.d/stock-cron

# 註: logs/, config/, assets/, data_prod.db 會由 docker-compose 的 volumes 掛載

# 設定環境變數
ENV PATH=/opt/conda/envs/stock-analysis/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Taipei

# 激活 conda 環境
SHELL ["/bin/bash", "-c"]
RUN echo "source activate stock-analysis" > ~/.bashrc

# 暴露 Flask 端口
EXPOSE 5000

# 預設啟動 dashboard
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "dashboard:server"]
