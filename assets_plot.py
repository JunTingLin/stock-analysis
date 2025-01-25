
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import calendar

class AssetsPlot:
    def __init__(self, df_assets):
        """
        df_assets 欄位預期:
        date, bank_balance, settlements, total_assets,
        adjusted_bank_balance, market_value
        """
        self.df = df_assets.copy()

    def plot(self, start_date=None, end_date=None):
        """
        回傳一個包含 2x1 區域 (上方: 資產趨勢; 下方: 月報酬熱力圖) 的 figure
        """
        print("Plotting assets trend and monthly return heatmap...")
        df = self.df

        # 1. 根據日期篩選
        if start_date:
            df = df[df['date'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['date'] <= pd.to_datetime(end_date)]

        # 若資料為空，直接回傳空 figure
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="No data in selected date range.")
            return fig

        # 2. 資產趨勢圖
        # 建立子圖: 2 rows, 1 col
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.15,
            subplot_titles=["Assets Trend", "Monthly Return Heatmap"]
        )

        # 上方折線
        fig.add_trace(
            go.Scatter(
                x=df["date"], y=df["adjusted_bank_balance"],
                mode="lines+markers",
                name="adjusted_bank_balance",
                marker_color="blue"
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df["date"], y=df["market_value"],
                mode="lines+markers",
                name="market_value",
                marker_color="orange"
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df["date"], y=df["total_assets"],
                mode="lines+markers",
                name="total_assets",
                marker_color="green"
            ),
            row=1, col=1
        )

        # 3. 月報酬率計算 => 以 "total_assets" 為基準
        #   step1: 取出每個月的期初 & 期末 (或每月最後一天)
        #   step2: (期末 - 期初)/期初 -> 月報酬
        df_monthly = df.copy()
        df_monthly["year"] = df_monthly["date"].dt.year
        df_monthly["month"] = df_monthly["date"].dt.month

        # 找每個 year-month 的期初(第一天)與期末(最後一天) 的 total_assets
        # 簡便作法：按 year、month 分組後，分別取 min 與 max
        grouped = df_monthly.groupby(["year", "month"])

        # 期初資產 (該月最早一天) => idxmin by date
        idx_first = grouped["date"].idxmin()
        # 期末資產 (該月最後一天) => idxmax by date
        idx_last = grouped["date"].idxmax()

        df_first = df_monthly.loc[idx_first, ["year", "month", "total_assets"]].rename(columns={"total_assets":"start_assets"})
        df_last  = df_monthly.loc[idx_last,  ["year", "month", "total_assets"]].rename(columns={"total_assets":"end_assets"})
        df_merge = pd.merge(df_first, df_last, on=["year","month"], how="inner")

        # 計算月報酬 (end_assets - start_assets)/start_assets
        df_merge["monthly_return"] = (df_merge["end_assets"] - df_merge["start_assets"]) / df_merge["start_assets"]

        # 4. 準備 heatmap 資料 (橫軸：月份 1~12；縱軸：年分)
        #   pivot table => index=year, columns=month, values=monthly_return
        pivot_table = df_merge.pivot(index="year", columns="month", values="monthly_return")

        # 先排序一下年分(小到大)
        pivot_table = pivot_table.sort_index(axis=0)
        # 月份欄位 => 1~12
        pivot_table = pivot_table.reindex(columns=range(1,13))

        # 轉成 2D list
        z_values = pivot_table.values
        y_labels = pivot_table.index.astype(str).tolist()   # 年
        x_labels = [calendar.month_abbr[m] for m in pivot_table.columns]  # 短月份名稱

        # 5. 在第二列繪製 Heatmap
        fig.add_trace(
            go.Heatmap(
                x=x_labels,
                y=y_labels,
                z=z_values,
                colorscale="RdBu",
                zmid=0,  # 中間 0 代表報酬率正負
                hovertemplate="Year: %{y}<br>Month: %{x}<br>Return: %{z:.2%}<extra></extra>",
                    colorbar=dict(
                    len=0.4,          # 調整 colorbar 的長度 (0~1 代表相對於整個 figure 的比例)
                    y=0.15,           # colorbar 的中心點在整個 figure 的哪個 y 座標(0=底,1=頂)
                    yanchor="middle", # 以 colorbar 的中間對齊 y=0.15
                    x=1.05,           # 默認 colorbar 在右側，你可以微調 x 以免疊到圖表
                    xanchor="left"
                )
            ),
            row=2, col=1
        )

        # 美化佈局
        fig.update_layout(
            width=1200, 
            height=800,
            title="Assets Trend & Monthly Return",
            showlegend=True
        )
        fig.update_yaxes(title="Assets", row=1, col=1)

        return fig
