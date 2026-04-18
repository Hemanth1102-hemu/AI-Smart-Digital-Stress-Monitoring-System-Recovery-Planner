from django.shortcuts import render, redirect
from django.http import JsonResponse
import random
import hashlib
from .models import UserProfile, StressLog
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
import json
import urllib.request
import os

def index(request):
    return render(request, 'core/index.html')

def login_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('fitness_input')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('index')
    return redirect('index')

def signup_view(request):
    if request.method == "POST":
        f = request.POST.get('first_name')
        l = request.POST.get('last_name')
        u = request.POST.get('username')
        p = request.POST.get('password')
        cp = request.POST.get('confirm_password')
        
        if p != cp:
            messages.error(request, 'Passwords do not match.')
            return redirect('index')
            
        if User.objects.filter(username=u).exists():
            messages.error(request, 'Username already exists.')
            return redirect('index')
            
        user = User.objects.create_user(username=u, password=p, first_name=f, last_name=l)
        UserProfile.objects.create(user=user)
        login(request, user)
        return redirect('fitness_input')
    return redirect('index')

def fitness_input(request):
    if request.method == 'POST':
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        age = request.POST.get('age')
        activity = request.POST.get('activity')
        avg_sleep = request.POST.get('avg_sleep')
        avg_screen = request.POST.get('avg_screen')
        
        request.session['weight'] = weight
        request.session['height'] = height
        request.session['age'] = age
        request.session['activity'] = activity
        request.session['avg_sleep'] = avg_sleep
        request.session['avg_screen'] = avg_screen
        
        # Save to DB if user is authenticated (mocking logic if custom auth is pending)
        if request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            if weight: profile.weight = float(weight)
            if height: profile.height = float(height)
            if avg_sleep: profile.avg_sleep = float(avg_sleep)
            if avg_screen: profile.avg_screen = float(avg_screen)
            profile.save()
            
        return redirect('stress_input')
        
    # If GET, try to pre-fill from DB or session
    context = {}
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            context['weight'] = profile.weight
            context['height'] = profile.height
            context['avg_sleep'] = profile.avg_sleep
            context['avg_screen'] = profile.avg_screen
        except UserProfile.DoesNotExist:
            pass
            
    return render(request, 'core/fitness_input.html', context)

def stress_input(request):
    if request.method == 'POST':
        request.session['sleep_time'] = request.POST.get('sleep_time')
        request.session['screen_time'] = request.POST.get('screen_time')
        request.session['mood'] = request.POST.get('mood')
        return redirect('stress_result')
    return render(request, 'core/stress_input.html')

