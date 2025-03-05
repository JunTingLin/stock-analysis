from dash import dcc, html, Input, Output, callback

class FinlabReportTab:
    def __init__(self, report_service, accounts):
        self.report_service = report_service
        self.accounts = accounts

    def get_layout(self):
        """返回 finlab 報表標籤的版面配置"""
        return html.Div([
            html.Div([
                html.Div([
                    html.Label("年："),
                    dcc.Dropdown(
                        id='report-year-dropdown',
                        options=[],
                        value=None
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'margin-right': '10px'}),
                html.Div([
                    html.Label("月："),
                    dcc.Dropdown(
                        id='report-month-dropdown',
                        options=[],
                        value=None
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'margin-right': '10px'}),
                html.Div([
                    html.Label("日："),
                    dcc.Dropdown(
                        id='report-day-dropdown',
                        options=[],
                        value=None
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'margin-right': '10px'}),
                html.Div([
                    html.Label("時間："),
                    dcc.Dropdown(
                        id='report-time-dropdown',
                        options=[],
                        value=None
                    )
                ], style={'width': '20%', 'display': 'inline-block'}),
            ], style={'margin': '20px'}),
            html.Div([
                html.Iframe(
                    id='report-iframe',
                    style={'width': '100%', 'height': '800px', 'border': 'none'}
                )
            ], style={'margin': '20px'})
        ])

    def register_callbacks(self, app):
        """註冊該標籤所需的回調函數"""
        
        @app.callback(
            Output('report-year-dropdown', 'options'),
            Output('report-year-dropdown', 'value'),
            Input('account-dropdown', 'value')
        )
        def update_report_years(selected_account):
            if not selected_account:
                return [], None
                
            # 從 account_id 取得 account_name
            account_name = next((acc['account_name'] for acc in self.accounts if acc['account_id'] == selected_account), None)
            if not account_name:
                return [], None
                
            years = self.report_service.get_available_years(account_name)
            default_year = years[0]['value'] if years else None
            return years, default_year

        @app.callback(
            Output('report-month-dropdown', 'options'),
            Output('report-month-dropdown', 'value'),
            Input('account-dropdown', 'value'),
            Input('report-year-dropdown', 'value')
        )
        def update_report_months(selected_account, selected_year):
            if not selected_account or not selected_year:
                return [], None
                
            # 從 account_id 取得 account_name
            account_name = next((acc['account_name'] for acc in self.accounts if acc['account_id'] == selected_account), None)
            if not account_name:
                return [], None
                
            months = self.report_service.get_available_months(account_name, selected_year)
            default_month = months[0]['value'] if months else None
            return months, default_month

        @app.callback(
            Output('report-day-dropdown', 'options'),
            Output('report-day-dropdown', 'value'),
            Input('account-dropdown', 'value'),
            Input('report-year-dropdown', 'value'),
            Input('report-month-dropdown', 'value')
        )
        def update_report_days(selected_account, selected_year, selected_month):
            if not selected_account or not selected_year or not selected_month:
                return [], None
                
            # 從 account_id 取得 account_name
            account_name = next((acc['account_name'] for acc in self.accounts if acc['account_id'] == selected_account), None)
            if not account_name:
                return [], None
                
            days = self.report_service.get_available_days(account_name, selected_year, selected_month)
            default_day = days[0]['value'] if days else None
            return days, default_day

        @app.callback(
            Output('report-time-dropdown', 'options'),
            Output('report-time-dropdown', 'value'),
            Input('account-dropdown', 'value'),
            Input('report-year-dropdown', 'value'),
            Input('report-month-dropdown', 'value'),
            Input('report-day-dropdown', 'value')
        )
        def update_report_times(selected_account, selected_year, selected_month, selected_day):
            if not selected_account or not selected_year or not selected_month or not selected_day:
                return [], None
                
            # 從 account_id 取得 account_name
            account_name = next((acc['account_name'] for acc in self.accounts if acc['account_id'] == selected_account), None)
            if not account_name:
                return [], None
                
            times = self.report_service.get_available_times(account_name, selected_year, selected_month, selected_day)
            default_time = times[0]['value'] if times else None
            return times, default_time

        @app.callback(
            Output('report-iframe', 'src'),
            Input('account-dropdown', 'value'),
            Input('report-year-dropdown', 'value'),
            Input('report-month-dropdown', 'value'),
            Input('report-day-dropdown', 'value'),
            Input('report-time-dropdown', 'value')
        )
        def update_report_iframe(selected_account, selected_year, selected_month, selected_day, selected_time):
            if not selected_account or not selected_year or not selected_month or not selected_day or not selected_time:
                return ""
                
            # 從 account_id 取得 account_name
            account_name = next((acc['account_name'] for acc in self.accounts if acc['account_id'] == selected_account), None)
            if not account_name:
                return ""
                
            report_url = self.report_service.get_report_url(account_name, selected_year, selected_month, selected_day, selected_time)
            return report_url