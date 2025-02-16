# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='cliente')
    

    def __str__(self):
        return self.username
