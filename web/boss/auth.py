import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from boss.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


#Blueprint 是一种组织一组相关视图及其他代码的方式。与把视图及其他 代码直接注册到应用的方式不同，蓝图方式是把它们注册到蓝图，然后在工厂函数中 把蓝图注册到应用。
#Flaskr 有两个蓝图，一个用于认证功能，另一个用于博客帖子管理。每个蓝图的代码 都在一个单独的模块中。使用博客首先需要认证，因此我们先写认证蓝图。

@bp.route('/register', methods=('GET', 'POST'))# @bp 说明是bp蓝图，bp蓝图会在URL前自动加url_prefix
def register():# 注册视图
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            current_app.logger.info(('%s regist in successfully', username))
            return redirect(url_for('auth.login'))#url_for('auth.login'):视图login的url,

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            current_app.logger.info('%s logged in successfully', user['username'])
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

#bp.before_app_request() 注册一个 在视图函数之前运行的函数，不论其 URL 是什么。 load_logged_in_user 检查用户 id 是否已经储存在 session 中，
#并从数据库中获取用户数据，然后储存在 g.user 中。 g.user 的持续时间比请求要长。 如果没有用户 id ，或者 id 不存在，那么 g.user 将会是 None 。
#
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:#没有登陆
        g.user = None
    else:# 已登录
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view