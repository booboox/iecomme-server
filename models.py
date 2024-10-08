# models.py
from flask_login import UserMixin
from database import db
import json
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(51), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    image_paths = db.Column(db.Text, nullable=True)  # 存储 JSON 格式的图片路径

    def get_image_paths(self):
        return json.loads(self.image_paths) if self.image_paths else []

    def set_image_paths(self, paths):
        self.image_paths = json.dumps(paths)

    def __repr__(self):
        return f'<Product {self.name}>'
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 外键，关联 User 表
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # 外键，关联 Product 表
    quantity = db.Column(db.Integer, nullable=False)  # 购买数量
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间

    user = db.relationship('User', backref='orders')  # 反向关系，获取用户的订单
    product = db.relationship('Product', backref='orders')  # 反向关系，获取产品的订单

    def __repr__(self):
        return f'<Order {self.id} - User {self.user_id} - Product {self.product_id}>'
