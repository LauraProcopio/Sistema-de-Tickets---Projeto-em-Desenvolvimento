from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar/', views.cadastrar_tickets, name='cadastrar_tickets'),  # Usado para ADM ou Cliente
    path('listar/', views.listar_tickets, name='listar_tickets'),
    path('listar-cliente/', views.listar_tickets, name='listar_tickets_cliente'),
    path('ticket/<int:ticket_id>/', views.detalhar_ticket, name='detalhar_ticket'),
    path('ticket/<int:ticket_id>/responder/', views.responder_ticket, name='responder_ticket'),
    path('ticket/<int:ticket_id>/atualizar/', views.atualizar_ticket, name='atualizar_ticket'),
    path('excluir/<int:id>/', views.excluir_ticket, name='excluir_ticket'),
    path('excluir_resposta/<int:resposta_id>/', views.excluir_resposta, name='excluir_resposta'),

]
