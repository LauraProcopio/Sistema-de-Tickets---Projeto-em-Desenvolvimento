from django.db import models

# Create your models here.
class Empresa(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome
    
# Modelo para Departamento
class Departamento(models.Model):
    nome = models.CharField(max_length=255)
    sigla = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.nome


