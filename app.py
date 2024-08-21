from flask import Flask
from flask_autoindex import AutoIndex

app = Flask(__name__)

# 將目錄公開
AutoIndex(app, browse_root='output')

if __name__ == "__main__":
    app.run(debug=True)