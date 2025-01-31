from django.urls import path
from . import views

urlpatterns = [
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('clientes/cadastrar/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('clientes/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/excluir/<int:id>/', views.excluir_cliente, name='excluir_cliente'),

    # Empresas
    path('empresas/', views.listar_empresas, name='listar_empresas'),
    path('empresas/cadastrar/', views.cadastrar_empresa, name='cadastrar_empresa'),
    path('editar/<int:id>/', views.editar_empresa, name='editar_empresa'),
    path('excluir/<int:id>/', views.excluir_empresa, name='excluir_empresa'),

    # Departamentos
    path('departamentos/', views.listar_departamentos, name='listar_departamentos'),
    path('departamentos/cadastrar/', views.cadastrar_departamentos, name='cadastrar_departamentos'),
    path('departamentos/editar/<int:id>/', views.editar_departamento, name='editar_departamento'),
    path('departamentos/excluir/<int:id>/', views.excluir_departamento, name='excluir_departamento'),


    #Admins
    path('adms/', views.listar_adms, name='listar_adms'),
    path('adms/cadastrar/', views.cadastrar_adm, name='cadastrar_adm'),
    path('adms/editar/<int:admin_id>/', views.editar_adm, name='editar_adm'),
    path('adms/excluir/<int:id>/', views.excluir_adm, name='excluir_adm'),
    
]
