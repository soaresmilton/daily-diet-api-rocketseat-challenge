from flask import jsonify, request, Blueprint
from app.database import db
from flask_login import login_user, current_user, logout_user, login_required
from ..models.user import User
import bcrypt

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['POST'])
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

@user_bp.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user()
  return jsonify({"message": "Usuário deslogado com sucesso"})

@user_bp.route('/user', methods=['POST'])
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

  return jsonify({"message": "Credenciais inválidas"}), 400
  
@user_bp.route('/user/<int:id_user>', methods=['GET'])
@login_required
def read_user(id_user):
  user = User.query.get(id_user)
  if user:
    return {"username": user.username, "role": user.role}

  return jsonify({"message": "Usuário não encontrado."}), 404

@user_bp.route('/user/<int:id_user>', methods=['PUT'])
@login_required
def update_user(id_user):
  user = User.query.get(id_user)
  data = request.get_json()
  if id_user != current_user.id and current_user.role == 'user':
    return jsonify({"message": "Operação não permitida"}), 403
  
  if user and data.get("password"):
    hashed_password = bcrypt.hashpw(str.encode(data.get("password")), bcrypt.gensalt())
    user.password = hashed_password
    db.session.commit()

    return jsonify({"message": "Senha alterada com sucesso."})

  return jsonify({"message": "Usuário não encontrado"}), 404    

@user_bp.route('/user/<int:id_user>', methods=['DELETE'])
@login_required
def delete_user(id_user):
  user = User.query.get(id_user)

  if current_user.role != 'admin':
    return jsonify({"message": "Operação não permitida"}), 403
  
  if id_user == current_user.id:
    return jsonify({"message": "Deleção não permitida"}), 403
  
  if user:
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Usuário deletado com sucesso."})
  
  return jsonify({"message": "Usuário não encontrado"}), 404
