from database import db

class Meal(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  description = db.Column(db.Text, nullable=True)
  date = db.Column(db.DateTime, nullable=False)
  is_diet = db.Column(db.Boolean, nullable=False, default=False)