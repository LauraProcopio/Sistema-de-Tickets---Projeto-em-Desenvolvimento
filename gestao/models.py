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


# Modelo para Cliente
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15)
    email = models.EmailField(max_length=100, unique=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome