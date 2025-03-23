from dash import dcc, html, Input, Output, callback
import datetime

class FinlabReportTab:
    def __init__(self, report_service, accounts):
        self.report_service = report_service
        self.accounts = accounts

    def get_layout(self):
        """返回 finlab 報表標籤的版面配置"""
        return html.Div([
            html.Div([
                html.Div([
                    html.Label("選擇日期："),
                    dcc.DatePickerSingle(
                        id='report-date-picker',
                        min_date_allowed=datetime.date(2020, 1, 1),
                        max_date_allowed=datetime.date.today(),
                        initial_visible_month=datetime.date.today(),
                        date=datetime.date.today(),
                        display_format='YYYY-MM-DD'
                    )
                ], style={'width': '40%', 'display': 'inline-block', 'margin-right': '10px'}),
            ], style={'margin': '20px'}),
            html.Div(id='report-container', children=[
                html.Div("請選擇帳戶和日期以查看報告。", style={'padding': '20px', 'text-align': 'center'})
            ], style={'margin': '20px'})
        ])

    def register_callbacks(self, app):
        """註冊該標籤所需的回調函數"""
        
        @app.callback(
            Output('report-container', 'children'),
            Input('account-dropdown', 'value'),
            Input('report-date-picker', 'date')
        )
        def update_report_display(selected_account, selected_date):
            if not selected_account or not selected_date:
                return html.Div("請選擇帳戶和日期以查看報告。", 
                             style={'padding': '20px', 'text-align': 'center'})
                
            # 從 account_id 取得 account_name
            account_name = next((acc['account_name'] for acc in self.accounts if acc['account_id'] == selected_account), None)
            if not account_name:
                return html.Div("無效的帳戶選擇。", 
                             style={'padding': '20px', 'text-align': 'center'})
            
            # 將字符串日期轉換為日期對象
            if isinstance(selected_date, str):
                selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
            
            # 獲取選定日期的報告URL
            report_url = self.report_service.get_report_url_by_date(account_name, selected_date)
            
            if report_url:
                return html.Iframe(
                    src=report_url,
                    style={'width': '100%', 'height': '800px', 'border': 'none'}
                )
            else:
                return html.Div(f"{selected_date.strftime('%Y-%m-%d')} 沒有可用的報告。", 
                             style={'padding': '20px', 'text-align': 'center'})