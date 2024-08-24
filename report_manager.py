import os
import logging
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import plotly.express as px
import plotly.io as pio

class ReportManager:
    def __init__(self, data_dict, report_finlab_directory, report_final_directory, datetime, template_path):
        self.data_dict = data_dict
        self.report_finlab_directory = report_finlab_directory
        self.report_final_directory = report_final_directory
        self.datetime = datetime
        self.template_path = template_path

        self.report_finlab_path = os.path.join(report_finlab_directory, f'{self.datetime.strftime("%Y-%m-%d_%H-%M-%S")}.html')
        self.final_report_path = os.path.join(report_final_directory, f'{self.datetime.strftime("%Y-%m-%d_%H-%M-%S")}.html')

        # 初始化 Jinja2 模板環境
        self.env = Environment(loader=FileSystemLoader(os.path.dirname(self.template_path)))

    def render_data_dict(self):
        df1_html = self.data_dict['current_portfolio_today'].to_html(classes='table table-striped', index=False, table_id="df1_table")
        df2_html = self.data_dict['next_portfolio_today'].to_html(classes='table table-striped', index=False, table_id="df2_table")
        df3_html = self.data_dict['order_status'].to_html(classes='table table-striped', index=False, table_id="df3_table")
        df4_html = self.data_dict['financial_summary_today'].to_html(classes='table table-striped', index=False, table_id="df4_table")

        plot1_html = self.generate_financial_summary_plot()
        plot2_html = self.generate_monthly_return_plot()

        return df1_html, df2_html, df3_html, df4_html, plot1_html, plot2_html
    
    def generate_financial_summary_plot(self):
        fig = px.line(
            self.data_dict['financial_summary_all'], 
            x='datetime', 
            y=['adjusted_bank_balance', 'market_value', 'total_assets'],
            labels={"value": "Amount NT$", "variable": "funding level"},
            title="Financial Summary Over Time"
        )
        return pio.to_html(fig, full_html=False)

    def generate_monthly_return_plot(self):
        financial_summary_all = self.data_dict['financial_summary_all'].copy()
        financial_summary_all['datetime'] = pd.to_datetime(financial_summary_all['datetime'])

        monthly_returns = financial_summary_all.groupby(financial_summary_all['datetime'].dt.to_period('M')).apply(
            lambda x: (x.iloc[-1]['total_assets'] / x.iloc[0]['total_assets'] - 1) * 100 if len(x) > 1 else None
        ).dropna().reset_index(name='monthly_return')

        # 將 Period 轉換為字符串格式
        monthly_returns['datetime'] = monthly_returns['datetime'].astype(str)

        fig = px.line(
            monthly_returns, 
            x='datetime', 
            y='monthly_return',
            labels={"monthly_return": "Monthly Return (%)", "datetime": "Month"},
            title="Monthly Return Over Time"
        )
        return pio.to_html(fig, full_html=False)

    def integrate_finlab_report(self, df1_html, df2_html, df3_html, df4_html, plot1_html, plot2_html):
        # 加載模板
        template = self.env.get_template(os.path.basename(self.template_path))

        # 檢查 report_finlab_path 是否存在
        if not os.path.exists(self.report_finlab_path):
            logging.warning(f"Finlab report not found at {self.report_finlab_path}. Skipping iframe embedding.")
            self.report_finlab_path = None
        else:
            relative_finlab_path  = f'/report_finlab/{os.path.basename(self.report_finlab_path)}'
            logging.info(f"Finlab report found at {self.report_finlab_path}")


        # 渲染模板
        rendered_html = template.render(
            df1_html=df1_html,
            df2_html=df2_html,
            df3_html=df3_html,
            df4_html=df4_html,
            plot1_html=plot1_html,
            plot2_html=plot2_html,
            finlab_report_url=relative_finlab_path,
            formatted_datetime=self.datetime.strftime("%Y-%m-%d %H:%M:%S")
        )

        # 嘗試創建目標目錄
        os.makedirs(os.path.dirname(self.final_report_path), exist_ok=True)

        # 保存最終報表
        try:
            with open(self.final_report_path, 'w', encoding='utf-8') as file:
                file.write(rendered_html)
            logging.info(f"Final report saved at {self.final_report_path}")
        except FileNotFoundError as e:
            logging.error(f"Failed to save final report: {e}")
            return None

        return self.final_report_path

    def save_final_report(self):
        df1_html, df2_html, df3_html, df4_html, plot1_html, plot2_html = self.render_data_dict()
        final_report_path = self.integrate_finlab_report(df1_html, df2_html, df3_html, df4_html, plot1_html, plot2_html)
        return final_report_path