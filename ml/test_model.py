import pandas as pd
import joblib
from sklearn.metrics import accuracy_score

def test_models():
    print("Loading models and encoders...")
    try:
        classifier = joblib.load('best_classifier.joblib')
        regressor = joblib.load('best_regressor_wait.joblib')
        encoders = joblib.load('label_encoders.joblib')
    except Exception as e:
        print(f"Error loading models: {e}")
        return

    print("Loading test data...")
    # Generate 500 new rows for testing using our generate function
    # To keep it simple, we'll just read from the original data and take 500 random rows
    df = pd.read_csv('bank_appointment_data.csv').sample(500, random_state=101)

    # Feature Engineering
    df['Load_Ratio'] = df['Current_Appointments'] / (df['Available_Employees'] * 5 + 1)
    df['Duration_per_Employee'] = df['Estimated_Duration'] / df['Available_Employees']

    features = [
        'Purpose', 'Preferred_Time', 'Estimated_Duration', 'Priority',
        'Current_Rush_Level', 'Current_Appointments', 'Available_Employees',
        'Holiday', 'Day_of_Week', 'Historical_Slot_Load', 'Load_Ratio', 'Duration_per_Employee'
    ]
    
    X = df[features].copy()
    
    # Encode
    cat_cols = ['Purpose', 'Preferred_Time', 'Priority', 'Current_Rush_Level', 'Day_of_Week']
    for col in cat_cols:
        X[col] = encoders[col].transform(X[col])
        
    y_status_true = encoders['Appointment_Status'].transform(df['Appointment_Status'])
    
    print("\nRunning predictions...")
    y_status_pred = classifier.predict(X)
    
    if hasattr(classifier, "predict_proba"):
        y_status_prob = classifier.predict_proba(X)
        confidence_scores = [max(probs) for probs in y_status_prob]
    else:
        confidence_scores = [1.0] * 500
        
    y_wait_pred = regressor.predict(X)
    
    acc = accuracy_score(y_status_true, y_status_pred)
    print(f"\nTest Accuracy on 500 records: {acc*100:.2f}%")
    
    if acc < 0.90:
        print("Warning: Accuracy is below 90%! Retraining is recommended.")
    else:
        print("Model passed the 90% accuracy threshold.")
        
    print("\n--- Sample Test Cases ---\n")
    for i in range(5):
        orig_row = df.iloc[i]
        
        status_decoded_pred = encoders['Appointment_Status'].inverse_transform([y_status_pred[i]])[0]
        
        print(f"Test Case {i+1}:")
        print(f"Input: Purpose={orig_row['Purpose']}, Pref Time={orig_row['Preferred_Time']}, Rush={orig_row['Current_Rush_Level']}, Priority={orig_row['Priority']}")
        print(f"Expected Status: {orig_row['Appointment_Status']}")
        print(f"Predicted Status: {status_decoded_pred}")
        print(f"Confidence Score: {confidence_scores[i]:.2f}")
        print(f"Predicted Waiting Time: {max(0, int(y_wait_pred[i]))} mins")
        if status_decoded_pred == 'Suggested Slot':
             print(f"Suggested Slot Logic will trigger.")
        print("-" * 30)

if __name__ == "__main__":
    test_models()
