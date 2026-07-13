import joblib
import pandas as pd
import os

# Paths to models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ML_DIR = os.path.join(BASE_DIR, 'ml')

class AIService:
    def __init__(self):
        try:
            self.classifier = joblib.load(os.path.join(ML_DIR, 'best_classifier.joblib'))
            self.regressor = joblib.load(os.path.join(ML_DIR, 'best_regressor_wait.joblib'))
            self.encoders = joblib.load(os.path.join(ML_DIR, 'label_encoders.joblib'))
            print("AI Models loaded successfully.")
        except Exception as e:
            print(f"Error loading AI models: {e}")
            self.classifier = None
            self.regressor = None
            self.encoders = None
            
    def predict_appointment(self, appointment_data, system_state):
        """
        appointment_data dict: Purpose, Preferred_Time, Estimated_Duration, Priority, Day_of_Week
        system_state dict: Current_Rush_Level, Current_Appointments, Available_Employees, Holiday, Historical_Slot_Load
        """
        if not self.classifier:
            return {"error": "Models not loaded"}
            
        features = [
            'Purpose', 'Preferred_Time', 'Estimated_Duration', 'Priority',
            'Current_Rush_Level', 'Current_Appointments', 'Available_Employees',
            'Holiday', 'Day_of_Week', 'Historical_Slot_Load', 'Load_Ratio', 'Duration_per_Employee'
        ]
        
        load_ratio = system_state['Current_Appointments'] / (system_state['Available_Employees'] * 5 + 1)
        duration_per_employee = appointment_data['Estimated_Duration'] / system_state['Available_Employees']

        # Build dataframe row
        row = {
            'Purpose': appointment_data['Purpose'],
            'Preferred_Time': appointment_data['Preferred_Time'],
            'Estimated_Duration': appointment_data['Estimated_Duration'],
            'Priority': appointment_data['Priority'],
            'Current_Rush_Level': system_state['Current_Rush_Level'],
            'Current_Appointments': system_state['Current_Appointments'],
            'Available_Employees': system_state['Available_Employees'],
            'Holiday': system_state['Holiday'],
            'Day_of_Week': appointment_data['Day_of_Week'],
            'Historical_Slot_Load': system_state['Historical_Slot_Load'],
            'Load_Ratio': load_ratio,
            'Duration_per_Employee': duration_per_employee
        }
        
        df = pd.DataFrame([row])
        
        # Encode categorical
        cat_cols = ['Purpose', 'Preferred_Time', 'Priority', 'Current_Rush_Level', 'Day_of_Week']
        for col in cat_cols:
            df[col] = self.encoders[col].transform(df[col])
            
        # Predict
        status_encoded = self.classifier.predict(df)[0]
        wait_pred = self.regressor.predict(df)[0]
        
        status = self.encoders['Appointment_Status'].inverse_transform([status_encoded])[0]
        wait_time = max(0, int(wait_pred))
        
        if hasattr(self.classifier, "predict_proba"):
            probs = self.classifier.predict_proba(df)[0]
            confidence = max(probs)
        else:
            confidence = 1.0
            
        # If suggested slot, we can logically calculate the next slot based on preference
        suggested_slot = "None"
        if status == 'Suggested Slot':
            time_slots = [
                '09:30-10:00', '10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00', '12:00-12:30', '12:30-13:00', 
                '14:00-14:30', '14:30-15:00', '15:00-15:30', '15:30-16:00', '16:00-16:30'
            ]
            try:
                idx = time_slots.index(appointment_data['Preferred_Time'])
                # Suggest next available slot (simplified)
                suggested_slot = time_slots[min(len(time_slots)-1, idx+1)]
            except:
                pass
                
        return {
            'predicted_status': status,
            'suggested_slot': suggested_slot,
            'waiting_time': wait_time,
            'confidence': round(confidence * 100, 2)
        }

ai_service = AIService()
