# __init__.py
import os
from os.path import join, dirname

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


from life.utils.template_filters import replace_newline

login_manager = LoginManager()
login_manager.login_view = 'app.view'
login_manager.login_message = 'ログインしてください'

basedir = os.path.abspath(os.path.dirname(__name__))
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = \
        b'\xd0\xdecCed\xa4BiX\xc7%\x1e8\xech\x15\x9d\xf2~P\x1d\x82\xcf\xfc\xc7q;\x0b\xfd\x1dp'
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ITEMS_PER_PAGE'] = 10
    from life.views import bp
    from life.users.views import users
    from life.english.views import english
    from life.recipe.views import recipes
    app.register_blueprint(bp)
    app.register_blueprint(users)
    app.register_blueprint(english)
    app.register_blueprint(recipes)
    db.init_app(app)
    app.add_template_filter(replace_newline)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    return app