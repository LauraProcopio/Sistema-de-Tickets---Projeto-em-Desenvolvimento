# urls.py
from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Este é o admin padrão do Django

    # Página de Cadastro
    path('cadastro/', views.cadastro, name='cadastro'),

    # Página de Login
    path('login/', views.user_login, name='login'),

    # Página de Logout
    path('logout/', views.user_logout, name='logout'),

    path('dashboard_adm/', views.dashboard_adm, name='dashboard_adm'),
    path('dashboard_cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    path('gerar_relatorio_pdf/', views.gerar_relatorio_pdf, name='gerar_relatorio_pdf'),
    path('relatorio/excel/', views.gerar_relatorio_excel, name='gerar_relatorio_excel'),

    path('alterar-cadastro/', views.alterar_cadastro, name='alterar_cadastro'),
    path('alterar-cadastro-cliente/', views.alterar_cadastro_cliente, name='alterar_cadastro_cliente'),

]

