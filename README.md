# AI-Based Smart Bank Appointment Scheduling and Queue Management System

## Overview
This is an end-to-end Machine Learning project aimed at reducing bank crowds by intelligently scheduling appointments using AI.

## Project Structure
- `/ml`: Contains synthetic data generation (20,000 records) and Machine Learning model training scripts using `LightGBM`, `XGBoost`, `CatBoost`, and `RandomForest` evaluated via `GridSearchCV`. Models are exported as `.joblib` files.
- `/backend`: A Python Flask API running on SQLite. It connects the trained ML model with the live API to predict appointment status, wait times, and queue positions.
- `/frontend`: A modern React application using Vite, Tailwind CSS, Recharts, and Lucide React. Contains Customer booking portal, Employee live queue, and Admin analytics.
- `/docs`: Contains Mermaid diagrams (ER, Architecture, Flowcharts).

## Installation & Run Guide

### 1. Backend & ML Environment
Make sure you have Python 3.10+ installed.

```bash
# 1. Activate the virtual environment
.\venv\Scripts\activate

# 2. Run the Flask Backend
cd backend
python app.py
```
*(The backend will start on http://127.0.0.1:5000 and auto-generate the `database.db`)*

### 2. Frontend Environment
Make sure you have Node.js installed.

```bash
# 1. Navigate to frontend
cd frontend

# 2. Start Vite Dev Server
npm run dev
```
*(The frontend will start on http://localhost:5173)*

## How to Test
1. Open the Customer Portal (`http://localhost:5173/`).
2. Submit a booking. The ML model will instantly predict if it should be Accepted, Rejected, or if a better slot should be Suggested based on the live queue and your priority status.
3. Open the Employee Dashboard (`http://localhost:5173/employee`) to see the request appear live.
4. Try cancelling an appointment to see the **First Come First Serve (FCFS)** logic automatically promote someone from the Waiting List!
