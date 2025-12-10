from flask import jsonify, request, Blueprint
from app.database import db
from flask_login import current_user, login_required
from ..models.meal import Meal

meal_bp = Blueprint('meal', __name__)

@meal_bp.route('/meal', methods=['POST'])
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

@meal_bp.route('/meal/<id_meal>', methods=['GET'])
@login_required
def read_user_meal(id_meal):
  meal = Meal.query.get(id_meal)

  if meal and meal.id_user == current_user.id:
    return jsonify({"name": meal.name, "description": meal.description, "date": meal.date.isoformat(), "created": meal.created.isoformat(), "is_diet": meal.is_diet})

  return jsonify({"message": "Refeição não encontrada."}), 404

@meal_bp.route('/meals', methods=['GET'])
@login_required
def list_all_user_meals():
  meals =  Meal.query.filter(Meal.id_user == current_user.id).all()
  meals_list = [meal.to_dict() for meal in meals]
  if meals:
    return jsonify({"meals": meals_list, "total": len(meals_list)})
  
  return jsonify({"message": "Nenhuma refeição foi encotrada"}), 404

@meal_bp.route('/meal/<id_meal>', methods=['PUT'])
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

@meal_bp.route('/meal/<id_meal>', methods=['DELETE'])
@login_required
def delete_meal(id_meal):
  meal = Meal.query.get(id_meal)

  if meal.id_user == current_user.id:
    
    db.session.delete(meal)
    db.session.commit()

    return jsonify({"message": "Refeição deletada com sucesso."})

  return jsonify({"message": "Refeição não encontrada"}), 404
