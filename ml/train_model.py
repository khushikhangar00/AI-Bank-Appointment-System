import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, mean_squared_error, r2_score
import joblib

# ML Models
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from catboost import CatBoostClassifier, CatBoostRegressor

def preprocess_data(filepath='bank_appointment_data.csv'):
    df = pd.read_csv(filepath)
    
    # Feature Engineering
    df['Load_Ratio'] = df['Current_Appointments'] / (df['Available_Employees'] * 5 + 1)
    df['Duration_per_Employee'] = df['Estimated_Duration'] / df['Available_Employees']
    
    # Features to use
    features = [
        'Purpose', 'Preferred_Time', 'Estimated_Duration', 'Priority',
        'Current_Rush_Level', 'Current_Appointments', 'Available_Employees',
        'Holiday', 'Day_of_Week', 'Historical_Slot_Load', 'Load_Ratio', 'Duration_per_Employee'
    ]
    
    X = df[features].copy()
    
    # Target variables
    y_status = df['Appointment_Status']
    y_wait = df['Waiting_Time']
    y_queue = df['Queue_Position']
    
    # Encoders dict
    encoders = {}
    
    # Categorical columns
    cat_cols = ['Purpose', 'Preferred_Time', 'Priority', 'Current_Rush_Level', 'Day_of_Week']
    
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le
        
    status_encoder = LabelEncoder()
    y_status_encoded = status_encoder.fit_transform(y_status)
    encoders['Appointment_Status'] = status_encoder
    
    return X, y_status_encoded, y_wait, y_queue, encoders

def train_status_classifier(X_train, y_train, X_test, y_test):
    print("Training Classification Models for Appointment Status...")
    
    models = {
        'Decision Tree': (DecisionTreeClassifier(random_state=42), {'max_depth': [5, 10, None]}),
        'Random Forest': (RandomForestClassifier(random_state=42), {'n_estimators': [50, 100], 'max_depth': [10, 20]}),
        'Logistic Regression': (LogisticRegression(max_iter=1000, random_state=42), {'C': [0.1, 1.0]}),
        'XGBoost': (XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42), {'n_estimators': [50, 100], 'max_depth': [3, 5]}),
        'LightGBM': (LGBMClassifier(random_state=42), {'n_estimators': [50, 100], 'learning_rate': [0.05, 0.1]}),
        'CatBoost': (CatBoostClassifier(verbose=0, random_state=42), {'iterations': [50, 100], 'depth': [4, 6]}),
        'Gradient Boosting': (GradientBoostingClassifier(random_state=42), {'n_estimators': [50, 100], 'learning_rate': [0.05, 0.1]})
    }
    
    best_model_name = None
    best_model = None
    best_accuracy = 0
    
    results = {}
    
    for name, (model, params) in models.items():
        print(f"Training {name}...")
        grid = GridSearchCV(model, params, cv=3, scoring='accuracy', n_jobs=-1)
        grid.fit(X_train, y_train)
        
        y_pred = grid.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        
        results[name] = acc
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model = grid.best_estimator_
            best_model_name = name
            
    print(f"\nBest Classification Model: {best_model_name} with Accuracy: {best_accuracy:.4f}")
    
    # Detailed metrics for best model
    y_pred_best = best_model.predict(X_test)
    print(classification_report(y_test, y_pred_best))
    
    return best_model

def train_wait_time_regressor(X_train, y_train, X_test, y_test):
    print("\nTraining Regression Models for Waiting Time...")
    
    models = {
        'Random Forest': (RandomForestRegressor(random_state=42), {'n_estimators': [50, 100]}),
        'XGBoost': (XGBRegressor(random_state=42), {'n_estimators': [50, 100]}),
        'LightGBM': (LGBMRegressor(random_state=42), {'n_estimators': [50, 100]})
    }
    
    best_model_name = None
    best_model = None
    best_r2 = -float('inf')
    
    for name, (model, params) in models.items():
        print(f"Training {name}...")
        grid = GridSearchCV(model, params, cv=3, scoring='r2', n_jobs=-1)
        grid.fit(X_train, y_train)
        
        y_pred = grid.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = grid.best_estimator_
            best_model_name = name
            
    print(f"\nBest Regression Model (Wait Time): {best_model_name} with R2 Score: {best_r2:.4f}")
    return best_model

def main():
    X, y_status, y_wait, y_queue, encoders = preprocess_data()
    
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X, y_status, test_size=0.2, random_state=42)
    
    best_classifier = train_status_classifier(X_train_s, y_train_s, X_test_s, y_test_s)
    
    X_train_w, X_test_w, y_train_w, y_test_w = train_test_split(X, y_wait, test_size=0.2, random_state=42)
    best_regressor_wait = train_wait_time_regressor(X_train_w, y_train_w, X_test_w, y_test_w)
    
    # Save the models and encoders
    joblib.dump(best_classifier, 'best_classifier.joblib')
    joblib.dump(best_regressor_wait, 'best_regressor_wait.joblib')
    joblib.dump(encoders, 'label_encoders.joblib')
    print("Models and encoders saved successfully.")

if __name__ == "__main__":
    main()
