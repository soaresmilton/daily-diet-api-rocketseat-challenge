from flask import Flask, jsonify, request
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models.user import User
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@127.0.0.1:3306/flask-crud'

login_manager = LoginManager()

db.init_app(app)


login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
  data = request.get_json()
  username = data.get('username')
  password = data.get('password')
  if username and password: 
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

    if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
      login_user(user)
      return jsonify({"message": "Autenticação realizada com sucesos."})

  return jsonify({"message": "Credenciais inválidas."}), 400


@app.route('/user', methods=['POST'])
def create_user():
  data = request.get_json()
  username = data.get('username')
  password = data.get('password')

  if username and password:
    hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
    user = User(username=username, password=hashed_password, role='user')

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Usuário criado com sucesso."})
  



if __name__ == '__main__':
  app.run(debug=True)