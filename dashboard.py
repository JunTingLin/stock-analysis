import os
import re
import pandas as pd
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
from datetime import date

from assets_plot import AssetsPlot
from realized_pnl_plot import RealizedProfitLoss
from data_loader import fetch_assets_data, fetch_inventories_by_date, fetch_inventories_detail, fetch_orders_by_date, fetch_realized_pnl_data

app = Dash(__name__)

# 先從資料庫撈取已實現損益資料
df_pnl = fetch_realized_pnl_data()
rpl = RealizedProfitLoss(df_pnl)

df_assets = fetch_assets_data()
assets_plot = AssetsPlot(df_assets)

report_pattern = r'^(\d{4}-\d{2}-\d{2})\.html$'
report_dir = 'assets/report_finlab'


app.layout = html.Div([
    html.H1("My Trading Dashboard"),

    dcc.Tabs(id='main-tabs', value='tab-order', children=[

        dcc.Tab(label='下單', value='tab-order', children=[
            html.H3('下單 Page'),
            html.P("Select Order Date:"),
            dcc.DatePickerSingle(
                id='order-date-picker',
                min_date_allowed=date(2025, 1, 1),
                max_date_allowed=date(2030, 12, 31),
                date=date.today()
            ),
            dash_table.DataTable(
                id='orders-table',
                columns=[
                    {"name": "ID", "id": "id"},
                    {"name": "股票代號", "id": "stk_no"},
                    {"name": "股票名稱", "id": "stk_na"},
                    {"name": "股數", "id": "qty"},
                    {"name": "委託價", "id": "limit_price"},
                    {"name": "加減碼%", "id": "extra_bid_pct"},
                    {"name": "買賣", "id": "buy_sell"},
                    {"name": "Order Date", "id": "order_date"},
                    {"name": "Order Time", "id": "order_time"},
                ],
                data=[],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center'},
            ),
        ]),

        dcc.Tab(label='庫存', value='tab-inventory', children=[
            html.H3('庫存 Page'),
            html.P("Select Date:"),
            dcc.DatePickerSingle(
                id='inventory-date-picker',
                min_date_allowed=date(2025, 1, 1),
                max_date_allowed=date(2030, 12, 31),
                date=date.today()
            ),

            html.H4("庫存彙總 (inventories):"),
            dash_table.DataTable(
                id='inventories-table',
                columns=[
                    {"name": "ID", "id": "id"},
                    {"name": "股票代號", "id": "stk_no"},
                    {"name": "股票名稱", "id": "stk_na"},
                    {"name": "市值", "id": "value_mkt"},
                ],
                data=[],
                row_selectable="single",   # 允許使用者點選單列
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center'},
            ),

            html.Hr(),

            html.H4("庫存明細 (inventories_detail):"),
            dash_table.DataTable(
                id='inventories-detail-table',
                columns=[
                    {"name": "Detail ID", "id": "detail_id"},
                    {"name": "買賣方向", "id": "buy_sell"},
                    {"name": "價格", "id": "price"},
                    {"name": "股數", "id": "qty"},
                    {"name": "成交日期", "id": "t_date"},
                    {"name": "市值", "id": "value_mkt"},
                ],
                data=[],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center'},
            )
        ]),

        dcc.Tab(label='資產', value='tab-account', children=[
                    html.H3('資產 Page'),
                    html.P("Date Range:"),
                    dcc.DatePickerRange(
                        id='assets-date-picker-range',
                        min_date_allowed=date(1990, 1, 1),
                        max_date_allowed=date(2100, 12, 31),
                        initial_visible_month=date(2024, 1, 1),
                        start_date=date(2024, 1, 1),
                        end_date=date(2024, 12, 31)
                    ),
                    dcc.Graph(id="graph-assets")
                ]),

        dcc.Tab(label='對帳', value='tab-reconcile', children=[
            html.H3("Realized Profit Loss Page"),
            html.P("Date Range:"),
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(1990, 1, 1),
                max_date_allowed=date(2100, 12, 31),
                initial_visible_month=date(2024, 1, 1),
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            ),
            dcc.Graph(id="graph-pnl")
        ]),

        dcc.Tab(label='FinLab', value='tab-finlab', children=[
            html.H3("FinLab 報表"),
            html.P("Select Date:"),
            dcc.Dropdown(
                id="finlab-date-dropdown",
                options=[],  # 先給空, 等 callback 動態更新
                value=None
            ),
            html.Br(),
            html.Iframe(
                id='finlab-iframe',
                src="",
                width="100%",
                height="1000"
            )
        ]),
    ])
])

