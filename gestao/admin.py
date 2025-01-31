
# Register your models here.
from django.contrib import admin
from .models import Empresa, Departamento, Cliente

admin.site.register(Empresa)
admin.site.register(Departamento)
admin.site.register(Cliente)