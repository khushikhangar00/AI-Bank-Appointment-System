import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_dataset(num_rows=20000, output_file='bank_appointment_data.csv'):
    np.random.seed(42)
    random.seed(42)

    purposes = [
        'Account Opening', 'Cash Deposit', 'Cash Withdrawal', 'Loan Inquiry', 'Loan Approval', 
        'Locker Service', 'KYC Update', 'Debit Card Issue', 'Credit Card Issue', 'Cheque Deposit', 
        'Cheque Clearance', 'Passbook Update', 'Demand Draft', 'RTGS/NEFT', 'Document Verification', 
        'Fixed Deposit', 'Gold Loan', 'Personal Loan', 'Education Loan', 'Home Loan', 'Complaint', 'Other'
    ]
    
    # Mapping purpose to roughly estimated duration (minutes)
    purpose_duration_map = {
        'Account Opening': 30, 'Cash Deposit': 10, 'Cash Withdrawal': 10, 'Loan Inquiry': 20, 
        'Loan Approval': 45, 'Locker Service': 15, 'KYC Update': 15, 'Debit Card Issue': 15, 
        'Credit Card Issue': 15, 'Cheque Deposit': 5, 'Cheque Clearance': 10, 'Passbook Update': 5, 
        'Demand Draft': 15, 'RTGS/NEFT': 10, 'Document Verification': 20, 'Fixed Deposit': 20, 
        'Gold Loan': 45, 'Personal Loan': 30, 'Education Loan': 30, 'Home Loan': 45, 'Complaint': 20, 'Other': 15
    }

    time_slots = [
        '09:30-10:00', '10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00', '12:00-12:30', '12:30-13:00', 
        '14:00-14:30', '14:30-15:00', '15:00-15:30', '15:30-16:00', '16:00-16:30'
    ]

    priorities = ['Normal', 'Senior Citizen', 'Disabled']
    rush_levels = ['Low', 'Medium', 'High', 'Very High']
    statuses = ['Accepted', 'Rejected', 'Suggested Slot']

    data = []
    
    start_date = datetime(2023, 1, 1)

    for i in range(num_rows):
        customer_id = f"CUST{str(i).zfill(6)}"
        purpose = np.random.choice(purposes)
        duration = purpose_duration_map[purpose] + np.random.randint(-5, 6) # small variance
        duration = max(5, duration)
        
        priority = np.random.choice(priorities, p=[0.7, 0.2, 0.1])
        
        # Random date in a 1-year span
        days_offset = np.random.randint(0, 365)
        pref_date = start_date + timedelta(days=days_offset)
        day_of_week = pref_date.strftime('%A')
        
        is_holiday = 1 if day_of_week == 'Sunday' or np.random.random() < 0.05 else 0
        
        pref_time_idx = np.random.randint(0, len(time_slots))
        pref_time = time_slots[pref_time_idx]
        
        request_timestamp = pref_date - timedelta(days=np.random.randint(1, 14), hours=np.random.randint(0, 24))
        
        current_rush_level = np.random.choice(rush_levels, p=[0.3, 0.4, 0.2, 0.1])
        available_employees = np.random.randint(3, 10)
        current_appointments = np.random.randint(0, 50)
        
        historical_load = np.random.uniform(0.1, 0.9)
        if time_slots.index(pref_time) in [0, 1, 7, 8]: # Morning and post-lunch rush
            historical_load = np.random.uniform(0.6, 1.0)
            
        cancellation = 1 if np.random.random() < 0.1 else 0
        rescheduled = 1 if np.random.random() < 0.05 else 0

        # Simulate logical outputs based on constraints
        if is_holiday == 1:
            status = 'Rejected'
            suggested_slot = 'None'
            actual_slot = 'None'
            wait_time = 0
            queue_pos = 0
        else:
            # Capacity logic
            slot_capacity = available_employees * (30 / np.mean([purpose_duration_map[p] for p in purposes])) 
            slot_capacity = max(1, int(slot_capacity))
            
            simulated_current_bookings_for_slot = np.random.randint(0, int(slot_capacity * 1.5))
            
            # Purely deterministic logic for ML to learn perfectly
            load_ratio = current_appointments / (available_employees * 5 + 1)
            
            if priority == 'Disabled' or priority == 'Senior Citizen':
                if load_ratio > 1.8:
                    status = 'Suggested Slot'
                else:
                    status = 'Accepted'
            else:
                if load_ratio > 1.2:
                    status = 'Rejected'
                elif load_ratio > 0.8:
                    status = 'Suggested Slot'
                else:
                    status = 'Accepted'

            if status == 'Accepted':
                suggested_slot = pref_time
                actual_slot = pref_time
                # Queue position and wait time
                queue_pos = max(1, simulated_current_bookings_for_slot - priority_score)
                wait_time = max(0, int(queue_pos * duration / available_employees) + np.random.randint(-2, 5))
            elif status == 'Suggested Slot':
                # Suggest next available slot
                suggested_idx = min(len(time_slots) - 1, pref_time_idx + np.random.randint(1, 3))
                suggested_slot = time_slots[suggested_idx]
                actual_slot = suggested_slot if np.random.random() > 0.5 else 'None'
                queue_pos = 0
                wait_time = 0
            else:
                suggested_slot = 'None'
                actual_slot = 'None'
                queue_pos = 0
                wait_time = 0

        employee_id = f"EMP{np.random.randint(1, 20):03d}" if actual_slot != 'None' else 'None'
        customer_feedback = np.random.randint(1, 6) if actual_slot != 'None' else np.nan

        data.append({
            'Customer_ID': customer_id,
            'Purpose': purpose,
            'Preferred_Date': pref_date.strftime('%Y-%m-%d'),
            'Preferred_Time': pref_time,
            'Estimated_Duration': duration,
            'Priority': priority,
            'Current_Rush_Level': current_rush_level,
            'Current_Appointments': current_appointments,
            'Available_Employees': available_employees,
            'Holiday': is_holiday,
            'Day_of_Week': day_of_week,
            'Request_Timestamp': request_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Appointment_Status': status,
            'Suggested_Slot': suggested_slot,
            'Actual_Allocated_Slot': actual_slot,
            'Queue_Position': queue_pos,
            'Waiting_Time': wait_time,
            'Cancellation': cancellation,
            'Rescheduled': rescheduled,
            'Employee_ID': employee_id,
            'Customer_Feedback': customer_feedback,
            'Historical_Slot_Load': round(historical_load, 2)
        })

    df = pd.DataFrame(data)
    # Fill NAs for feedback
    df['Customer_Feedback'] = df['Customer_Feedback'].fillna(3)
    
    df.to_csv(output_file, index=False)
    print(f"Dataset with {num_rows} rows saved to {output_file}")

if __name__ == "__main__":
    generate_dataset()
