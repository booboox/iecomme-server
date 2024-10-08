from flask import Flask
from config import Config
from database import db
from routes import api, user, shop
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from models import User

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# 初始化数据库
db.init_app(app)

# 初始化 Flask-Migrate
migrate = Migrate(app, db)

# 初始化 LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# 用户加载器
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 注册蓝图
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(shop, url_prefix='/shop')

@app.route('/')
def home():
    return "Welcome to the Flask application!"

if __name__ == '__main__':
    app.run(debug=True)
