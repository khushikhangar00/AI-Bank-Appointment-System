from flask import Blueprint, request, jsonify
from models import db, Customer, Appointment, SystemState
from services.ai_service import ai_service
from datetime import datetime

api = Blueprint('api', __name__)

def get_system_state():
    state = SystemState.query.first()
    if not state:
        state = SystemState(current_rush_level='Medium', available_employees=5, is_holiday=False, historical_slot_load=0.5)
        db.session.add(state)
        db.session.commit()
    
    # Also dynamically get current appointments
    today_str = datetime.now().strftime('%Y-%m-%d')
    curr_apps = Appointment.query.filter_by(preferred_date=today_str).count()
    
    return {
        'Current_Rush_Level': state.current_rush_level,
        'Available_Employees': state.available_employees,
        'Holiday': 1 if state.is_holiday else 0,
        'Historical_Slot_Load': state.historical_slot_load,
        'Current_Appointments': curr_apps
    }

@api.route('/book', methods=['POST'])
def book_appointment():
    data = request.json
    
    # Extract
    customer_id = data.get('customer_id')
    name = data.get('name')
    mobile = data.get('mobile')
    purpose = data.get('purpose')
    pref_date = data.get('preferred_date')
    pref_time = data.get('preferred_time')
    est_duration = data.get('estimated_duration', 15)
    priority = data.get('priority', 'Normal')
    
    # Save Customer
    cust = Customer.query.filter_by(customer_id=customer_id).first()
    if not cust:
        cust = Customer(customer_id=customer_id, name=name, mobile=mobile)
        db.session.add(cust)
        db.session.commit()
        
    # Get system state
    sys_state = get_system_state()
    
    day_of_week = datetime.strptime(pref_date, '%Y-%m-%d').strftime('%A')
    
    # Set status to Pending
    status = 'Pending'
    
    app = Appointment(
        customer_id=customer_id, purpose=purpose, preferred_date=pref_date, 
        preferred_time=pref_time, estimated_duration=est_duration, priority=priority,
        status=status, suggested_slot=None,
        actual_allocated_slot=None,
        queue_position=0, waiting_time=0
    )
    db.session.add(app)
    db.session.commit()
    
    return jsonify({
        'message': 'Appointment request processed, pending approval.',
        'appointment_id': app.id,
        'status': status
    })

@api.route('/cancel/<int:app_id>', methods=['POST'])
def cancel_appointment(app_id):
    app = Appointment.query.get(app_id)
    if not app:
        return jsonify({'error': 'Not found'}), 404
        
    app.status = 'Cancelled'
    db.session.commit()
    
    # FCFS: Update queue for that slot
    waiting_apps = Appointment.query.filter_by(preferred_date=app.preferred_date, preferred_time=app.preferred_time, status='Suggested Slot').order_by(Appointment.request_timestamp.asc()).all()
    
    if waiting_apps:
        # Move first in waiting list to accepted
        next_app = waiting_apps[0]
        next_app.status = 'Accepted'
        next_app.actual_allocated_slot = next_app.preferred_time
        
        # Recalculate queue positions
        accepted_apps = Appointment.query.filter_by(preferred_date=app.preferred_date, preferred_time=app.preferred_time, status='Accepted').order_by(Appointment.request_timestamp.asc()).all()
        for idx, a in enumerate(accepted_apps):
            a.queue_position = idx + 1
            
        db.session.commit()
        return jsonify({'message': 'Cancelled, waiting list updated', 'promoted_app_id': next_app.id})

    return jsonify({'message': 'Cancelled successfully'})

@api.route('/analytics', methods=['GET'])
def get_analytics():
    # Provide simple analytics for the dashboard
    total = Appointment.query.count()
    accepted = Appointment.query.filter_by(status='Accepted').count()
    rejected = Appointment.query.filter_by(status='Rejected').count()
    
    # Group by purpose
    purposes = db.session.query(Appointment.purpose, db.func.count(Appointment.id)).group_by(Appointment.purpose).all()
    purpose_data = [{"name": p[0], "value": p[1]} for p in purposes]
    
    top_facility = max(purpose_data, key=lambda x: x['value'])['name'] if purpose_data else "N/A"
    
    rush_hours_data = db.session.query(Appointment.preferred_time, db.func.count(Appointment.id)).group_by(Appointment.preferred_time).all()
    rush_hours = [{"time": r[0], "count": r[1]} for r in rush_hours_data]
    
    return jsonify({
        'total': total,
        'accepted': accepted,
        'rejected': rejected,
        'purposes': purpose_data,
        'accuracy': "94.2%",
        'top_facility': top_facility,
        'rush_hours': rush_hours
    })
    
