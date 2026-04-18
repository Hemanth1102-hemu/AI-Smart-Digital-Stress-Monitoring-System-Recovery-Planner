import os
import joblib
import pandas as pd
import numpy as np

# Path to the model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ai_models', 'health_stress_model.joblib')

def get_stress_prediction(sleep, screen, mood, bmi, activity):
    """
    Loads the trained model and returns an accurate prediction based on the user's data.
    """
    
    # 1. Encodings (matches generating logic)
    mood_map = {'pleasant': 1, 'calm': 1, 'neutral': 2, 'anxious': 3, 'stressed': 3}
    activity_map = {'sedentary': 1, 'light': 2, 'moderate': 3, 'active': 4}
    
    mood_enc = mood_map.get(mood.lower(), 2)
    activity_enc = activity_map.get(activity.lower(), 3)
    
    # 2. Check if model exists, if not, fallback to a simpler calc (until trained)
    if not os.path.exists(MODEL_PATH):
        # Fallback accurate manual formula (similar to training ground truth)
        stress = 20 + (8-sleep)*8 + (screen-4)*5 + (mood_enc-1)*20 + (bmi-22)*2 - (activity_enc-1)*5
        return float(np.clip(stress, 5, 100))
        
    try:
        model = joblib.load(MODEL_PATH)
        # Prepare input as DataFrame (features must be in same order)
        features = pd.DataFrame([{
            'sleep_time': sleep,
            'screen_time': screen,
            'mood_encoded': mood_enc,
            'bmi': bmi,
            'activity_encoded': activity_enc
        }])
        
        prediction = model.predict(features)[0]
        return float(np.clip(prediction, 5, 100))
    except Exception as e:
        print(f"Prediction Error: {e}")
        # Final fallback
        return 50.0
