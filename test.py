import pandas as pd
import plotly.express as px
import plotly.io as pio

# 創建三個 DataFrame
df1 = pd.DataFrame({
    "Column A": [1, 2, 3],
    "Column B": [4, 5, 6]
})

df2 = pd.DataFrame({
    "Column C": [7, 8, 9],
    "Column D": [10, 11, 12]
})

df3 = pd.DataFrame({
    "Date": pd.date_range(start='1/1/2020', periods=10),
    "Value": [3, 5, 7, 9, 11, 13, 15, 17, 19, 21]
})

# 將 DataFrame 轉換為 HTML 表格
df1_html = df1.to_html(classes='table table-striped', index=False)
df2_html = df2.to_html(classes='table table-striped', index=False)

# 使用 Plotly 繪製互動趨勢圖
fig = px.line(df3, x='Date', y='Value', title='Trend over Time')
plot_html = pio.to_html(fig, full_html=False)

# 組合 HTML 內容
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container">
        <h1 class="my-4">Data Dashboard</h1>

        <div class="row">
            <div class="col-md-6">
                <h3>DataFrame 1</h3>
                {df1_html}
            </div>
            <div class="col-md-6">
                <h3>DataFrame 2</h3>
                {df2_html}
            </div>
        </div>

        <div class="row my-4">
            <div class="col-md-12">
                <h3>Trend over Time</h3>
                {plot_html}
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
"""

# 將 HTML 內容寫入文件
with open("output/dashboard.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML file created successfully.")