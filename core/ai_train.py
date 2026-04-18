import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

def generate_synthetic_data(num_samples=1000):
    """
    Generate realistic synthetic health data for a stress monitoring project.
    Features: Sleep(hrs), Screen(hrs), Mood(num), BMI(float), Activity(num)
    """
    np.random.seed(42)
    
    # 1. Sleep: 4-10 hours
    sleep = np.random.uniform(4, 10, num_samples)
    
    # 2. Screen: 1-14 hours
    screen = np.random.uniform(1, 14, num_samples)
    
    # 3. Mood: 1(Pleasant), 2(Neutral), 3(Stressed)
    mood = np.random.randint(1, 4, num_samples)
    
    # 4. BMI: 18-40
    bmi = np.random.uniform(18, 40, num_samples)
    
    # 5. Activity: 1(Sedentary), 2(Light), 3(Moderate), 4(Active)
    activity = np.random.randint(1, 5, num_samples)
    
    # --- The Equation for Ground Truth (Stress %) ---
    # Enhanced Non-Linear Logic for realistic AI learning
    stress = 25 + \
             (7.5 - sleep) * 12 + \
             (screen - 3.5) * 6 + \
             (mood - 1) * 22 + \
             ((bmi / 22) ** 2) * 5 - \
             (activity - 1) * 8
    
    # Add non-linear interactions (e.g., poor sleep makes screen time worse)
    stress += (sleep < 6) * (screen > 7) * 15
    stress += (bmi > 30) * 10
    
    # Add significant Gaussian noise for realism
    stress += np.random.normal(0, 8, num_samples)
    
    # Clip to 0-100 range
    stress = np.clip(stress, 5, 100)
    
    data = pd.DataFrame({
        'sleep_time': sleep,
        'screen_time': screen,
        'mood_encoded': mood,
        'bmi': bmi,
        'activity_encoded': activity,
        'stress_percentage': stress
    })
    
    return data

def train_and_save():
    print("Generating enriched synthetic data (5,000 samples)...")
    data = generate_synthetic_data(num_samples=5000)
    
    # Prepare features and target
    X = data[['sleep_time', 'screen_time', 'mood_encoded', 'bmi', 'activity_encoded']]
    y = data['stress_percentage']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    # Train
    print("Training RandomForest model (optimized for granularity)...")
    model = RandomForestRegressor(n_estimators=200, max_depth=12, min_samples_leaf=3, random_state=42)
    model.fit(X_train, y_train)
    
    # Score
    score = model.score(X_test, y_test)
    print(f"Model R^2 Score: {score:.4f}")
    
    # Save
    os.makedirs('core/ai_models', exist_ok=True)
    model_path = 'core/ai_models/health_stress_model.joblib'
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    # Save a small sample for CSV inspection if needed
    data.head(100).to_csv('core/ai_models/health_data_sample.csv', index=False)
    print("Sample CSV saved.")

if __name__ == "__main__":
    train_and_save()
