from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()  # We will initialize it with the directory parameter below.
login = LoginManager()
login.login_view = 'main.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    # Specify the migrations directory explicitly:
    migrate.init_app(app, db, directory='migrations')
    login.init_app(app)

    # Register blueprint
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
