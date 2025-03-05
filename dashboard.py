import dash
from dash import dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import datetime

from service import OrderService
from service import AccountService

account_service = AccountService()
order_service = OrderService()

accounts = account_service.get_all_accounts()
account_options = [{'label': acc['account_name'], 'value': acc['account_id']} for acc in accounts]

# 下拉選單選年、月、日
current_year = datetime.datetime.now().year
current_month = datetime.datetime.now().month
current_day = datetime.datetime.now().day
year_options = [{'label': str(year), 'value': str(year)} for year in range(2020, current_year+1)]
month_options = [{'label': f"{m:02d}", 'value': f"{m:02d}"} for m in range(1, 13)]
day_options = [{'label': f"{d:02d}", 'value': f"{d:02d}"} for d in range(1, 32)]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("MirLab Dashboard"),
    html.Div([
        html.Label("選擇帳戶："),
        dcc.Dropdown(
            id='account-dropdown',
            options=account_options,
            value=account_options[0]['value'] if account_options else None
        )
    ], style={'width': '30%', 'margin': '10px'}),

    dcc.Tabs(id="tabs", value='tab-order-history', children=[
        dcc.Tab(label='下單歷史', value='tab-order-history', children=[
            html.Div([
                html.Div([
                    html.Label("年："),
                    dcc.Dropdown(
                        id='year-dropdown',
                        options=year_options,
                        value=str(current_year)
                    )
                ], style={'width': '30%', 'display': 'inline-block'}),
                html.Div([
                    html.Label("月："),
                    dcc.Dropdown(
                        id='month-dropdown',
                        options=month_options,
                        value=f"{current_month:02d}"
                    )
                ], style={'width': '30%', 'display': 'inline-block'}),
                html.Div([
                    html.Label("日："),
                    dcc.Dropdown(
                        id='day-dropdown',
                        options=day_options,
                        value=f"{current_day:02d}"
                    )
                ], style={'width': '30%', 'display': 'inline-block'}),
            ], style={'margin': '10px'}),

            html.Div([
                dash_table.DataTable(
                    id='order-history-table',
                    columns=[
                        {'name': 'Order Timestamp', 'id': 'order_timestamp'},
                        {'name': 'Action', 'id': 'action'},
                        {'name': 'Stock ID', 'id': 'stock_id'},
                        {'name': 'Stock Name', 'id': 'stock_name'},
                        {'name': 'Quantity', 'id': 'quantity'},
                        {'name': 'Price', 'id': 'price'},
                        {'name': 'Extra Bid %', 'id': 'extra_bid_pct'},
                        {'name': 'Order Condition', 'id': 'order_condition'},
                    ],
                    data=[],
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                )
            ], style={'margin': '20px'})
        ]),
        dcc.Tab(label='finlab報表', value='tab-finlab-report', children=[
            html.Div("Finlab 報表將在此呈現。")
        ]),
    ])
])

@app.callback(
    Output('order-history-table', 'data'),
    Input('account-dropdown', 'value'),
    Input('year-dropdown', 'value'),
    Input('month-dropdown', 'value'),
    Input('day-dropdown', 'value'),
)
def update_order_history(selected_account, selected_year, selected_month, selected_day):
    if not selected_account:
        return []

    try:
        date_str = f"{selected_year}-{selected_month}-{selected_day}"
        query_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        return []

    orders = order_service.get_order_history(selected_account, query_date)
    return orders

if __name__ == '__main__':
    app.run_server(debug=True)
