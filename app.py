from flask import Flask, jsonify, request
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models.user import User
from models.meal import Meal
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@127.0.0.1:3306/flask-crud'

login_manager = LoginManager()

db.init_app(app)

login_manager.init_app(app)
login_manager.login_view = 'login'

# API DE USUÁRIOS E AUTENTICAÇÃO
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

@app.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user()
  return jsonify({"message": "Usuário deslogado com sucesso"})

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

  return jsonify({"message": "Credenciais inválidas"}), 400
  
@app.route('/user/<int:id_user>', methods=['GET'])
@login_required
def read_user(id_user):
  user = User.query.get(id_user)
  if user:
    return {"username": user.username, "role": user.role}

  return jsonify({"message": "Usuário não encontrado."}), 404

@app.route('/user/<int:id_user>', methods=['PUT'])
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

@app.route('/user/<int:id_user>', methods=['DELETE'])
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

## API DAS REFEIÇÕES - MEAL API
@app.route('/meal', methods=['POST'])
@login_required
def create_meal():
  data = request.get_json()
  name = data.get("name")
  description = data.get("description")
  date = data.get("date")
  is_diet = data.get("is_diet")

  if name and description and date:
    meal = Meal(name=name, description=description, date=date, is_diet=is_diet, id_user=current_user.id)
    db.session.add(meal)
    db.session.commit()
    return jsonify({"message": "Refeição cadastrada com sucesso."})

  return jsonify({"message": "Informações inválidas"}), 400

@app.route('/meal/<id_meal>', methods=['GET'])
@login_required
def read_user_meal(id_meal):
  meal = Meal.query.get(id_meal)

  if meal and meal.id_user == current_user.id:
    return jsonify({"name": meal.name, "description": meal.description, "date": meal.date.isoformat(), "created": meal.created.isoformat(), "is_diet": meal.is_diet})

  return jsonify({"message": "Refeição não encontrada."}), 404

@app.route('/meals', methods=['GET'])
@login_required
def list_all_user_meals():
  meals =  Meal.query.filter(Meal.id_user == current_user.id).all()
  meals_list = [meal.to_dict() for meal in meals]
  if meals:
    return jsonify({"meals": meals_list, "total": len(meals_list)})
  
  return jsonify({"message": "Nenhuma refeição foi encotrada"}), 404

@app.route('/meal/<id_meal>', methods=['PUT'])
@login_required
def update_meal(id_meal):
  meal = Meal.query.get(id_meal)

  if current_user.id != meal.id_user:
    return jsonify({"message": "Operação não permitida"}), 403

  if meal and meal.id_user == current_user.id:
    data = request.get_json()
    meal.name = data.get("name")
    meal.description = data.get("description")
    meal.date = data.get("date")
    meal.is_diet = data.get("is_diet")
    db.session.commit()

    return jsonify({"message": "Dados da refeição alterados com sucesso."})

  return jsonify({"message": "Refeição não encontrada"}), 404

@app.route('/meal/<id_meal>', methods=['DELETE'])
@login_required
def delete_meal(id_meal):
  meal = Meal.query.get(id_meal)

  if meal.id_user == current_user.id:
    
    db.session.delete(meal)
    db.session.commit()

    return jsonify({"message": "Refeição deletada com sucesso."})

  return jsonify({"message": "Refeição não encontrada"}), 404

if __name__ == '__main__':
  app.run(debug=True)