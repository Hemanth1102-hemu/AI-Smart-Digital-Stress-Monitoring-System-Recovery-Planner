from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fitness/', views.fitness_input, name='fitness_input'),
    path('stress/', views.stress_input, name='stress_input'),
    path('result/', views.stress_result, name='stress_result'),
    path('recovery/', views.recovery_plan, name='recovery_plan'),
    path('chat/', views.chat_view, name='chat'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
]