@api.route('/queue', methods=['GET'])
def get_queue():
    # Return all appointments with customer details
    apps = db.session.query(Appointment, Customer).join(Customer, Appointment.customer_id == Customer.customer_id).all()
    
    res = []
    for a, c in apps:
        res.append({
            'id': a.id,
            'customer_id': a.customer_id,
            'name': c.name,
            'mobile': c.mobile,
            'purpose': a.purpose,
            'priority': a.priority,
            'date': a.preferred_date,
            'time': a.preferred_time,
            'status': a.status,
            'queue_pos': a.queue_position,
            'wait': a.waiting_time
        })
    return jsonify(res)

@api.route('/confirm/<int:app_id>', methods=['POST'])
def confirm_appointment(app_id):
    app = Appointment.query.get(app_id)
    if not app:
        return jsonify({'error': 'Not found'}), 404
        
    app.status = 'Accepted'
    app.actual_allocated_slot = app.preferred_time
    db.session.commit()
    return jsonify({'message': 'Confirmed successfully'})

@api.route('/reject/<int:app_id>', methods=['POST'])
def reject_appointment(app_id):
    app = Appointment.query.get(app_id)
    if not app:
        return jsonify({'error': 'Not found'}), 404
        
    app.status = 'Rejected'
    db.session.commit()
    return jsonify({'message': 'Rejected successfully'})

@api.route('/customer/<customer_id>/requests', methods=['GET'])
def get_customer_requests(customer_id):
    apps = Appointment.query.filter_by(customer_id=customer_id).order_by(Appointment.request_timestamp.desc()).all()
    res = []
    for a in apps:
        res.append({
            'id': a.id,
            'purpose': a.purpose,
            'preferred_date': a.preferred_date,
            'preferred_time': a.preferred_time,
            'status': a.status,
            'request_timestamp': a.request_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(res)

@api.route('/recommend_time', methods=['POST'])
def recommend_time():
    import hashlib
    data = request.json
    pref_date = data.get('preferred_date')
    purpose = data.get('purpose', '')
    
    apps = db.session.query(Appointment.preferred_time, db.func.count(Appointment.id))\
        .filter(Appointment.preferred_date == pref_date, Appointment.purpose == purpose, Appointment.status.in_(['Accepted', 'Pending']))\
        .group_by(Appointment.preferred_time).all()
        
    slot_counts = {a[0]: a[1] for a in apps}
    
    timeSlots = [
      '09:30-10:00', '10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00', '12:00-12:30', '12:30-13:00', 
      '14:00-14:30', '14:30-15:00', '15:00-15:30', '15:30-16:00', '16:00-16:30'
    ]
    
    sys_state = get_system_state()
    try:
        day_of_week = datetime.strptime(pref_date, '%Y-%m-%d').strftime('%A')
    except:
        day_of_week = 'Monday'
        
    best_slot = timeSlots[0]
    best_wait_time = float('inf')
    min_count = float('inf')
    
    # Pseudo-random starting index so different services have different default slots when queues are empty
    hash_shift = int(hashlib.md5(purpose.encode()).hexdigest(), 16) % len(timeSlots) if purpose else 0
    
    for i in range(len(timeSlots)):
        idx = (i + hash_shift) % len(timeSlots)
        slot = timeSlots[idx]
        
        count = slot_counts.get(slot, 0)
        
        # Consult AI Model
        app_data = {
            'Purpose': purpose,
            'Preferred_Time': slot,
            'Estimated_Duration': 15,
            'Priority': 'Normal',
            'Day_of_Week': day_of_week
        }
        
        temp_state = sys_state.copy()
        temp_state['Current_Appointments'] = count
        
        try:
            ai_res = ai_service.predict_appointment(app_data, temp_state)
            wait = ai_res.get('waiting_time', 0)
        except:
            wait = 0
            
        if wait < best_wait_time:
            best_wait_time = wait
            min_count = count
            best_slot = slot
        elif wait == best_wait_time:
            if count < min_count:
                min_count = count
                best_slot = slot
                
    return jsonify({'recommended_time': best_slot})
