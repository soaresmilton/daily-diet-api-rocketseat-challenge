from flask import Flask, jsonify, request
from flask_login import LoginManager
from .database import db
from .models.user import User
from .routes.user_routes import user_bp
from .routes.meal_routes import meal_bp

login_manager = LoginManager()

def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = "your_secret_key"
  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@127.0.0.1:3306/flask-crud'


  db.init_app(app)

  login_manager.init_app(app)
  login_manager.login_view = 'login'

  # API DE USUÁRIOS E AUTENTICAÇÃO
  @login_manager.user_loader
  def load_user(user_id):
    return User.query.get(user_id)
  
  app.register_blueprint(user_bp)
  app.register_blueprint(meal_bp)


  return app