def stress_result(request):
    # Retrieve data
    sleep = float(request.session.get('sleep_time') or 7)
    screen = float(request.session.get('screen_time') or 4)
    mood = request.session.get('mood') or 'neutral'
    weight = float(request.session.get('weight') or 70)
    height = float(request.session.get('height') or 170)
    activity = request.session.get('activity') or 'moderate'
    
    # --- AI-Powered Analysis Engine ---
    from .ai_logic import get_stress_prediction
    
    # Accurate BMI calculation
    bmi = round(weight / ((height / 100) ** 2), 1)
    
    # Local Machine Learning Model Prediction
    # This takes into account the user's specific age (simulated), BMI, sleep, screen time, mood and activity
    stress_score = get_stress_prediction(sleep, screen, mood, bmi, activity)
    
    # 1. Biological Impact Description (Dynamic based on data ranges)
    if sleep < 6:
        sleep_impact, sleep_class = "Critical Sleep Deficit", "text-negative"
    elif sleep < 8:
        sleep_impact, sleep_class = "Minimal Insufficiency", "text-warning"
    else:
        sleep_impact, sleep_class = "Excellent Recovery Sleep", "text-positive"

    # 2. Digital Load Description
    if screen > 9:
        screen_impact, screen_class = "Severe Digital Strain", "text-negative"
    elif screen > 6:
        screen_impact, screen_class = "Significant Exposure", "text-warning"
    else:
        screen_impact, screen_class = "Low Digital Impact", "text-positive"
        
    # 3. Emotional State Label
    mood_impact, mood_class = f"State: {mood.capitalize()}", "text-warning"
    if mood.lower() == 'pleasant': mood_class = "text-positive"
    elif mood.lower() == 'stressed': mood_class = "text-negative"

    # 4. Metabolic Composition Label
    if bmi > 30:
        bmi_impact, bmi_class = "High Metabolic Strain", "text-negative"
    elif bmi > 25:
        bmi_impact, bmi_class = "Moderate Biological Load", "text-warning"
    else:
        bmi_impact, bmi_class = "Optimal BMI Range", "text-positive"
        
    # 5. Physical Synergy Label
    if activity.lower() in ['sedentary', 'light']:
        activity_impact, activity_class = "Insufficient Circulation", "text-warning"
    else:
        activity_impact, activity_class = "Positive Activity Synergy", "text-positive"
        
    # --- Final Logic ---
    stress_percentage = max(5, min(100, stress_score))
    
    if stress_percentage < 35:
        severity = "Stress State: Healthy"
        severity_class = "good"
    elif stress_percentage < 65:
        severity = "Stress State: Moderate Load"
        severity_class = "moderate"
    else:
        severity = "Stress State: High Strain"
        severity_class = "bad"
        
    request.session['stress_percentage'] = stress_percentage

    if request.user.is_authenticated:
        StressLog.objects.create(
            user=request.user,
            sleep_time=sleep,
            screen_time=screen,
            mood=mood,
            concentration="Unknown",
            calculated_stress_percentage=stress_percentage
        )

    context = {
        'stress_percentage': stress_percentage,
        'severity': severity,
        'severity_class': severity_class,
        'sleep_time': sleep,
        'screen_time': screen,
        'mood': mood.capitalize(),
        'sleep_impact': sleep_impact,
        'screen_impact': screen_impact,
        'mood_impact': mood_impact,
        'sleep_impact_class': sleep_class,
        'screen_impact_class': screen_class,
        'mood_impact_class': mood_class,
        'bmi_value': bmi,
        'bmi_impact': bmi_impact,
        'bmi_class': bmi_class,
        'activity_level': activity.capitalize(),
        'activity_impact': activity_impact,
        'activity_class': activity_class,
    }
    return render(request, 'core/stress_result.html', context)

def call_grok_api(system_msg, user_msg):
    api_key = os.environ.get("GROK_API_KEY")
    
    # If API key is missing, return None to handle dynamically
    if not api_key:
        return None

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result['choices'][0]['message']['content']
    except Exception as e:
        return json.dumps([{"title": "Grok API Error", "description": str(e)}])

def generate_unique_plan(session_data, bmi):
    """
    Uses Grok AI to create a uniquely tailored recovery plan based on user state.
    """
    age = str(session_data.get('age') or '25')
    weight = str(session_data.get('weight') or '70')
    height = str(session_data.get('height') or '170')
    activity = str(session_data.get('activity') or 'moderate')
    sleep = str(session_data.get('sleep_time') or '7')
    screen = str(session_data.get('screen_time') or '4')
    mood = str(session_data.get('mood') or 'neutral')
    
    # Use our local AI logic for an accurate stress baseline
    from .ai_logic import get_stress_prediction
    try:
        stress_pred = get_stress_prediction(float(sleep), float(screen), mood, float(bmi), activity)
    except:
        stress_pred = 50.0
    
    system_msg = (
        "You are an expert AI fitness and recovery coach. Provide exactly 3 personalized actionable recovery steps "
        "based on the user's health state. Output strictly as a JSON array of objects with 'title' and 'description' keys. "
        "Do not include markdown formatting or backticks."
    )
    user_msg = (
        f"User Profile: Age {age}, BMI: {bmi}, Activity: {activity}. Current state: "
        f"{sleep}h sleep, {screen}h screen, Mood: {mood}. AI Calculated Stress: {stress_pred}%. "
        "Prescribe a personalized recovery plan. Reference my stress level."
    )
    
    response_content = call_grok_api(system_msg, user_msg)
    
    if response_content is None:
        # Dynamic fallback that works uniquely for different values and age groups
        return [
            {"title": f"BMI {bmi} Recommendation", "description": f"Based on your calculated BMI of {bmi} (Height: {height}cm, Weight: {weight}kg), ensure your caloric intake aligns with a {activity} lifestyle."},
            {"title": f"Physical Routine for {age}yo", "description": f"Considering your age of {age} and your {sleep} hours of sleep, incorporate 20 mins of daily mobility to offset your {screen} hours of screen time."},
            {"title": "Personalized Recovery Tip", "description": f"Since your mood is {mood}, prioritize a short mindfulness session today to maintain your mental clarity."}
        ]
        
    try:
        plan = json.loads(response_content)
    except:
        # Fallback if AI didn't return valid JSON
        plan = [
            {"title": "AI Parsing Error", "description": "The AI provided a response, but it was not in the expected JSON format."},
            {"title": "Raw Output", "description": response_content[:200] + "..."}
        ]
        
    return plan

