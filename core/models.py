from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    illness = models.TextField(null=True, blank=True)
    avg_sleep = models.FloatField(null=True, blank=True)
    avg_screen = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.nickname

class StressLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_recorded = models.DateTimeField(auto_now_add=True)
    sleep_time = models.FloatField(help_text="Hours of sleep")
    screen_time = models.FloatField(help_text="Hours of screen time")
    mood = models.CharField(max_length=50) # Pleasant, Neutral, Stressed
    concentration = models.CharField(max_length=50) # High, Medium, Low
    calculated_stress_percentage = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.date_recorded.strftime('%Y-%m-%d')} ({self.calculated_stress_percentage}%)"
