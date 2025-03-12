# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from gestao.models import Empresa, Departamento  # Importando as relações


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='cliente')
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)
    

    def __str__(self):
        return self.username