def recovery_plan(request):
    age = request.session.get('age') or '25'
    weight = request.session.get('weight') or '70'
    height = request.session.get('height') or '170'
    
    try:
        # BMI Calculation
        bmi = round(float(weight) / ((float(height) / 100) ** 2), 1)
    except:
        bmi = 24.0

    plan = generate_unique_plan(request.session, bmi)
    
    past_logs = []
    if request.user.is_authenticated:
        # Exclude the exact one we just created in this session by ordering and offset,
        # or just grab the last 4 and slice. Let's grab the last 3 prior records.
        past_logs = StressLog.objects.filter(user=request.user).order_by('-date_recorded')[1:4]
    
    context = {
        'age': age,
        'weight': weight,
        'height': height,
        'bmi': bmi,
        'sleep_time': request.session.get('sleep_time') or '7',
        'screen_time': request.session.get('screen_time') or '4',
        'activity_level': (request.session.get('activity') or 'moderate').capitalize(),
        'stress_percentage': request.session.get('stress_percentage') or 0,
        'ai_plan': plan,
        'past_logs': past_logs,
    }
    return render(request, 'core/recovery_plan.html', context)

def chat_view(request):
    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Retrieve data from session for context
            age = str(request.session.get('age') or '25')
            weight = str(request.session.get('weight') or '70')
            activity = str(request.session.get('activity') or 'moderate')
            sleep_v = float(request.session.get('sleep_time') or 7)
            screen_v = float(request.session.get('screen_time') or 4)
            mood_v = str(request.session.get('mood') or 'neutral')
            height_v = float(request.session.get('height') or 170)
            
            # Use our new AI logic to get an accurate stress prediction for the chatbot's context
            from .ai_logic import get_stress_prediction
            try:
                # Calculate BMI for prediction context
                bmi_val = round(float(weight) / ((float(height_v) / 100) ** 2), 1)
                stress_pred = get_stress_prediction(
                    sleep_v,
                    screen_v,
                    mood_v,
                    bmi_val,
                    activity
                )
            except:
                stress_pred = 50.0

            system_msg = (
                f"You are a helpful AI health assistant for a user who is {age} years old, weighs {weight}kg, "
                f"with a {activity} activity level. Their current AI-calculated stress load is {stress_pred}%. "
                "Provide personalized health advice based on these metrics. Answer concisely."
            )
            
            api_key = os.environ.get("GROK_API_KEY")
            if not api_key:
                # Smarter local fallback that reacts to keywords
                msg = user_message.lower()
                
                if 'sleep' in msg or 'rest' in msg:
                    response_text = f"Your current sleep is {sleep_v} hours. For your profile, aim for 7-9 hours of consistent REM cycles to lower your {stress_pred}% stress load."
                elif 'screen' in msg or 'digital' in msg or 'eye' in msg:
                    response_text = f"Your screen time is {screen_v} hours. I recommend the 20-20-20 rule: every 20 mins, look 20 feet away for 20 seconds to reduce digital strain."
                elif 'activity' in msg or 'exercise' in msg or 'sedentary' in msg:
                    response_text = f"As a '{activity}' user, incorporating just 15 minutes of zone 2 cardio can significantly improve your metabolic health and lower stress."
                elif 'improve' in msg or 'better' in msg or 'tips' in msg:
                    response_text = f"To improve your {stress_pred}% stress load, I'd suggest focusing first on reducing your {screen_v} hours of screen time. Small gains lead to long-term success!"
                elif 'mood' in msg or 'stress' in msg:
                    response_text = f"With a stress level of {stress_pred}%, your '{mood_v}' mood is a key indicator. Try deep breathing exercises for 5 minutes to reset your nervous system."
                else:
                    response_text = (
                        f"Based on your profile ({age}yo, {weight}kg), your stress load is {stress_pred}%. "
                        f"I'm keeping an eye on your {activity} activity level. Ask me about your sleep, screen time, or tips to improve!"
                    )
                
                return JsonResponse({"reply": response_text})
                
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": "grok-beta",
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_message}
                ]
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                ai_reply = result['choices'][0]['message']['content']
                return JsonResponse({"reply": ai_reply})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
            
    return render(request, 'core/chat.html')