@app.callback(
    Output("orders-table", "data"),
    [Input("order-date-picker", "date"),
     Input("main-tabs", "value")]
)
def update_orders_table(selected_date, active_tab):
    if active_tab != "tab-order":
        return []
    if not selected_date:
        return []

    date_str = str(selected_date)
    df_orders = fetch_orders_by_date(date_str)
    if df_orders.empty:
        return []
    return df_orders.to_dict("records")




# 資產 頁籤: 選擇日期範圍 => 顯示資產趨勢圖
@app.callback(
    Output("graph-assets", "figure"),
    [Input('assets-date-picker-range', 'start_date'),
     Input('assets-date-picker-range', 'end_date'),
     Input('main-tabs', 'value')]
)
def update_assets_chart(start_date, end_date, active_tab):
    if active_tab == 'tab-account':
        return assets_plot.plot(start_date, end_date)
    return {}


# 庫存 頁籤: 選擇日期 => 顯示庫存表格
@app.callback(
    Output('inventories-table', 'data'),
    [Input('inventory-date-picker', 'date'),
     Input('main-tabs', 'value')]
)
def update_inventories_table(selected_date, active_tab):
    """
    當使用者改變 DatePickerSingle 或切換到「庫存」tab 時，
    就去 DB 撈該日期的庫存並顯示於 table
    """
    if active_tab != 'tab-inventory':
        return []
    if not selected_date:
        return []

    # 將 selected_date 轉成 str(YYYY-MM-DD)
    record_date_str = str(selected_date)
    df_inv = fetch_inventories_by_date(record_date_str)

    if df_inv.empty:
        return []

    # dash_table 期望 data 為 list of dict
    # DataFrame.to_dict("records") 會變成 [ {列1}, {列2}, ... ]
    return df_inv.to_dict("records")


# inventories-table 的某一列 => 顯示 detail
@app.callback(
    Output('inventories-detail-table', 'data'),
    [Input('inventories-table', 'selected_rows'),
     Input('inventories-table', 'data')],
    [State('main-tabs', 'value')]
)
def update_inventories_detail_table(selected_rows, table_data, active_tab):
    """
    selected_rows: 例如 [0], 代表使用者選了表格中的第 0 列
    table_data: 目前表格中的所有列的資料
    """
    if active_tab != 'tab-inventory':
        return []

    if not selected_rows:
        return []
    
    if not selected_rows or len(selected_rows) == 0:
        return []

    # 取出使用者點選的那一列
    idx = selected_rows[0]

    # 檢查 idx 是否超過 table_data 長度
    if idx >= len(table_data):
        return []

    row = table_data[idx]
    inventories_id = row["id"]  # inventories表中的 id

    # 呼叫 fetch_inventories_detail(inventories_id)
    df_detail = fetch_inventories_detail(inventories_id)
    if df_detail.empty:
        return []
    return df_detail.to_dict("records")


# 對帳 頁籤: 選擇日期範圍 => 顯示實現損益圖
@app.callback(
    Output("graph-pnl", "figure"),
    [Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('main-tabs', 'value')]
)
def update_pnl_chart(start_date, end_date, active_tab):
    if active_tab == 'tab-reconcile':
        return rpl.plot(start_date, end_date)
    return {}

# 在使用者切換到 'tab-finlab' 時, 重新掃描報表資料夾, 更新 dropdown
@app.callback(
    Output("finlab-date-dropdown", "options"),
    Output("finlab-date-dropdown", "value"),
    [Input("main-tabs", "value")]
)
def refresh_report_list(active_tab):
    if active_tab != 'tab-finlab':
        # 不在 FinLab 分頁 => 直接回傳空清單
        return [], None

    # 掃描資料夾
    file_names = os.listdir(report_dir)
    date_list = []
    for fname in file_names:
        match = re.match(report_pattern, fname)
        if match:
            date_list.append(match.group(1))  # e.g. "2024-08-18"
    date_list.sort()

    # 建立 dropdown options
    opts = [{"label": d, "value": d} for d in date_list]

    # 預設選擇最後一個 (或你想要的邏輯)
    default_val = date_list[-1] if date_list else None

    return opts, default_val

# 選取 dropdown => 設定 iframe.src
@app.callback(
    Output("finlab-iframe", "src"),
    [Input("finlab-date-dropdown", "value"),
     Input("main-tabs", "value")]
)
def update_finlab_iframe(value, active_tab):
    if active_tab != 'tab-finlab':
        return ""
    if not value:
        return ""

    # 產生對應的 URL 路徑, Dash 會去 /assets/report_finlab/<value>.html 取檔案
    return f"/assets/report_finlab/{value}.html"

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
