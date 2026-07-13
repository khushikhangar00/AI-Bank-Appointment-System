from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(20), db.ForeignKey('customer.customer_id'), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)
    preferred_date = db.Column(db.String(20), nullable=False)
    preferred_time = db.Column(db.String(20), nullable=False)
    estimated_duration = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    request_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ML Outputs / System Assigns
    status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Rejected, Cancelled
    ai_recommendation = db.Column(db.String(20), nullable=True) # Accepted, Rejected, Suggested Slot
    suggested_slot = db.Column(db.String(20), nullable=True)
    actual_allocated_slot = db.Column(db.String(20), nullable=True)
    queue_position = db.Column(db.Integer, default=0)
    waiting_time = db.Column(db.Integer, default=0)
    
class SystemState(db.Model):
    # To mock live bank settings (rush level, active employees)
    id = db.Column(db.Integer, primary_key=True)
    current_rush_level = db.Column(db.String(20), default="Medium")
    available_employees = db.Column(db.Integer, default=5)
    is_holiday = db.Column(db.Boolean, default=False)
    historical_slot_load = db.Column(db.Float, default=0.5)
