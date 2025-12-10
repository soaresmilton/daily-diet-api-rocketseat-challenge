from datetime import datetime
from app.database import db

class Meal(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  description = db.Column(db.Text, nullable=True)
  date = db.Column(db.DateTime, nullable=False)
  is_diet = db.Column(db.Boolean, nullable=False, default=False)
  id_user = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, nullable=False,  default=datetime.now())

  def to_dict(self):
    return {
      "id": self.id,
      "name": self.name,
      "description": self.description,
      "date": self.date.isoformat(),
      "is_diet": self.is_diet,
      "id_user": self.id_user,
      "created": self.created.isoformat()
    }