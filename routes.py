# routes.py
from database import db
from config import Config
from flask import request, g, jsonify, Blueprint, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Product, Order
import jwt
import datetime
import json
import os
# 创建一个蓝图，这样可以将相关的路由分组
api = Blueprint('api', __name__)


@api.route('/hello', methods=['GET'])
def zyb_tracker_statistics_action():
    return jsonify({"status": "success", "message": "hello world!"})


user = Blueprint('user', __name__)

@user.route('', methods=['GET'])
def get_user_info():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"status": "error", "message": "Token is missing."}), 400
    try:
        token = token.split(" ")[1]
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = User.query.get(user_id)
        if user:
            return jsonify({"status": "success", "user": {"id": user.id, "username": user.username}}), 200
        else:
            return jsonify({"status": "error", "message": "User not found."}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({"status": "error", "message": "Token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"status": "error", "message": "Invalid token."}), 401

@user.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "User already exists."}), 400

    new_user = User(username=username, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"status": "success", "message": "User registered successfully."}), 200


@user.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        # 生成 token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 设置过期时间
        }, Config.SECRET_KEY, algorithm='HS256')

        return jsonify({"status": "success", "message": "Login successful.", "token": token}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid username or password."}), 401

shop = Blueprint('shop', __name__)
# 添加产品

# 假设这个是你的图片存储基目录
IMAGE_UPLOAD_DIRECTORY = r"C:\Users\LENOVO\Desktop\iEComme\flask\static\images"  # 更新为你的服务器路径

@shop.route('/products', methods=['POST'])
def add_product():
    # 从 form-data 获取字段
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    stock = request.form.get('stock')

    # 获取所有上传的图片文件
    image_files = request.files.getlist('images')  # 使用 getlist 获取多个文件

    if not image_files:
        return jsonify({"message": "No images provided"}), 400

    # 创建新的产品对象
    new_product = Product(
        name=name,
        description=description,
        price=float(price),
        stock=int(stock)
    )

    db.session.add(new_product)
    db.session.commit()  # 先提交以获取新产品的 ID

    # 创建对应 ID 的目录
    product_dir = os.path.join(IMAGE_UPLOAD_DIRECTORY, str(new_product.id))
    os.makedirs(product_dir, exist_ok=True)  # 创建文件夹，如果已存在则忽略

    # 保存每张图片，并记录文件名
    image_filenames = []  # 用于存储文件名
    for image_file in image_files:
        # 确保文件名唯一，避免覆盖
        filename = f"{new_product.id}_{image_file.filename}"
        image_path = os.path.join(product_dir, filename)
        image_file.save(image_path)  # 保存图片到目录
        image_filenames.append(filename)  # 存储每张图片的文件名

    # 将图片文件名保存到数据库的 image_paths 列中
    new_product.set_image_paths(image_filenames)  # 调用 set_image_paths 方法
    db.session.commit()  # 提交更改

    return jsonify({"message": "Product added", "id": new_product.id, "images": image_filenames}), 201


@shop.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()  # 获取所有产品
    product_data = [{
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "images": product.get_image_paths()  # 假设这个方法返回图片路径
    } for product in products]

    return jsonify({"products": product_data}), 200


@shop.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)  # 根据产品 ID 查询产品
    if product is None:
        return jsonify({"error": "Product not found"}), 404  # 如果未找到，返回404错误

    product_data = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": str(product.price),  # 转换为字符串以确保 JSON 序列化
        "stock": product.stock,
        "images": product.get_image_paths()  # 假设这个方法返回图片路径
    }

    return jsonify(product_data), 200  # 返回产品信息



# 删除产品
@shop.route('/products/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 204


# 更新产品
@shop.route('/products/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    # 从 form-data 获取字段
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    stock = request.form.get('stock')

    # 获取所有上传的图片文件
    image_files = request.files.getlist('images')  # 使用 getlist 获取多个文件
    images_to_delete = request.form.getlist('delete_images')  # 获取需要删除的图片文件名

    # 查找要更新的产品
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    # 更新产品信息
    if name:
        product.name = name
    if description:
        product.description = description
    if price is not None:
        try:
            product.price = float(price)
        except ValueError:
            return jsonify({"message": "Invalid price"}), 400
    if stock is not None:
        try:
            product.stock = int(stock)
        except ValueError:
            return jsonify({"message": "Invalid stock"}), 400

    # 创建对应 ID 的目录
    product_dir = os.path.join(r"D:\BBX\image", str(product.id))
    os.makedirs(product_dir, exist_ok=True)  # 创建文件夹，如果已存在则忽略

    # 存储所有新上传的图片路径
    image_paths = []

    # 保存新上传的每张图片
    for image_file in image_files:
        if image_file:
            image_path = os.path.join(product_dir, image_file.filename)
            image_file.save(image_path)
            image_paths.append(image_file.filename)  # 存储文件名而不是完整路径

    # 确保 product.image_paths 是列表，如果不是，则初始化为空列表
    existing_images = json.loads(product.image_paths) if product.image_paths else []

    # 删除指定的旧图片
    for image_name in images_to_delete:
        old_image_path = os.path.join(product_dir, image_name)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)  # 删除本地文件
            # 从 existing_images 中移除对应的图片路径
            if image_name in existing_images:
                existing_images.remove(image_name)

    # 更新数据库中的图片路径
    existing_images.extend(image_paths)  # 添加新上传的图片文件名
    # 确保产品的 image_paths 字段存储的是唯一的文件名
    product.image_paths = json.dumps(list(set(existing_images)))  # 转换为 JSON 格式

    db.session.commit()  # 提交更改

    return jsonify({"message": "Product updated", "id": product.id, "images": json.loads(product.image_paths)}), 200

# 购买产品
@shop.route('/products/<int:product_id>/purchase', methods=['POST'])
def purchase_product(product_id):
    data = request.json
    quantity = data.get('quantity', 1)

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    if product.stock < quantity:
        return jsonify({"message": "Not enough stock available"}), 400

    # 创建订单记录
    user_id = data.get('user_id')  # 假设用户 ID 从请求中获取
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    new_order = Order(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(new_order)

    # 更新产品库存
    product.stock -= quantity
    db.session.commit()
    return jsonify({"message": "Purchase successful", "remaining_stock": product.stock}), 200


# 获取用户的订单
@user.route('/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    return jsonify(
        [{"id": order.id, "product_id": order.product_id, "quantity": order.quantity, "created_at": order.created_at}
         for order in orders]), 200


# 获取特定订单详情
@user.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    return jsonify({
        "id": order.id,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "created_at": order.created_at
    }), 200


# 删除特定订单
@user.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted"}), 204
