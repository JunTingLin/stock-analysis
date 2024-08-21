import os
import logging
from jinja2 import Environment, FileSystemLoader
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

        # 提取當天的 financial_summary_all 數據
        summary_today = self.data_dict['financial_summary_all'].loc[self.data_dict['financial_summary_all']['日期時間'] == self.datetime]
        summary_today_html = summary_today.to_html(classes='table table-striped', index=False)

        # 使用 Plotly 生成趨勢圖表
        fig = px.line(
            self.data_dict['financial_summary_all'], 
            x='日期時間', 
            y=['銀行餘額(計入交割款)', '現股總市值', '資產總值'],
            labels={"value": "金額", "variable": "指標"},
            title="Financial Summary Over Time"
        )
        plot_html = pio.to_html(fig, full_html=False)

        return df1_html, df2_html, summary_today_html, plot_html

    def integrate_finlab_report(self, df1_html, df2_html, summary_today_html, plot_html):
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
            summary_today_html=summary_today_html,
            plot_html=plot_html,
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
        df1_html, df2_html, summary_today_html, plot_html = self.render_data_dict()
        final_report_path = self.integrate_finlab_report(df1_html, df2_html, summary_today_html, plot_html)
        return final_report_path