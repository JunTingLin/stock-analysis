import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from service.account_service import AccountService
from service.inventory_service import InventoryService
from service.order_service import OrderService
from service.report_service import ReportService
from service.balance_service import BalanceService
from tabs.order_history import OrderHistoryTab
from tabs.finlab_report import FinlabReportTab
from tabs.inventory_history import InventoryHistoryTab
from tabs.balance_history import BalanceHistoryTab

def create_app():
    # 初始化服務
    account_service = AccountService()
    order_service = OrderService()
    report_service = ReportService()
    inventory_service = InventoryService()
    balance_service = BalanceService()
    
    # 獲取帳戶信息
    accounts = account_service.get_all_accounts()
    account_options = [{'label': acc['account_name'], 'value': acc['account_id']} for acc in accounts]
    
    # 初始化標籤
    order_history_tab = OrderHistoryTab(order_service)
    finlab_report_tab = FinlabReportTab(report_service, accounts)
    inventory_history_tab = InventoryHistoryTab(inventory_service)
    balance_history_tab = BalanceHistoryTab(balance_service)
    
    # 創建 Dash 應用
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # 定義應用布局
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
                order_history_tab.get_layout()
            ]),
            dcc.Tab(label='庫存', value='tab-inventory', children=[
                inventory_history_tab.get_layout()
            ]),
            dcc.Tab(label='帳戶資金', value='tab-balance-history', children=[
                balance_history_tab.get_layout()
            ]),
            dcc.Tab(label='finlab報表', value='tab-finlab-report', children=[
                finlab_report_tab.get_layout()
            ])
        ])
    ])
    
    # 註冊所有標籤的回調函數
    order_history_tab.register_callbacks(app)
    finlab_report_tab.register_callbacks(app)
    inventory_history_tab.register_callbacks(app)
    balance_history_tab.register_callbacks(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)