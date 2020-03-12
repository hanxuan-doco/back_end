import uuid
from functools import wraps

from flask import Flask, render_template, flash, redirect, url_for, request, abort, session, g
from flask_sqlalchemy import SQLAlchemy

import constants
from forms import ProductEditForm, LoginForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root: @127.0.0.1:3306/flask_mall'
app.config['SECRET_KEY'] = 'abcdsacb12312'
db = SQLAlchemy(app)


class User(db.Model):
    """ 用户模型 """
    __tablename__ = 'accounts_user'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    username = db.Column(db.String(64), nullable=False)
    nickname = db.Column(db.String(64))
    password = db.Column(db.String(256), nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    is_super = db.Column(db.Boolean, default=False)


class Tag(db.Model):
    """ 商品标签 """
    __tablename__ = 'product_tag'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    # UID
    uid = db.Column(db.String(256), nullable=False, default=uuid.uuid4, unique=True)
    # 标签名称
    name = db.Column(db.String(128), nullable=False)
    # 标签编码
    code = db.Column(db.String(32))
    # 标签的描述
    desc = db.Column(db.String(256))
    # 逻辑删除
    is_valid = db.Column(db.Boolean, default=True)
    # 排序
    reorder = db.Column(db.Integer, default=0)
    # 创建时间
    created_at = db.Column(db.DateTime)
    # 最后修改的时间
    updated_at = db.Column(db.DateTime)


class Classify(db.Model):
    """ 商品分类 """
    __tablename__ = 'product_classify'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    # UID
    uid = db.Column(db.String(256), nullable=False, default=uuid.uuid4, unique=True)
    # 关联父级的ID
    parent_id = db.Column(db.Integer, db.ForeignKey('product_classify.id'))
    img = db.Column(db.String(256))
    # 分类名称
    name = db.Column(db.String(128), nullable=False)
    # 分类编码
    code = db.Column(db.String(32))
    # 分类的描述
    desc = db.Column(db.String(256))
    # 逻辑删除
    is_valid = db.Column(db.Boolean, default=True)
    # 排序
    reorder = db.Column(db.Integer, default=0)
    # 创建时间
    created_at = db.Column(db.DateTime)
    # 最后修改的时间
    updated_at = db.Column(db.DateTime)


class Product(db.Model):
    """ 商品类 """
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    # UID
    uid = db.Column(db.String(256), nullable=False, default=uuid.uuid4, unique=True)
    # 商品标题
    name = db.Column(db.String(128), nullable=False)
    # 商品描述（富文本）
    content = db.Column(db.Text, nullable=False)
    # 商品推荐语
    desc = db.Column(db.String(256))
    # 类型
    types = db.Column(db.String(10), nullable=False)
    # 价格
    price = db.Column(db.Integer, nullable=False)
    # 原价￥
    origin_price = db.Column(db.Float)
    # 主图
    img = db.Column(db.String(256), nullable=False)
    # 渠道
    channel = db.Column(db.String(32))
    # 链接
    buy_link = db.Column(db.String(256))
    # 商品状态
    status = db.Column(db.String(10), nullable=False)
    # 库存
    sku_count = db.Column(db.Integer, default=0)
    # 剩余库存
    remain_count = db.Column(db.Integer, default=0)
    # 浏览次数
    view_count = db.Column(db.Integer, default=0)
    # 评分
    score = db.Column(db.Float, default=10)

    # 逻辑删除
    is_valid = db.Column(db.Boolean, default=True)
    # 排序
    reorder = db.Column(db.Integer, default=0)
    # 创建时间
    created_at = db.Column(db.DateTime)
    # 最后修改的时间
    updated_at = db.Column(db.DateTime)


class ProductClasses(db.Model):
    """ 商品与分类的关系 """
    __tablename__ = 'product_classify_rel'

    id = db.Column(db.Integer, primary_key=True)  # 主键
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    cls_id = db.Column(db.Integer, db.ForeignKey('product_classify.id'))


class ProductTags(db.Model):
    """ 商品与标签的关系 """
    __tablename__ = 'product_tag_rel'

    id = db.Column(db.Integer, primary_key=True)  # 主键
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('product_tag.id'))

db.create_all()

