from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import datetime
import pandas as pd
import numpy as np

class BalanceHistoryTab:
    def __init__(self, balance_service):
        self.balance_service = balance_service
        
    def get_layout(self):
        """返回帳戶資金標籤的版面配置"""
        # 計算默認日期範圍：過去一年
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=365)
        
        return html.Div([
            # 日期選擇和概要摘要
            html.Div([
                html.Div([
                    html.Label("選擇日期範圍："),
                    dcc.DatePickerRange(
                        id='balance-date-range',
                        start_date=start_date,
                        end_date=end_date,
                        display_format='YYYY-MM-DD'
                    )
                ], style={'width': '50%', 'margin': '10px'}),
                
                html.Div([
                    html.H3("帳戶資金摘要", className='mb-3'),
                    html.Div(id='balance-summary', className='summary-box')
                ], style={'margin': '20px'})
            ], className='row'),
            
            # 資金水位趨勢圖
            html.Div([
                html.H3("資金水位趨勢", className='mb-3'),
                dcc.Graph(id='balance-trend-graph')
            ], style={'margin': '20px'}),
            
            # 月度回報率熱力圖
            html.Div([
                html.H3("月度報酬率熱力圖", className='mb-3'),
                dcc.Graph(id='monthly-return-heatmap')
            ], style={'margin': '20px'})
        ])
        
    def register_callbacks(self, app):
        """註冊該標籤所需的回調函數"""
        
        # 帳戶資金摘要回調
        @app.callback(
            Output('balance-summary', 'children'),
            Input('account-dropdown', 'value')
        )
        def update_balance_summary(selected_account):
            if not selected_account:
                return html.Div("請選擇帳戶", className='text-muted')
                
            # 獲取最新餘額數據
            latest_balance = self.balance_service.get_latest_balance(selected_account)
            
            if not latest_balance:
                return html.Div("無資金數據", className='text-muted')
                
            # 解析日期
            try:
                fetch_date = datetime.datetime.strptime(
                    latest_balance['fetch_timestamp'], 
                    "%Y-%m-%d %H:%M:%S"
                ).strftime("%Y-%m-%d")
            except:
                fetch_date = "未知日期"
                
            # 創建摘要卡片
            summary_cards = dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("銀行餘額", className="card-title"),
                            html.H3(f"${latest_balance['bank_balance']:,.2f}", className="card-text text-primary")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("調整後銀行餘額", className="card-title"),
                            html.H3(f"${latest_balance['adjusted_bank_balance']:,.2f}", className="card-text text-info")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("市值", className="card-title"),
                            html.H3(f"${latest_balance['market_value']:,.2f}", className="card-text text-success")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("總資產", className="card-title"),
                            html.H3(f"${latest_balance['total_assets']:,.2f}", className="card-text text-dark")
                        ])
                    ])
                ], width=3)
            ])
            
            return html.Div([
                html.P(f"最新資料日期：{fetch_date}", className="text-muted mb-3"),
                summary_cards
            ])
            
        # 資金水位趨勢圖回調
        @app.callback(
            Output('balance-trend-graph', 'figure'),
            [Input('account-dropdown', 'value'),
             Input('balance-date-range', 'start_date'),
             Input('balance-date-range', 'end_date')]
        )
        def update_balance_trend(selected_account, start_date, end_date):
            if not selected_account or not start_date or not end_date:
                return go.Figure()
                
            try:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            except:
                # 處理已經是日期格式的情況
                if isinstance(start_date, str) and isinstance(end_date, str):
                    try:
                        start_date = datetime.datetime.fromisoformat(start_date).date()
                        end_date = datetime.datetime.fromisoformat(end_date).date()
                    except:
                        return go.Figure()
                else:
                    return go.Figure()
            
            # 獲取趨勢數據
            trend_data = self.balance_service.get_balance_trend_data(
                selected_account, 
                start_date,
                end_date
            )
            
            if not trend_data:
                fig = go.Figure()
                fig.update_layout(
                    title="無資金水位數據",
                    xaxis_title="日期",
                    yaxis_title="金額"
                )
                return fig
                
            # 轉換為DataFrame便於處理
            df = pd.DataFrame(trend_data)
            
            # 創建趨勢圖
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['date'], 
                y=df['adjusted_bank_balance'],
                mode='lines+markers',
                name='調整後銀行餘額',
                line=dict(color='#36a2eb', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['date'], 
                y=df['market_value'],
                mode='lines+markers',
                name='市值',
                line=dict(color='#4bc0c0', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['date'], 
                y=df['total_assets'],
                mode='lines+markers',
                name='總資產',
                line=dict(color='#ff6384', width=2)
            ))
            
            # 更新佈局
            fig.update_layout(
                title="資金水位趨勢",
                xaxis_title="日期",
                yaxis_title="金額",
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                template="plotly_white"
            )
            
            return fig
            
        # 月度回報率熱力圖回調
        @app.callback(
            Output('monthly-return-heatmap', 'figure'),
            [Input('account-dropdown', 'value')]
        )
        def update_monthly_return_heatmap(selected_account):
            if not selected_account:
                return go.Figure()
                
            # 獲取熱力圖數據
            heatmap_data, years, max_return, min_return = self.balance_service.get_monthly_return_data(
                selected_account
            )
            print(heatmap_data)

            if not heatmap_data:
                fig = go.Figure()
                fig.update_layout(
                    title="無足夠數據計算月度報酬率",
                    xaxis_title="月份",
                    yaxis_title="年份"
                )
                return fig
                
            # 轉換為DataFrame
            df = pd.DataFrame(heatmap_data)
            
            # 月份名稱映射
            month_names = {
                '01': '一月', '02': '二月', '03': '三月', '04': '四月',
                '05': '五月', '06': '六月', '07': '七月', '08': '八月',
                '09': '九月', '10': '十月', '11': '十一月', '12': '十二月'
            }
            
            # 添加月份名稱列
            df['month_name'] = df['month'].map(month_names)
            
            # 創建熱力圖
            fig = px.imshow(
                pd.pivot_table(
                    df, 
                    values='return', 
                    index='year', 
                    columns='month_name',
                    aggfunc='first'
                ),
                labels=dict(x="月份", y="年份", color="月報酬率 (%)"),
                x=[month_names[m] for m in sorted(df['month'].unique())],
                y=sorted(df['year'].unique()),
                color_continuous_scale='RdBu_r',  # 紅藍色比例(負值為紅，正值為藍)
                zmin=min_return,  # 最小值
                zmax=max_return,  # 最大值
            )
            
            # 添加數值標籤
            for year in df['year'].unique():
                for month, month_name in month_names.items():
                    if month in df[df['year'] == year]['month'].values:
                        value = df[(df['year'] == year) & (df['month'] == month)]['return'].values[0]
                        fig.add_annotation(
                            x=month_name,
                            y=year,
                            text=f"{value:.2f}%",
                            showarrow=False,
                            font=dict(
                                color="black" if abs(value) < (max_return - min_return) / 2 else "white",
                                size=10
                            )
                        )
            
            # 更新佈局
            fig.update_layout(
                title="月度報酬率熱力圖",
                xaxis_title="月份",
                yaxis_title="年份",
                coloraxis_colorbar=dict(
                    title="報酬率 (%)"
                ),
                template="plotly_white"
            )
            
            return fig