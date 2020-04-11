import os

from flask import Flask


def create_app(test_config=None):# 创建一个flask实例
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',#是被 Flask 和扩展用于保证数据安全的。在开发过程中， 为了方便可以设置为 'dev' ，但是在发布的时候应当使用一个随机值来 重载它。
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    

    from . import db 
    db.init_app(app) #在应用中注册 数据库相关函数

    from . import auth
    app.register_blueprint(auth.bp) #在应用中注册auth.bp蓝图

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')#app.add_url_rule() 关联端点名称 'index' 和 / URL  这样 url_for('index') 或 url_for('blog.index') 都会有效，会生成同样的 / URL 。

    from . import movie
    app.register_blueprint(movie.bp)

    return app