def login_required(view_func):
    """ 登录验证 """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id', None)
        if not user_id:
            flash('请登录', 'danger')
            return redirect(url_for('login'))
        return view_func(*args, *kwargs)
    return wrapper


@app.route('/')
def index():
    """ 首页 """
    return render_template('index.html')


@app.route('/product/list/<int:page>')
@login_required
def product_list(page):
    """ 商品列表 """
    page_size = 2  # 每页多少条
    # 查询搜索条件的查询
    name = request.args.get('name', '')
    print('name---', name)
    if name:
        page_data = Product.query.filter(Product.name.contains(name))\
            .paginate(page=page, per_page=page_size)
    else:
        page_data = Product.query.paginate(page=page, per_page=page_size)
    return render_template('mall/product_list.html', page_data=page_data)


@app.route('/product/detail/<uid>')
def product_detail(uid):
    """ 商品详情 """
    # todo 如果触发了404,404的页面需要定制
    prod_obj = Product.query.filter_by(uid=uid).first_or_404()
    print(prod_obj)
    return render_template('mall/product_detail.html', prod_obj=prod_obj)


@app.route('/product/add', methods=['GET', 'POST'])
def product_add():
    """ 商品添加 """
    form = ProductEditForm()
    if form.validate_on_submit():
        # 保存到数据库
        print(form.data)
        prod_obj = Product(
            name=form.data['name'],
            content =form.data['content'],
            desc =form.data['desc'],
            types =form.data['types'],
            price =form.data['price'],
            origin_price =form.data['origin_price'],
            img = '/xxx.jpg',
            channel = form.data['channel'],
            buy_link = form.data['buy_link'],
            status = form.data['status'],
            sku_count = form.data['sku_count'],
            remain_count = form.data['remain_count'],
            view_count = form.data['view_count'],
            score = form.data['score'],
            is_valid =form.data['is_valid'],
            reorder = form.data['reorder'],
        )
        db.session.add(prod_obj)
        db.session.commit()
        # 消息提示
        flash('新增商品成功', 'success')
        # 跳转到商品列表中去
        return redirect(url_for('product_list', page=1))
    else:
        # 消息提示
        flash('请修改页面中的页面错误，然后提交', 'warning')
        print(form.errors)
    return render_template('mall/product_add.html', form=form)


@app.route('/product/edit/<uid>', methods=['GET', 'POST'])
def product_edit(uid):
    """ 商品编辑 """
    # 查询商品信息
    prod_obj = Product.query.filter_by(uid=uid, is_valid=True).first()
    if prod_obj is None:
        abort(404)
    form = ProductEditForm(obj=prod_obj)
    if form.validate_on_submit():
        prod_obj.name = form.name.data
        prod_obj.content = form.data['content']
        db.session.add(prod_obj)
        db.session.commit()
        flash('修改成功', 'success')
        return redirect(url_for('product_list', page=1))
    else:
        print(form.errors)

    return render_template('mall/product_edit.html', form=form, prod_obj=prod_obj)


@app.route('/product/delete/<uid>', methods=['GET', 'POST'])
def product_delete(uid):
    """ 商品的删除 """
    prod_obj = Product.query.filter_by(uid=uid, is_valid=True).first()
    if prod_obj is None:
        return 'no'
    prod_obj.is_valid = False
    db.session.add(prod_obj)
    db.session.commit()
    return 'ok'


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ 用户登录 """
    form = LoginForm()
    if form.validate_on_submit():
        # 用户名，密码
        username = form.username.data
        password = form.password.data
        # 查找用户
        user = User.query.filter_by(username=username, password=password).first()
        if user is None:
            flash('用户名或者是密码错误', 'danger')
        else:
            session['user_id'] = user.id
            flash('欢迎回来', 'success')
            return redirect(url_for('index'))
    return render_template('accounts/login.html', form=form)


@app.route('/logout')
def logout():
    """ 退出登录 """
    session['user_id'] = None
    g.user = None

    flash('欢迎下次再来', 'success')
    return redirect(url_for('login'))


@app.before_request
def before_request():
    """ 如果有用户的话，设置到全局对象g """
    user_id = session.get('user_id', None)
    if user_id:
        user = User.query.get(user_id)
        print(user)
        g.user = user

